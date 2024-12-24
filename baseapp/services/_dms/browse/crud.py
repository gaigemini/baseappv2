import logging

from pymongo.errors import PyMongoError
from typing import Optional, Dict, Any
from pymongo import ASCENDING, DESCENDING

from baseapp.config import setting, mongodb, minio
from baseapp.services.audit_trail_service import AuditTrailService

config = setting.get_settings()

class CRUD:
    def __init__(self):
        self.collection_file = "_dmsfile"
        self.collection_folder = "_dmsfolder"
        self.collection_organization = "_organization"
        self.minio_conn = minio.MinioConn()
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

    def browse_by_key(self, filters: Optional[Dict[str, Any]] = None):
        """
        Retrieve all documents from the collection with optional filters, pagination, and sorting.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_file]
            with self.minio_conn as conn:
                try:
                    # Apply filters
                    query_filter = {}
                    if filters:
                        for key, value in filters.items():
                            if isinstance(value, str) and value.startswith("regex:"):
                                # Extract regex pattern from value
                                regex_pattern = value.split("regex:", 1)[1]
                                query_filter[key] = {"$regex": regex_pattern, "$options": "i"}  # Case-insensitive regex
                            else:
                                query_filter[key] = value

                    # Selected fields
                    selected_fields = {
                        "id": "$_id",
                        "filename": 1,
                        "filestat": 1,
                        "folder_id": 1,
                        "folder_path": 1,
                        "metadata": 1,
                        "doctype": 1,
                        "refkey_name": 1,
                        "_id": 0
                    }

                    # Aggregation pipeline
                    pipeline = [
                        {"$match": query_filter},  # Filter stage
                        {"$project": selected_fields}  # Project only selected fields
                    ]

                    # Execute aggregation pipeline
                    cursor = collection.aggregate(pipeline)
                    results = list(cursor)

                    # write audit trail for success
                    self.audit_trail.log_audittrail(
                        mongo,
                        action="retrieve",
                        target=self.collection_file,
                        target_id="agregate",
                        details={"aggregate": pipeline},
                        status="success"
                    )
                    
                    retData = {}
                    for x in results:
                        retData[x['refkey_name']] = {
                            'id':x['id'],
                            'folder_id':x['folder_id'],
                            'folder_path':x['folder_path'],
                            'filename':x['filename'],
                            'filestat':x['filestat'],
                            'metadata':x['metadata'],
                        }
                        # presigned url
                        minio_client = conn.get_minio_client()
                        url = minio_client.presigned_get_object(config.minio_bucket, x['filename'])
                        retData[x['refkey_name']]['url'] = url

                    return {
                        "data": retData
                    }
                except PyMongoError as pme:
                    self.logger.error(f"Error retrieving index with filters and pagination: {str(e)}")
                    # write audit trail for success
                    self.audit_trail.log_audittrail(
                        mongo,
                        action="retrieve",
                        target=self.collection_file,
                        target_id="agregate",
                        details={"aggregate": pipeline},
                        status="failure"
                    )
                    raise ValueError("Database error while retrieve document") from pme
                except Exception as e:
                    self.logger.exception(f"Unexpected error during deletion: {str(e)}")
                    raise

    def list_folder(self, filters: Optional[Dict[str, Any]] = None):
        """
        Retrieve all documents from the collection with optional filters, pagination, and sorting.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_folder]
            try:
                # Apply filters
                query_filter = {}
                if filters:
                    for key, value in filters.items():
                        if isinstance(value, str) and value.startswith("regex:"):
                            # Extract regex pattern from value
                            regex_pattern = value.split("regex:", 1)[1]
                            query_filter[key] = {"$regex": regex_pattern, "$options": "i"}  # Case-insensitive regex
                        else:
                            query_filter[key] = value

                # Selected fields
                selected_fields = {
                    "id": "$_id",
                    "folder_name": 1,
                    "level": 1,
                    "pid": 1,
                    "_id": 0
                }

                # Aggregation pipeline
                pipeline = [
                    {"$match": query_filter},  # Filter stage
                    {"$project": selected_fields}  # Project only selected fields
                ]

                self.logger.debug(f"Pipeline data: {pipeline}")

                # Execute aggregation pipeline
                cursor = collection.aggregate(pipeline)
                results = list(cursor)

                retData = []
                for x in results:
                    objFolder = {
                        'id':x['id'],
                        'value':x['folder_name']
                    }
                    retData.append(objFolder)

                if "pid" not in filters:
                    retData.append({
                        'id':'delete',
                        'value':'Trash'
                    })

                # write audit trail for success
                self.audit_trail.log_audittrail(
                    mongo,
                    action="retrieve",
                    target=self.collection_folder,
                    target_id="agregate",
                    details={"aggregate": pipeline},
                    status="success"
                )

                return {
                    "data": retData
                }
            except PyMongoError as pme:
                self.logger.error(f"Error retrieving index with filters and pagination: {str(e)}")
                # write audit trail for success
                self.audit_trail.log_audittrail(
                    mongo,
                    action="retrieve",
                    target=self.collection_folder,
                    target_id="agregate",
                    details={"aggregate": pipeline},
                    status="failure"
                )
                raise ValueError("Database error while retrieve document") from pme
            except Exception as e:
                self.logger.exception(f"Unexpected error during deletion: {str(e)}")
                raise

    def list_file(self, filters: Optional[Dict[str, Any]] = None, page: int = 1, per_page: int = 10, sort_field: str = "_id", sort_order: str = "asc"):
        """
        Retrieve all documents from the collection with optional filters, pagination, and sorting.
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_file]
            with self.minio_conn as conn:
                try:
                    # Apply filters
                    query_filter = {}
                    if filters:
                        for key, value in filters.items():
                            if isinstance(value, str) and value.startswith("regex:"):
                                # Extract regex pattern from value
                                regex_pattern = value.split("regex:", 1)[1]
                                query_filter[key] = {"$regex": regex_pattern, "$options": "i"}  # Case-insensitive regex
                            else:
                                query_filter[key] = value

                    # Pagination
                    skip = (page - 1) * per_page
                    limit = per_page

                    # Sorting
                    order = ASCENDING if sort_order == "asc" else DESCENDING

                    # Selected fields
                    selected_fields = {
                        "id": "$_id",
                        "filename": 1,
                        "filestat": 1,
                        "folder_id": 1,
                        "folder_path": 1,
                        "metadata": 1,
                        "doctype": 1,
                        "refkey_name": 1,
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
                        target=self.collection_file,
                        target_id="agregate",
                        details={"aggregate": pipeline},
                        status="success"
                    )

                    for i, data in enumerate(results):
                        # presigned url
                        minio_client = conn.get_minio_client()
                        url = minio_client.presigned_get_object(config.minio_bucket, data['filename'])
                        data['url'] = url

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
                    self.logger.error(f"Error retrieving index with filters and pagination: {str(e)}")
                    # write audit trail for success
                    self.audit_trail.log_audittrail(
                        mongo,
                        action="retrieve",
                        target=self.collection_file,
                        target_id="agregate",
                        details={"aggregate": pipeline},
                        status="failure"
                    )
                    raise ValueError("Database error while retrieve document") from pme
                except Exception as e:
                    self.logger.exception(f"Unexpected error during deletion: {str(e)}")
                    raise

    def check_storage(self):
        """
        Retrieve a free space by org id (session).
        """
        client = mongodb.MongoConn()
        with client as mongo:
            collection = mongo._db[self.collection_organization]
            try:
                obj = collection.find_one({"_id": self.org_id})
                if not obj:
                    # write audit trail for fail
                    self.audit_trail.log_audittrail(
                        mongo,
                        action="retrieve",
                        target=self.collection_organization,
                        target_id=self.org_id,
                        details={"_id": self.org_id},
                        status="failure",
                        error_message="Organization not found"
                    )
                    raise ValueError("Organization not found")
                # write audit trail for success
                self.audit_trail.log_audittrail(
                    mongo,
                    action="retrieve",
                    target=self.collection_organization,
                    target_id=self.org_id,
                    details={"_id": self.org_id, "retrieved": obj},
                    status="success"
                )
                return {"storage":obj["storage"],"usedstorage":obj["usedstorage"]}
            except PyMongoError as pme:
                self.logger.error(f"Database error occurred: {str(pme)}")
                # write audit trail for fail
                self.audit_trail.log_audittrail(
                    mongo,
                    action="retrieve",
                    target=self.collection_organization,
                    target_id=self.org_id,
                    details={"_id": self.org_id},
                    status="failure",
                    error_message=str(pme)
                )
                raise ValueError("Database error occurred while find document.") from pme
            except Exception as e:
                self.logger.exception(f"Unexpected error occurred while finding document: {str(e)}")
                raise
