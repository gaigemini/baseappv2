import logging,uuid
from hmac import compare_digest
from pymongo.errors import PyMongoError, DuplicateKeyError
from typing import Optional, Dict, Any
from pymongo import ASCENDING, DESCENDING
from datetime import datetime, timezone

from baseapp.model.common import Status, OTP_BASE_KEY
from baseapp.config import setting, mongodb
from baseapp.services._user.model import User, UpdateUsername, UpdateEmail, UpdateStatus, UpdateRoles, UpdateByAdmin, ChangePassword

from baseapp.services.audit_trail_service import AuditTrailService

from baseapp.utils.utility import hash_password, is_none, generate_password

config = setting.get_settings()

class CRUD:
    def __init__(self, collection_name="_user"):
        self.collection_name = collection_name
        self.logger = logging.getLogger()

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

    def create(self, data: User):
        """
        Insert a new user into the collection.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_name]

            obj = data.model_dump()
            obj["_id"] = str(uuid.uuid4())
            obj["rec_by"] = self.user_id
            obj["rec_date"] = datetime.now(timezone.utc)
            obj["org_id"] = self.org_id

            # Generate salt and hash password
            salt, hashed_password = hash_password(data.password)
            obj["salt"] = salt
            obj["password"] = hashed_password
            try:
                result = collection.insert_one(obj)
                del obj["salt"]
                del obj["password"]
                return obj
            except DuplicateKeyError as dke:
                self.logger.error(f"Duplicate entry detected: {str(dke)}")
                raise ValueError("A document with the same ID already exists.") from dke
            except PyMongoError as pme:
                self.logger.error(f"Database error occurred: {str(pme)}")
                raise ValueError("Database error occurred while creating document.") from pme
            except Exception as e:
                self.logger.exception(f"Unexpected error occurred while creating document: {str(e)}")
                raise

    def get_by_id(self, user_id: str):
        """
        Retrieve a user by ID.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_name]
            try:
                # Selected field
                selected_fields={
                    "id": "$_id",
                    "username":1,
                    "email":1,
                    "roles":1,
                    "status":1,
                    "org_id":1,
                    "_id": 0
                }
                user = collection.find_one({"_id": user_id},selected_fields)
                if not user:
                    # write audit trail for fail
                    self.audit_trail.log_audittrail(
                        mongo,
                        action="retrieve",
                        target=self.collection_name,
                        target_id=user_id,
                        details={"_id": user_id},
                        status="failure",
                        error_message="User not found"
                    )
                    raise ValueError("User not found")
                # write audit trail for success
                self.audit_trail.log_audittrail(
                    mongo,
                    action="retrieve",
                    target=self.collection_name,
                    target_id=user_id,
                    details={"_id": user_id, "retrieved_user": user},
                    status="success"
                )
                return user
            except PyMongoError as pme:
                self.logger.error(f"Database error occurred: {str(pme)}")
                # write audit trail for fail
                self.audit_trail.log_audittrail(
                    mongo,
                    action="retrieve",
                    target=self.collection_name,
                    target_id=user_id,
                    details={"_id": user_id},
                    status="failure",
                    error_message=str(pme)
                )
                raise ValueError("Database error occurred while find document.") from pme
            except Exception as e:
                self.logger.exception(f"Unexpected error occurred while finding document: {str(e)}")
                raise

    def update_all_by_admin(self, user_id: str, data: UpdateByAdmin):
        """
        Update a user's data [username,email,roles,status] by ID.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_name]
            obj = data.model_dump()
            obj["mod_by"] = self.user_id
            obj["mod_date"] = datetime.now(timezone.utc)
            self.logger.debug(f"update data user: {obj}")
            try:
                update_user = collection.find_one_and_update({"_id": user_id}, {"$set": obj}, return_document=True)
                if not update_user:
                    # write audit trail for fail
                    self.audit_trail.log_audittrail(
                        mongo,
                        action="update",
                        target=self.collection_name,
                        target_id=user_id,
                        details={"$set": obj},
                        status="failure",
                        error_message="User not found"
                    )
                    raise ValueError("User not found")
                # write audit trail for success
                self.audit_trail.log_audittrail(
                    mongo,
                    action="update",
                    target=self.collection_name,
                    target_id=user_id,
                    details={"$set": obj},
                    status="success"
                )
                return update_user
            except PyMongoError as pme:
                self.logger.error(f"Database error occurred: {str(pme)}")
                # write audit trail for fail
                self.audit_trail.log_audittrail(
                    mongo,
                    action="update",
                    target=self.collection_name,
                    target_id=user_id,
                    details={"$set": obj},
                    status="failure",
                    error_message=str(pme)
                )
                raise ValueError("Database error occurred while update document.") from pme
            except Exception as e:
                self.logger.exception(f"Error updating username: {str(e)}")
                raise

    def update_username(self, user_id: str, data: UpdateUsername):
        """
        Update a user's data [username] by ID.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_name]
            obj = data.model_dump()
            obj["mod_by"] = self.user_id
            obj["mod_date"] = datetime.now(timezone.utc)
            try:
                update_user = collection.find_one_and_update({"_id": user_id}, {"$set": obj}, return_document=True)
                if not update_user:
                    # write audit trail for fail
                    self.audit_trail.log_audittrail(
                        mongo,
                        action="update",
                        target=self.collection_name,
                        target_id=user_id,
                        details={"$set": obj},
                        status="failure",
                        error_message="User not found"
                    )
                    raise ValueError("User not found")
                # write audit trail for success
                self.audit_trail.log_audittrail(
                    mongo,
                    action="update",
                    target=self.collection_name,
                    target_id=user_id,
                    details={"$set": obj},
                    status="success"
                )
                return update_user
            except PyMongoError as pme:
                self.logger.error(f"Database error occurred: {str(pme)}")
                # write audit trail for fail
                self.audit_trail.log_audittrail(
                    mongo,
                    action="update",
                    target=self.collection_name,
                    target_id=user_id,
                    details={"$set": obj},
                    status="failure",
                    error_message=str(pme)
                )
                raise ValueError("Database error occurred while update document.") from pme
            except Exception as e:
                self.logger.exception(f"Error updating username: {str(e)}")
                raise
    
    def update_email(self, user_id: str, data: UpdateEmail):
        """
        Update a user's data [email] by ID.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_name]
            obj = data.model_dump()
            obj["mod_by"] = self.user_id
            obj["mod_date"] = datetime.now(timezone.utc)
            try:
                update_user = collection.find_one_and_update({"_id": user_id}, {"$set": obj}, return_document=True)
                if not update_user:
                    # write audit trail for fail
                    self.audit_trail.log_audittrail(
                        mongo,
                        action="update",
                        target=self.collection_name,
                        target_id=user_id,
                        details={"$set": obj},
                        status="failure",
                        error_message="User not found"
                    )
                    raise ValueError("User not found")
                # write audit trail for success
                self.audit_trail.log_audittrail(
                    mongo,
                    action="update",
                    target=self.collection_name,
                    target_id=user_id,
                    details={"$set": obj},
                    status="success"
                )
                return update_user
            except PyMongoError as pme:
                self.logger.error(f"Database error occurred: {str(pme)}")
                # write audit trail for fail
                self.audit_trail.log_audittrail(
                    mongo,
                    action="update",
                    target=self.collection_name,
                    target_id=user_id,
                    details={"$set": obj},
                    status="failure",
                    error_message=str(pme)
                )
                raise ValueError("Database error occurred while update document.") from pme
            except Exception as e:
                self.logger.exception(f"Error updating email: {str(e)}")
                raise
    
    def update_role(self, user_id: str, data: UpdateRoles):
        """
        Update a user's data [roles] by ID.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_name]
            obj = data.model_dump()
            obj["mod_by"] = self.user_id
            obj["mod_date"] = datetime.now(timezone.utc)
            try:
                update_user = collection.find_one_and_update({"_id": user_id}, {"$set": obj}, return_document=True)
                if not update_user:
                    # write audit trail for fail
                    self.audit_trail.log_audittrail(
                        mongo,
                        action="update",
                        target=self.collection_name,
                        target_id=user_id,
                        details={"$set": obj},
                        status="failure",
                        error_message="User not found"
                    )
                    raise ValueError("User not found")
                self.logger.info(f"User {user_id} updated successfully.")
                # write audit trail for success
                self.audit_trail.log_audittrail(
                    mongo,
                    action="update",
                    target=self.collection_name,
                    target_id=user_id,
                    details={"$set": obj},
                    status="success"
                )
                return update_user
            except PyMongoError as pme:
                self.logger.error(f"Database error occurred: {str(pme)}")
                # write audit trail for fail
                self.audit_trail.log_audittrail(
                    mongo,
                    action="update",
                    target=self.collection_name,
                    target_id=user_id,
                    details={"$set": obj},
                    status="failure",
                    error_message=str(pme)
                )
                raise ValueError("Database error occurred while update document.") from pme
            except Exception as e:
                self.logger.exception(f"Error updating roles: {str(e)}")
                raise
    
    def update_status(self, user_id: str, data: UpdateStatus):
        """
        Update a user's data [status] by ID.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_name]
            obj = data.model_dump()
            obj["mod_by"] = self.user_id
            obj["mod_date"] = datetime.now(timezone.utc)
            try:
                update_user = collection.find_one_and_update({"_id": user_id}, {"$set": obj}, return_document=True)
                if not update_user:
                    # write audit trail for fail
                    self.audit_trail.log_audittrail(
                        mongo,
                        action="update",
                        target=self.collection_name,
                        target_id=user_id,
                        details={"$set": obj},
                        status="failure",
                        error_message="User not found"
                    )
                    raise ValueError("User not found")
                self.logger.info(f"User {user_id} updated successfully.")
                # write audit trail for success
                self.audit_trail.log_audittrail(
                    mongo,
                    action="update",
                    target=self.collection_name,
                    target_id=user_id,
                    details={"$set": obj},
                    status="success"
                )
                return update_user
            except PyMongoError as pme:
                self.logger.error(f"Database error occurred: {str(pme)}")
                # write audit trail for fail
                self.audit_trail.log_audittrail(
                    mongo,
                    action="update",
                    target=self.collection_name,
                    target_id=user_id,
                    details={"$set": obj},
                    status="failure",
                    error_message=str(pme)
                )
                raise ValueError("Database error occurred while update document.") from pme
            except Exception as e:
                self.logger.exception(f"Error updating status: {str(e)}")
                raise
    
    def _validate_user(self,mongo,old_password):
        collection = mongo._db[self.collection_name]
        query = {"_id": self.user_id}
        user_info = collection.find_one(query)
        if not user_info:
            self.logger.warning(f"User with ID'{self.user_id}' not found.")
            raise ValueError("User not found")

        if user_info.get("status") != Status.ACTIVE.value:
            self.logger.warning(f"User {user_info.get('username')} is not active.")
            raise ValueError("User is not active.")
        
        usalt = user_info.get("salt")
        current_password = user_info.get("password")
        if not current_password:
            self.logger.error(f"Password missing for user {user_info.get('username')}.")
            raise ValueError("User data is invalid.")

        salt, verify_password = hash_password(old_password, usalt)

        if not compare_digest(current_password, verify_password):
            self.logger.warning(f"User {user_info.get('username')} provided invalid password.")
            raise ValueError("Invalid old password.")
        
        return user_info
    
    def change_password(self, data: ChangePassword):
        """
        Change password
        """
        if data.new_password != data.verify_password:
            raise ValueError("New password is not match with verify password.")
        
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_name]
            try:
                user_info = self._validate_user(mongo,data.old_password)

                password = is_none(data.new_password, generate_password())
                salt, hashed_password = hash_password(password)

                obj = {}
                obj["password"] = hashed_password
                obj["salt"] = salt
                obj["mod_by"] = self.user_id
                obj["mod_date"] = datetime.now(timezone.utc)

                update_user = collection.find_one_and_update({"_id": self.user_id}, {"$set": obj}, return_document=True)
                if not update_user:
                    # write audit trail for fail
                    self.audit_trail.log_audittrail(
                        mongo,
                        action="change_password",
                        target=self.collection_name,
                        target_id=self.user_id,
                        status="failure",
                        error_message="Change password failed"
                    )
                    raise ValueError("Change password failed")
                # write audit trail for success
                self.audit_trail.log_audittrail(
                    mongo,
                    action="change_password",
                    target=self.collection_name,
                    target_id=self.user_id,
                    status="success"
                )
                return {"id":update_user["_id"],"username":update_user["username"],"email":update_user["email"]}
            except PyMongoError as pme:
                self.logger.error(f"Database error occurred: {str(pme)}")
                # write audit trail for fail
                self.audit_trail.log_audittrail(
                    mongo,
                    action="change_password",
                    target=self.collection_name,
                    target_id=self.user_id,
                    status="failure",
                    error_message=str(pme)
                )
                raise ValueError("Database error occurred while update document.") from pme
            except Exception as e:
                self.logger.exception(f"Error updating status: {str(e)}")
                raise

    def reset_password(self, user_id:str , data: ChangePassword):
        """
        Reset password
        """
        if data.new_password != data.verify_password:
            raise ValueError("New password is not match with verify password.")
        
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_name]
            try:
                password = is_none(data.new_password, generate_password())
                salt, hashed_password = hash_password(password)

                obj = {}
                obj["password"] = hashed_password
                obj["salt"] = salt
                obj["mod_by"] = self.user_id
                obj["mod_date"] = datetime.now(timezone.utc)

                update_user = collection.find_one_and_update({"_id": user_id}, {"$set": obj}, return_document=True)
                if not update_user:
                    # write audit trail for fail
                    self.audit_trail.log_audittrail(
                        mongo,
                        action="reset_password",
                        target=self.collection_name,
                        target_id=user_id,
                        status="failure",
                        error_message="Reset password failed"
                    )
                    raise ValueError("Reset password failed")
                # write audit trail for success
                self.audit_trail.log_audittrail(
                    mongo,
                    action="reset_password",
                    target=self.collection_name,
                    target_id=self.user_id,
                    status="success"
                )
                return {"id":update_user["_id"],"username":update_user["username"],"email":update_user["email"]}
            except PyMongoError as pme:
                self.logger.error(f"Database error occurred: {str(pme)}")
                # write audit trail for fail
                self.audit_trail.log_audittrail(
                    mongo,
                    action="reset_password",
                    target=self.collection_name,
                    target_id=self.user_id,
                    status="failure",
                    error_message={str(pme)}
                )
                raise ValueError("Database error occurred while update document.") from pme
            except Exception as e:
                self.logger.exception(f"Error updating status: {str(e)}")
                raise
            
    def get_all(self, filters: Optional[Dict[str, Any]] = None, page: int = 1, per_page: int = 10, sort_field: str = "_id", sort_order: str = "asc"):
        """
        Retrieve all documents from the collection with optional filters, pagination, and sorting.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_name]
            try:
                # Apply filters
                query_filter = filters or {}

                # Pagination
                skip = (page - 1) * per_page
                limit = per_page

                # Sorting
                order = ASCENDING if sort_order == "asc" else DESCENDING

                # Selected field
                selected_fields={
                    "id": "$_id",
                    "username":1,
                    "email":1,
                    "roles":1,
                    "status":1,
                    "org_id":1,
                    "_id": 0
                }

                # Aggregation pipeline
                pipeline = [
                    {"$match": query_filter},  # Filter stage
                    {"$sort": {sort_field: order}},  # Sorting stage
                    {"$skip": skip},  # Pagination skip stage
                    {"$limit": limit},  # Pagination limit stage
                    {"$project": selected_fields}  # Project only selected fields
                ]

                # Execute aggregation pipeline
                cursor = collection.aggregate(pipeline)
                results = list(cursor)

                # Total count
                total_count = collection.count_documents(query_filter)

                # write audit trail for success
                self.audit_trail.log_audittrail(
                    mongo,
                    action="retrieve",
                    target=self.collection_name,
                    target_id="agregate",
                    details={"aggregate": pipeline},
                    status="success"
                )

                return {
                    "data": results,
                    "pagination": {
                        "current_page": page,
                        "items_per_page": per_page,
                        "total_items": total_count,
                        "total_pages": (total_count + per_page - 1) // per_page,  # Ceiling division
                    },
                }
            except PyMongoError as pme:
                self.logger.error(f"Error retrieving user with filters and pagination: {str(e)}")
                # write audit trail for success
                self.audit_trail.log_audittrail(
                    mongo,
                    action="retrieve",
                    target=self.collection_name,
                    target_id="agregate",
                    details={"aggregate": pipeline},
                    status="failure"
                )
                raise ValueError("Database error while retrieve document") from pme
            except Exception as e:
                self.logger.exception(f"Unexpected error during deletion: {str(e)}")
                raise