import logging
import traceback
from baseapp.config import setting, redis, mongodb, minio, rabbitmq, clickhouse

config = setting.get_settings()

def test_connection_to_redis():
    try:
        # client = redis.RedisConn()
        # redis_conn = client.get_connection()
        # redis_conn.set("test_connection", "test", 60)
        # res = redis_conn.get("test_connection")
        # redis_conn.delete("test_connection", "test")
        # result = f"redis: {res.decode('utf-8')}"
        # logging.info(result)
        # redis_conn.close()
        # return result
        
        client = redis.RedisConn()
        with client as redis_conn:
            # Test the connection by retrieving server info
            redis_conn.set("test_connection", "test", 60)
            res = redis_conn.get("test_connection")
            redis_conn.delete("test_connection", "test")
            result = f"redis: {res.decode('utf-8')}"
            logging.info(result)
            return result
    except Exception as err:
        logging.error("redis: %s", err)
        error = traceback.format_exc()
        logging.error("redis: %s", error)
        return error
    
def test_connection_to_mongodb():
    try:
        client = mongodb.MongoConn()
        with client as mongo_conn:
            server_info = mongo_conn.get_connection().server_info()
            result = f"mongodb: {server_info.get('version', 'Unknown')}"
            logging.info(result)
            return result
    except Exception as err:
        logging.error("mongodb: %s", err)
        error = traceback.format_exc()
        logging.error("mongodb: %s", error)
        return error
    
def test_connection_to_minio():
    try:
        # Initialize MinCon instance
        client = minio.MinConn()
        with client as minio_conn:
            # Test the connection by checking if the default bucket exists
            if minio_conn.bucket_exists():
                result = f"minio: Connection successful, bucket '{minio_conn.bucket}' exists."
            else:
                result = f"minio: Connection successful, bucket '{minio_conn.bucket}' does not exist."
            
            # Log the result
            logging.info(result)
            return result
    except Exception as err:
        # Log the error
        logging.error("minio: %s", err)
        error = traceback.format_exc()
        logging.error("minio: %s", error)
        return error
    
def test_connection_to_rabbit():
    try:
        # Initialize RabbitMQ connection
        client = rabbitmq.RabbitMqConn()
        with client as rabbit_conn:
            if rabbit_conn:
                # Uji koneksi dengan mendeklarasikan queue sementara
                rabbit_conn.queue_declare(queue='test_queue', durable=False, auto_delete=True)
                result = "RabbitMQ: Connection successful. Queue 'test_queue' declared."
            else:
                result = "RabbitMQ: Connection failed. Unable to create channel."

            # Log the result
            logging.info(result)
            return result
    except Exception as err:
        # Log the error
        logging.error("RabbitMQ: %s", err)
        error = traceback.format_exc()
        logging.error("RabbitMQ: %s", error)
        return f"RabbitMQ: Connection test failed. Error: {err}"
    
def test_connection_to_clickhouse():
    try:
        client = clickhouse.ClickHouseConn()
        with client as clickhouse_conn:
            # Uji koneksi dengan query sederhana
            result = clickhouse_conn.query("SELECT 1")
            if result:
                logging.info("ClickHouse: Connection successful")
                return "ClickHouse: Connection successful"
            else:
                logging.warning("ClickHouse: Connection test failed")
                return "ClickHouse: Connection test failed"
    except Exception as err:
        logging.error(f"ClickHouse: Connection test failed. Error: {err}")
        error = traceback.format_exc()
        logging.error("RabbitMQ: %s", error)
        return f"ClickHouse: Connection test failed. Error: {err}"