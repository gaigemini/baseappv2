import redis,logging
from config import setting

logger = logging.getLogger()

class Redis:
    def __init__(self, host=None, port=None, max_connections=10):
        config = setting.get_settings()
        self.host = host or config.redis_host
        self.port = port or config.redis_port
        self.max_connections  = max_connections or config.redis_max_connections

        # Inisialisasi Redis Connection Pool
        try:
            self.pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                max_connections=self.max_connections,
            )
            self._conn = redis.Redis(connection_pool=self.pool)
            logger.info("Redis Connection Pool established.")
        except Exception as e:
            logger.exception("Failed to initialize Redis Connection Pool: %s", e)
            self.pool = None
            self._conn = None
    
    @property
    def conn(self):
        if self._conn:
            try:
                self._conn.ping()  # Tes koneksi
                return self._conn
            except Exception as e:
                logger.exception("Redis connection error: %s", e)
                return None
        return None

    def close(self):
        if self.pool:
            self.pool.disconnect()
            logger.info("Redis Connection Pool closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()