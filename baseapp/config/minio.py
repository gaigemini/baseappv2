import logging
from minio import Minio
from baseapp.config import setting

logger = logging.getLogger()

class MinConn:
    def __init__(self, host=None, port=None, access_key=None, secret_key=None, secure=False, bucket="baseapp", verify=False):
        config = setting.get_settings()
        self.host = host or config.minio_host
        self.port = port or config.minio_port
        self.access_key = access_key or config.minio_access_key
        self.secret_key = secret_key or config.minio_secret_key
        self.secure = secure or config.minio_secure
        self.bucket = bucket or config.minio_bucket
        self.verify = verify or config.minio_verify

        try:
            # Inisialisasi koneksi Minio
            self._conn = Minio(
                endpoint=f"{self.host}:{self.port}",
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure,
                http_client=None if self.verify else False,
            )
            logger.info(f"Connected to MinIO at {self.host}:{self.port}")
        except Exception as e:
            logger.exception(f"Failed to connect to MinIO: {e}")
            self._conn = None

    def __enter__(self):
        return self
    
    def get_minio_client(self):
        """
        Returns the MinIO client instance.
        """
        if not self._conn:
            logger.error("MinIO client is not initialized.")
        return self._conn

    def bucket_exists(self):
        """
        Check if the default bucket exists.
        """
        try:
            if self._conn.bucket_exists(self.bucket):
                logger.info(f"Bucket '{self.bucket}' exists.")
                return True
            else:
                logger.warning(f"Bucket '{self.bucket}' does not exist.")
                return False
        except Exception as e:
            logger.exception(f"Failed to check bucket existence: {e}")
            return False

    def create_bucket(self):
        """
        Create the default bucket if it doesn't exist.
        """
        try:
            if not self._conn.bucket_exists(self.bucket):
                self._conn.make_bucket(self.bucket)
                logger.info(f"Bucket '{self.bucket}' created.")
            else:
                logger.info(f"Bucket '{self.bucket}' already exists.")
        except Exception as e:
            logger.exception(f"Failed to create bucket '{self.bucket}': {e}")

    def close(self):
        """
        Close the MinIO connection (if needed).
        """
        # MinIO client in the current library doesn't require explicit connection close,
        # but this method can be used for cleanup in future versions if required.
        logger.info("MinIO connection closed.")

    

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def get_minio_endpoint(self):
        """
        Get MinIO endpoint from settings
        """
        return f"{self.host}:{self.port}"