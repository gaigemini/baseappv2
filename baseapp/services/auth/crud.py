import logging, bcrypt
from baseapp.config import setting, mongodb
from baseapp.services.auth.model import UserInfo, ClientInfo
from baseapp.model.common import Status
from baseapp.utils.utility import get_enum

config = setting.get_settings()
logger = logging.getLogger()

class CRUD:
    def __init__(self):
        self.user_collection = "_user"
        self.org_collection = "_organization"
        self.permissions_collection = "_featureonrole"
        self.api_credentials = "_api_credentials"

        self.mongo = mongodb.MongoConn()  # Inisialisasi MongoDB di sini

    def __enter__(self):
        # Membuka koneksi saat memasuki konteks
        self.mongo.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Menutup koneksi saat keluar dari konteks
        self.mongo.__exit__(exc_type, exc_value, traceback)

    def check_org(self, org_id) -> int:
        collection = self.mongo._db[self.org_collection]
        query = {"_id": org_id}
        find_org = collection.find_one(query)
        if not find_org:
            logger.warning(f"Organization with ID {org_id} not found.")
            raise ValueError("Organization not found")
        return find_org.get("authority")

    def get_role_action(self):
        bitRA = get_enum(self.mongo,"ROLEACTION")
        bitRA = bitRA["value"]
        return bitRA
    
    def get_feature(self, roles):
        _featureDict = {}
        collection = self.mongo._db[self.permissions_collection]
        query = {"r_id": {"$in": roles}}
        find_role = collection.find(query)
        for i in find_role:
            if i['f_id'] not in _featureDict:
                _featureDict[i['f_id']] = i['permission']
            else:
                _featureDict[i['f_id']] = i['permission'] | _featureDict[i['f_id']]
        return _featureDict
    
    def validate_password(self, user_info, password: str) -> UserInfo:
        if user_info.get("status") != Status.ACTIVE.value:
            logger.warning(f"User {user_info.get('username')} is not active.")
            raise ValueError("User is not active.")

        hashed_password = user_info.get("password")
        if not hashed_password:
            logger.error(f"Password missing for user {user_info.get('username')}.")
            raise ValueError("User data is invalid.")

        claim_password = password.encode('utf-8')

        if not bcrypt.checkpw(claim_password, hashed_password):
            logger.warning(f"User {user_info.get('username')} provided invalid password.")
            raise ValueError("Invalid password.")
        
        return UserInfo(
            id=user_info["_id"], 
            org_id=user_info["org_id"], 
            roles=user_info["roles"], 
            authority=user_info["authority"],
            bitws=user_info["bitws"],
            feature=user_info["feature"]
        )

    def find_user(self, username: str) -> dict:
        collection = self.mongo._db[self.user_collection]
        query = {"$or": [{"username": username}, {"email": username}]}
        user_info = collection.find_one(query)
        if not user_info:
            logger.warning(f"User with username or email '{username}' not found.")
            raise ValueError("User not found")
        user_info["bitws"]=self.get_role_action()
        user_info["feature"]=self.get_feature(user_info["roles"])
        return user_info

    def validate_user(self, username, password=None) -> UserInfo:
        user_info = self.find_user(username)
        authority = self.check_org(user_info["org_id"])

        user_data = {
            key: user_info.get(key, None)
            for key in ["_id", "username", "org_id", "password", "roles", "status", "bitws", "feature"]
        }
        user_data["authority"] = authority
        if password is None:
            return UserInfo(
                id=user_data["_id"], 
                org_id=user_data["org_id"], 
                roles=user_data["roles"], 
                authority=user_data["authority"],
                bitws=user_data["bitws"],
                feature=user_data["feature"]
            )
        else:
            return self.validate_password(user_data, password)
        
    def find_client_id(self, client_id: str) -> dict:
        collection = self.mongo._db[self.api_credentials]
        query = {"client_id": client_id}
        client_info = collection.find_one(query)
        if not client_info:
            logger.warning(f"Client with ID '{client_id}' not found.")
            raise ValueError("Client not found")
        return client_info
    
    def validate_client(self, client_id, client_secret) -> ClientInfo:
        client_info = self.find_client_id(client_id)

        client_data = {
            key: client_info.get(key, None)
            for key in ["_id", "org_id", "client_id", "client_secret_hash"]
        }

        if client_info.get("status") != Status.ACTIVE.value:
            logger.warning(f"Client {client_id} is not active.")
            raise ValueError("Client is not active.")

        client_secret_hash = client_info.get("client_secret_hash")
        claim_client_secret = client_secret.encode('utf-8')

        if not bcrypt.checkpw(claim_client_secret, client_secret_hash):
            logger.warning(f"Client {client_id} provided invalid secret.")
            raise ValueError("Invalid client secret.")
        
        return ClientInfo(
            id=client_data["_id"], 
            org_id=client_data["org_id"], 
            client_id=client_data["client_id"]
        )