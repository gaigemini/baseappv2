import logging,json,uuid,traceback

from pymongo.errors import DuplicateKeyError
from typing import Optional, Dict, Any
from pymongo import ASCENDING, DESCENDING

from baseapp.config import setting, mongodb
from baseapp.services._enum import model

config = setting.get_settings()
logger = logging.getLogger()

class CRUD:
    def __init__(self, collection_name="_enum"):
        self.collection_name = collection_name

    def create(self, data: model.Enum):
        """
        Insert a new enum into the collection.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_name]

            enum_data = data.model_dump()
            enum_data["_id"] = data.id or str(uuid.uuid4())
            del enum_data["id"]

            # logger.debug(f"Data enum: {enum_data}")
            try:
                result = collection.insert_one(enum_data)
                logger.info(f"Enum created with id: {result.inserted_id}")
                return {"status": 0, "data": enum_data}
            except DuplicateKeyError:
                logger.error("Duplicate enum ID detected.")
                return {"status": 4, "message": "Enum with the same ID already exists."}
            except Exception as e:
                logger.exception("Error creating enum.")
                return {"status": 4, "message": str(e)}

    def get_by_id(self, enum_id: str):
        """
        Retrieve a enum by ID.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_name]

            try:
                enum = collection.find_one({"_id": enum_id})
                if not enum:
                    return {"status": 4, "message": "Enum not found"}
                return {"status": 0, "data": enum}
            except Exception as e:
                logger.exception("Error retrieving enum.")
                return {"status": 4, "message": str(e)}

    def update_by_id(self, enum_id: str, data: model.EnumUpdate):
        """
        Update a enum's data by ID.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_name]
            enum_data = data.model_dump()
            try:
                update_enum = collection.find_one_and_update({"_id": enum_id}, {"$set": enum_data}, return_document=True)
                if not update_enum:
                    return {"status": 4, "message": "Enum not found"}
                logger.info(f"Enum {enum_id} updated successfully.")
                return {"status": 0, "data": update_enum}
            except Exception as e:
                logger.exception("Error updating enum.")
                return {"status": 4, "message": str(e)}

    def delete_by_id(self, enum_id: str):
        """
        Delete a enum by ID.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_name]
            try:
                result = collection.delete_one({"_id": enum_id})
                if result.deleted_count == 0:
                    return {"status": 4, "message": "Enum not found"}
                logger.info(f"Enum {enum_id} deleted successfully.")
                return {"status": 0, "data": result.deleted_count}
            except Exception as e:
                logger.exception("Error deleting enum.")
                return {"status": 4, "message": str(e)}
            
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

                # Execute query
                cursor = collection.find(query_filter).sort(sort_field, order).skip(skip).limit(limit)
                results = list(cursor)

                # Total count
                total_count = collection.count_documents(query_filter)

                return {
                    "status": 0,
                    "data": results,
                    "pagination": {
                        "current_page": page,
                        "items_per_page": per_page,
                        "total_items": total_count,
                        "total_pages": (total_count + per_page - 1) // per_page,  # Ceiling division
                    },
                }
            except Exception as e:
                logger.exception("Error retrieving documents with filters and pagination.")
                return {"status": 4, "message": str(e)}
