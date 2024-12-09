import logging,json,uuid,traceback

from datetime import datetime,timezone

from pymongo.errors import DuplicateKeyError

from baseapp.config import setting, mongodb
from baseapp.services._org import model
from baseapp.model.common import Status
from baseapp.utils.utility import hash_password, get_enum

config = setting.get_settings()
logger = logging.getLogger()

class CRUD:
    def __init__(self, collection_name="_organization"):
        self.collection_name = collection_name

    def init_owner_org(self, org_data: model.Organization, user_data: model.User):
        """
        Insert a new owner into the collection.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            self.mongo = mongo

            collection = mongo._db[self.collection_name]
            collection_user = mongo._db["_user"]

            org_data = org_data.model_dump()
            user_data = user_data.model_dump()

            org_data["_id"] = str(uuid.uuid4())
            org_data["rec_date"] = datetime.now(timezone.utc)
            org_data["mod_date"] = datetime.now(timezone.utc)
            try:
                # check owner is exist or not
                owner_is_exist = collection.find_one({"authority":1})
                if owner_is_exist:
                    return {"status": 4, "message": "The owner already exists, and there is only one owner in the structure."}
                
                # check owner user is exist or not
                owner_user_is_exist = collection_user.find_one({"username":user_data["username"]})
                if owner_user_is_exist:
                    return {"status": 4, "message": "The owner user already exists, please fill other username or email."}
                
                # insert owner data to the table
                result = collection.insert_one(org_data)
                logger.info(f"Owner created with id: {result.inserted_id}")

                # insert owner role data to the table
                obj_role = model.Role(name="Admin",org_id=result.inserted_id)
                init_role = self.init_role(org_data,role_data=obj_role)

                # insert user data to the table
                user_data["roles"] = init_role["data"]["_id"]
                init_user = self.init_user(org_data, user_data)
                return {"status": 0, "data": {"org":org_data,"user":init_user["data"]}}
            except DuplicateKeyError:
                logger.error("Duplicate ID detected.")
                return {"status": 4, "message": "the same ID already exists."}
            except Exception as e:
                logger.exception("Error creating owner.")
                return {"status": 4, "message": str(e)}
            
    def init_role(self, org_data, role_data:model.Role):
        """
        Insert a new role into the collection.
        """
        collection = self.mongo._db["_role"]

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

            return {"status": 0, "data": role_data}
        except DuplicateKeyError:
            logger.error("Duplicate Role ID detected.")
            return {"status": 4, "message": "Role with the same ID already exists."}
        except Exception as e:
            logger.exception("Error creating role.")
            return {"status": 4, "message": str(e)}

    def init_role_in_feature(self, org_data, role_id):
        """
        Generate role in feature into the collection.
        """
        collection = self.mongo._db["_featureonrole"]
        collection_features = self.mongo._db["_feature"]

        try:
            # get enum bit of roleaction
            bitRA = get_enum("ROLEACTION")
            totalBitRA = sum(bitRA["value"].values())

            # list of features
            filters = {
                "authority": { "$bitsAnySet": org_data["authority"] }
            }
            get_features = collection_features.find(filters)
            initial_data = []
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
            
            return {"status": 0, "data": initial_data}
        except DuplicateKeyError:
            logger.error("Duplicate User ID detected.")
            return {"status": 4, "message": "Role with the same ID already exists."}
        except Exception as e:
            logger.exception("Error creating role.")
            return {"status": 4, "message": str(e)}

    def init_user(self, org_data, user_data):
        """
        Insert a new user into the collection.
        """
        collection = self.mongo._db["_user"]

        user_data["_id"] = str(uuid.uuid4())
        user_data["rec_date"] = datetime.now(timezone.utc)
        user_data["mod_date"] = datetime.now(timezone.utc)
        user_data["org_id"] = org_data["_id"]

        # Generate salt and hash password
        salt, hashed_password = hash_password(user_data["password"])
        user_data["salt"] = salt.decode('utf-8')
        user_data["password"] = hashed_password

        try:
            result = collection.insert_one(user_data)
            logger.info(f"User created with id: {result.inserted_id}")
            return {"status": 0, "data": user_data}
        except DuplicateKeyError:
            logger.error("Duplicate User ID detected.")
            return {"status": 4, "message": "User with the same ID already exists."}
        except Exception as e:
            logger.exception("Error creating User.")
            return {"status": 4, "message": str(e)}
