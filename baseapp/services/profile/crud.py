import logging,uuid

from typing import Optional, Dict, Any
from pymongo import ASCENDING, DESCENDING, errors

from baseapp.config import setting, mongodb
from baseapp.services._enum import model

config = setting.get_settings()

class CRUD:
    def __init__(self):
        self.collection_user = "_user"
        self.collection_org = "_organization"
        self.logger = logging.getLogger()

    def find_user_by_id(self, user_id: str):
        """
        Retrieve a user by ID.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_user]
            try:
                get_user = collection.find_one({"_id": user_id},{"username":1,"email":1,"roles":1,"status":1,"org_id":1})
                get_user["id"] = get_user.pop("_id", None)
                if not get_user:
                    raise ValueError("User not found")
                return get_user
            except errors.PyMongoError as e:
                self.logger.exception(f"Error find user: {e._message}")
            except Exception as e:
                self.logger.exception(f"Unexpected error: {e}")
                raise
