from pymongo import MongoClient
import logging
from config import setting

logger = logging.getLogger()

logger = logging.getLogger(__name__)

class MongoConn(object):
    def __init__(self, host=None, port=None, database=None, username=None, password=None):
        config = setting.get_settings()
        self.host = host or config.mongodb_host
        self.port = port or config.mongodb_port
        self.database = database or config.mongodb_db
        self.username = username or config.mongodb_user
        self.password = password or config.mongodb_pass
        self._conn = None
        self._db = None

    def __enter__(self):
        try:
            # Buat URL koneksi
            uri = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}" if self.username and self.password else f"mongodb://{self.host}:{self.port}"
            
            # Membuka koneksi ke MongoDB
            self._conn = MongoClient(uri)
            logger.info("Connected to MongoDB")

            if self.database:
                self._db = self._conn[self.database]

        except Exception as e:
            logger.exception("Failed to connect to MongoDB")
            raise e

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()
        if exc_type is not None:
            logger.exception(f"mod: MongoConn.__exit__, exc_type: {exc_type}, exc_value: {exc_value}, exc_traceback: {exc_traceback}")

    def get_database(self):
        if not self._db:
            logger.warning("Database is not selected. Use __enter__ method with a database name.")
        return self._db

    def get_connection(self):
        if not self._conn:
            self.__enter__()
        return self._conn

    def close(self):
        if self._conn:
            logger.info("Closing connection to MongoDB")
            self._conn.close()
            self._conn = None
            self._db = None
