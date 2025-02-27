import logging,json,uuid,traceback
from datetime import datetime,timezone
from pymongo.errors import DuplicateKeyError, PyMongoError
from typing import Optional, Dict, Any

from baseapp.config import setting, mongodb
from baseapp.services._org import model
from baseapp.model.common import Status
from baseapp.utils.utility import hash_password, get_enum
from baseapp.services.audit_trail_service import AuditTrailService

config = setting.get_settings()
logger = logging.getLogger()

class CRUD:
    def __init__(self):
        self.collection_org = "_organization"
        self.collection_user = "_user"
        self.collection_role = "_role"
        self.storage = 10737418240
        self.usedstorage = 0

    def set_context(self, user_id: str, org_id: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """
        Memperbarui konteks pengguna dan menginisialisasi AuditTrailService.
        """
        self.user_id = user_id
        self.org_id = org_id
        self.ip_address = ip_address
        self.user_agent = user_agent

        # Inisialisasi atau perbarui AuditTrailService dengan konteks terbaru
        self.audit_trail = AuditTrailService(
            user_id=self.user_id,
            org_id=self.org_id,
            ip_address=self.ip_address,
            user_agent=self.user_agent
        )

    def init_owner_org(self, org_data: model.Organization, user_data: model.User):
        """
        Insert a new owner into the collection.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            self.mongo = mongo

            collection = mongo._db[self.collection_org]
            collection_user = mongo._db[self.collection_user]

            org_data = org_data.model_dump()
            user_data = user_data.model_dump()

            org_data["_id"] = str(uuid.uuid4())
            org_data["rec_date"] = datetime.now(timezone.utc)
            org_data["storage"] = self.storage
            org_data["usedstorage"] = self.usedstorage
            try:
                # check owner is exist or not
                owner_is_exist = collection.find_one({"authority":1})
                if owner_is_exist:
                    raise ValueError("The owner already exists, and there is only one owner in the structure.")
                
                # check owner user is exist or not
                owner_user_is_exist = collection_user.find_one({"username":user_data["username"]})
                if owner_user_is_exist:
                    raise ValueError("The owner user already exists, please fill other username or email.")
                
                # insert owner data to the table
                result = collection.insert_one(org_data)
                logger.info(f"Owner created with id: {result.inserted_id}")

                # insert owner role data to the table
                obj_role = model.Role(name="Admin",org_id=result.inserted_id)
                init_role = self.init_role(org_data,role_data=obj_role)

                # insert user data to the table
                user_data["roles"] = [init_role["_id"]]
                init_user = self.init_user(org_data, user_data)
                return {"org":org_data,"user":init_user}
            except DuplicateKeyError:
                logger.error("Duplicate ID detected.")
                raise ValueError("the same ID already exists.")
            except PyMongoError as pme:
                logger.error(f"Database error occurred: {str(pme)}")
                raise ValueError("Database error occurred while init owner.") from pme
            except Exception as e:
                logger.exception(f"Unexpected error occurred while init owner: {e}")
                raise
    
    def init_partner_client_org(self, org_data: model.Organization, user_data: model.User):
        """
        Insert a new partner into the collection.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            self.mongo = mongo

            collection = mongo._db[self.collection_org]
            collection_user = mongo._db[self.collection_user]

            org_data = org_data.model_dump()
            user_data = user_data.model_dump()

            org_data["_id"] = str(uuid.uuid4())
            org_data["rec_by"] = self.user_id
            org_data["rec_date"] = datetime.now(timezone.utc)
            org_data["ref_id"] = self.org_id
            org_data["storage"] = self.storage
            org_data["usedstorage"] = self.usedstorage
            try:
                # check owner user is exist or not
                owner_user_is_exist = collection_user.find_one({"username":user_data["username"]})
                if owner_user_is_exist:
                    # write audit trail for fail
                    self.audit_trail.log_audittrail(
                        mongo,
                        action="init_partner_client",
                        target=self.collection_user,
                        target_id=None,
                        details={"username":user_data["username"]},
                        status="failure",
                        error_message="Role not found"
                    )
                    raise ValueError("The partner user already exists, please fill other username or email.")
                
                # insert owner data to the table
                result = collection.insert_one(org_data)
                logger.info(f"Partner created with id: {result.inserted_id}")

                # insert owner role data to the table
                obj_role = model.Role(name="Admin",org_id=result.inserted_id)
                init_role = self.init_role(org_data,role_data=obj_role)

                # insert user data to the table
                user_data["roles"] = [init_role["_id"]]
                init_user = self.init_user(org_data, user_data)
                return {"org":org_data,"user":init_user}
            except DuplicateKeyError:
                logger.error("Duplicate ID detected.")
                # write audit trail for fail
                self.audit_trail.log_audittrail(
                    mongo,
                    action="init_partner_client",
                    target=self.collection_org,
                    target_id=None,
                    details=org_data,
                    status="failure",
                    error_message="Duplicate ID"
                )
                raise ValueError("the same ID already exists.")
            except PyMongoError as pme:
                logger.error(f"Database error occurred: {str(pme)}")
                # write audit trail for fail
                self.audit_trail.log_audittrail(
                    mongo,
                    action="init_partner_client",
                    target=self.collection_org,
                    target_id=None,
                    details=org_data,
                    status="failure",
                    error_message=str(pme)
                )
                raise ValueError("Database error occurred while init partner.") from pme
            except Exception as e:
                logger.exception(f"Unexpected error occurred while init partner: {e}")
                raise

    def init_role(self, org_data, role_data:model.Role):
        """
        Insert a new role into the collection.
        """
        collection = self.mongo._db[self.collection_role]

        role_data = role_data.model_dump()

        role_data["_id"] = str(uuid.uuid4())
        role_data["rec_date"] = datetime.now(timezone.utc)
        role_data["mod_date"] = datetime.now(timezone.utc)
        role_data["org_id"] = org_data["_id"]

        try:
            result = collection.insert_one(role_data)
            logger.info(f"Role created with id: {result.inserted_id}")

            # trigger insert role on featuers
            self.init_role_in_feature(org_data,result.inserted_id)

            return role_data
        except PyMongoError as pme:
            logger.error(f"Database error occurred while init role of owner: {str(pme)}")
            # write audit trail for fail
            self.audit_trail.log_audittrail(
                self.mongo,
                action="init_partner_client:role",
                target=self.collection_role,
                target_id=None,
                details=role_data,
                status="failure",
                error_message=str(pme)
            )
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occurred while init owner: {e}")
            raise

    def init_role_in_feature(self, org_data, role_id):
        """
        Generate role in feature into the collection.
        """
        collection = self.mongo._db["_featureonrole"]
        collection_features = self.mongo._db["_feature"]
        initial_data = []
        try:
            # get enum bit of roleaction
            bitRA = get_enum(self.mongo,"ROLEACTION")
            totalBitRA = sum(bitRA["value"].values())

            # list of features
            filters = {
                "authority": { "$bitsAnySet": org_data["authority"] }
            }
            get_features = collection_features.find(filters)
            for feature in get_features:
                initial_data.append({
                    "_id":str(uuid.uuid4()),
                    "org_id": org_data["_id"],
                    "r_id": role_id,
                    "f_id": feature["_id"],
                    "permission": totalBitRA-feature["negasiperm"][str(org_data['authority'])]
                })
            collection.insert_many(initial_data, ordered=False)
            logger.info(f"Inserted {len(initial_data)} documents into _featureonrole")
            
            return initial_data
        except PyMongoError as pme:
            logger.error(f"Database error occurred while init role feature of owner.: {str(pme)}")
            # write audit trail for fail
            self.audit_trail.log_audittrail(
                self.mongo,
                action="init_partner_client:_featureonrole",
                target="_featureonrole",
                target_id=None,
                details=initial_data,
                status="failure",
                error_message=str(pme)
            )
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occurred while init owner: {e}")
            raise

    def init_user(self, org_data, user_data):
        """
        Insert a new user into the collection.
        """
        collection = self.mongo._db[self.collection_user]

        user_data["_id"] = str(uuid.uuid4())
        user_data["rec_date"] = datetime.now(timezone.utc)
        user_data["mod_date"] = datetime.now(timezone.utc)
        user_data["org_id"] = org_data["_id"]

        # Generate salt and hash password
        salt, hashed_password = hash_password(user_data["password"])
        user_data["salt"] = salt
        user_data["password"] = hashed_password

        try:
            result = collection.insert_one(user_data)
            logger.info(f"User created with id: {result.inserted_id}")
            return user_data
        except PyMongoError as pme:
            logger.error(f"Database error occurred while init user.: {str(pme)}")
            # write audit trail for fail
            self.audit_trail.log_audittrail(
                self.mongo,
                action="init_partner_client:_user",
                target="_featureonrole",
                target_id=None,
                details=user_data,
                status="failure",
                error_message=str(pme)
            )
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occurred while init user: {e}")
            raise

    def get_by_id(self, org_id: str):
        """
        Retrieve a organization by ID.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_org]
            try:
                data = collection.find_one({"_id": org_id})
                if not data:
                    # write audit trail for fail
                    self.audit_trail.log_audittrail(
                        mongo,
                        action="retrieve",
                        target=self.collection_org,
                        target_id=org_id,
                        details={"_id": org_id},
                        status="failure",
                        error_message="Organization not found"
                    )
                    raise ValueError("Organization not found")
                # write audit trail for success
                self.audit_trail.log_audittrail(
                    mongo,
                    action="retrieve",
                    target=self.collection_org,
                    target_id=org_id,
                    details={"_id": org_id, "retrieved": data},
                    status="success"
                )
                return data
            except PyMongoError as pme:
                self.logger.error(f"Database error occurred: {str(pme)}")
                # write audit trail for fail
                self.audit_trail.log_audittrail(
                    mongo,
                    action="retrieve",
                    target=self.collection_org,
                    target_id=org_id,
                    details={"_id": org_id},
                    status="failure",
                    error_message=str(pme)
                )
                raise ValueError("Database error occurred while find document.") from pme
            except Exception as e:
                self.logger.exception(f"Unexpected error occurred while finding document: {str(e)}")
                raise

    def update_by_id(self, org_id: str, data: model.OrganizationUpdate):
        """
        Update a organization's data by ID.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_org]
            obj = data.model_dump()
            obj["mod_by"] = self.user_id
            obj["mod_date"] = datetime.now(timezone.utc)
            try:
                update_data = collection.find_one_and_update({"_id": org_id}, {"$set": obj}, return_document=True)
                if not update_data:
                    # write audit trail for fail
                    self.audit_trail.log_audittrail(
                        mongo,
                        action="update",
                        target=self.collection_org,
                        target_id=org_id,
                        details={"$set": obj},
                        status="failure",
                        error_message="Organization not found"
                    )
                    raise ValueError("Organization not found")
                # write audit trail for success
                self.audit_trail.log_audittrail(
                    mongo,
                    action="update",
                    target=self.collection_org,
                    target_id=org_id,
                    details={"$set": obj},
                    status="success"
                )
                return update_data
            except PyMongoError as pme:
                self.logger.error(f"Database error occurred: {str(pme)}")
                # write audit trail for fail
                self.audit_trail.log_audittrail(
                    mongo,
                    action="update",
                    target=self.collection_org,
                    target_id=org_id,
                    details={"$set": obj},
                    status="failure",
                    error_message=str(pme)
                )
                raise ValueError("Database error occurred while update document.") from pme
            except Exception as e:
                self.logger.exception(f"Error updating role: {str(e)}")
                raise
