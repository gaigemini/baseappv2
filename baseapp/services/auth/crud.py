import logging

from baseapp.config import setting, mongodb
from baseapp.services.auth import model
from baseapp.model.common import Status
from baseapp.utils.utility import hash_password

config = setting.get_settings()
logger = logging.getLogger()

class CRUD:
    def __init__(self):
        self.user_collection = "_user"
        self.org_collection = "_organization"

    def check_org(self,org_id):
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.org_collection]
            try:
                query = {"_id": org_id}
                find_org = collection.find_one(query)
                if not find_org:
                    return model.UserInfo(res_code=4, res_message="Organization not found")
                return find_org["authority"]
            except Exception as e:
                logger.exception("Error find organization.")
                return model.UserInfo(res_code=4, res_message=str(e))

    def validate_password(self, user_info, password: str) -> model.UserInfo:
        logger.debug(f"user_info: {user_info}")
        if user_info["status"] != Status.ACTIVE.value:
            return model.UserInfo(res_code=4, res_message=f"{user_info['id']} is not active user.")
        
        usalt = user_info["salt"]
        salt, claim_password = hash_password(password, usalt.encode('utf-8'))
        if (claim_password == user_info["password"]):
            return model.UserInfo(res_code=0, id=user_info["id"], org_id=user_info["org_id"], roles=user_info["roles"], authority=user_info["authority"])

        return model.UserInfo(res_code=4, res_message="Invalid password.")

    def validate_user(self, username, password) -> model.UserInfo:
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.user_collection]
            try:
                query = {
                    "$or": [
                        {"username": username},
                        {"email": username}
                    ]
                }
                user_info = collection.find_one(query)

                if not user_info:
                    return model.UserInfo(res_code=4, res_message="User not found")
                                
                authority = self.check_org(user_info["org_id"])

                user_data = {}
                user_data["id"] = user_info["_id"]
                user_data["org_id"] = user_info["org_id"]
                user_data["password"] = user_info["password"]
                user_data["salt"] = user_info["salt"]
                user_data["roles"] = user_info["roles"]
                user_data["status"] = user_info["status"]
                user_data["authority"] = authority

                logger.debug(f"User data: {user_data}")
                
                return self.validate_password(user_data,password)
            except Exception as e:
                logger.exception("Error find user.")
                return model.UserInfo(res_code=4, res_message=str(e))
