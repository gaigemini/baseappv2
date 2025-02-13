import logging,json
from pymongo.errors import PyMongoError

from baseapp.config import setting, mongodb

config = setting.get_settings()

class CRUD:
    def __init__(self):
        self.logger = logging.getLogger()

    def create(self):
        """
        Create database and tables with schema.
        """
        try:
            with open(f"{config.file_location}initdata.json") as json_file:
                initData = json.load(json_file)            
                client = mongodb.MongoConn()
                with client as mongo_conn:
                    is_exists = mongo_conn.check_database_exists()
                    self.logger.debug(f"Database exist is {is_exists}")
                    if not is_exists:
                        mongo_conn.create_database(initData)
                    return is_exists
        except PyMongoError as pme:
            self.logger.error(f"Database error occurred: {str(pme)}")
            raise ValueError("Database error occurred while create database and tables.") from pme
        except Exception as e:
            self.logger.exception(f"Unexpected error occurred while creating document: {str(e)}")
            raise