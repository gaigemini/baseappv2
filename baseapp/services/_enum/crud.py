import logging,json,uuid,traceback

from baseapp.config import setting, mongodb
from baseapp.services._enum import model

config = setting.get_settings()
logger = logging.getLogger()

def create_enum(data: model.EnumCreate):
    try:
        client = mongodb.MongoConn()
        enum_dict = data.dict()
        enum_dict["_id"] = str(uuid.uuid4())  # Menggunakan UUID baru untuk _id
        result = client._enum.insert_one(enum_dict)
        enum_dict["id"] = str(result.inserted_id)  # Mengonversi ObjectId menjadi string
        return enum_dict
    except Exception as err:
        logging.error("baseapp.services.enum.crud: %s", err)
        error = traceback.format_exc()
        logging.error("baseapp.services.enum.crud: %s", error)
        return error
