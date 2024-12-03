import logging,json
import traceback
from baseapp.config import setting, mongodb

config = setting.get_settings()
logger = logging.getLogger()

def init_database():
    try:
        with open(f"{config.file_location}initdata.json") as json_file:
            initData = json.load(json_file)            
            client = mongodb.MongoConn()
            with client as mongo_conn:
                is_exists = mongo_conn.check_database_exists()
                logger.debug(f"Database exist is {is_exists}")
                if not is_exists:
                    mongo_conn.create_database(initData)
                return is_exists
    except Exception as err:
        logging.error("baseapp.services.database.crud: %s", err)
        error = traceback.format_exc()
        logging.error("baseapp.services.database.crud: %s", error)
        return error
