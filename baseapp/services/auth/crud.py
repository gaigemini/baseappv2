import logging
from hmac import compare_digest
from baseapp.config import setting, mongodb
from baseapp.services.auth.model import UserInfo
from baseapp.model.common import Status
from baseapp.utils.utility import hash_password

config = setting.get_settings()
logger = logging.getLogger()

class CRUD:
    def __init__(self):
        self.user_collection = "_user"
        self.org_collection = "_organization"
        self.mongo = None

    def check_org(self, org_id) -> int:
        collection = self.mongo._db[self.org_collection]
        query = {"_id": org_id}
        find_org = collection.find_one(query)
        if not find_org:
            logger.warning(f"Organization with ID {org_id} not found.")
            raise ValueError("Organization not found")
        return find_org.get("authority")

    def validate_password(self, user_info, password: str) -> UserInfo:
        if user_info.get("status") != Status.ACTIVE.value:
            logger.warning(f"User {user_info.get('username')} is not active.")
            raise ValueError("User is not active.")
        
        usalt = user_info.get("salt")
        if not usalt:
            logger.error(f"Salt missing for user {user_info.get('username')}.")
            raise ValueError("User data is invalid.")

        hashed_password = user_info.get("password")
        if not hashed_password:
            logger.error(f"Password missing for user {user_info.get('username')}.")
            raise ValueError("User data is invalid.")

        salt, claim_password = hash_password(password, usalt.encode("utf-8"))

        if not compare_digest(claim_password, hashed_password):
            logger.warning(f"User {user_info.get('username')} provided invalid password.")
            raise ValueError("Invalid password.")
        
        return UserInfo(
            id=user_info["_id"], 
            org_id=user_info["org_id"], 
            roles=user_info["roles"], 
            authority=user_info["authority"]
        )

    def find_user(self, username: str) -> dict:
        collection = self.mongo._db[self.user_collection]
        query = {"$or": [{"username": username}, {"email": username}]}
        user_info = collection.find_one(query)
        if not user_info:
            logger.warning(f"User with username or email '{username}' not found.")
            raise ValueError("User not found")
        return user_info
    
    def validate_user(self, username, password) -> UserInfo:
        client = mongodb.MongoConn()
        with client as mongo:
            self.mongo = mongo
            user_info = self.find_user(username)
            authority = self.check_org(user_info["org_id"])

            user_data = {
                key: user_info.get(key, None)
                for key in ["_id", "username", "org_id", "password", "salt", "roles", "status"]
            }
            user_data["authority"] = authority

            return self.validate_password(user_data, password)
    
    def is_valid_user(self, username: str) -> bool:
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.user_collection]
            query = {"$or": [{"username": username}, {"email": username}]}
            user_info = collection.find_one(query)
            if not user_info:
                logger.warning(f"User with username or email '{username}' not found.")
                return False
            if user_info.get("status") != Status.ACTIVE.value:
                logger.warning(f"User {user_info.get('username')} is not active.")
                return False
            return True