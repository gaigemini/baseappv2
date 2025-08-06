import logging
from baseapp.config import setting, redis, mongodb, minio, clickhouse
from baseapp.services import publisher
from baseapp.services.redis_queue import RedisQueueManager

config = setting.get_settings()
logger = logging.getLogger()

def test_connection_to_redis():
    logger.info("Redis test connection")
    client = redis.RedisConn()
    with client as redis_conn:
        redis_conn.set("test_connection", "test", 60)
        res = redis_conn.get("test_connection")
        redis_conn.delete("test_connection", "test")
        result = f"redis: {res}"
        logger.info(result)
        return result
    
def test_connection_to_mongodb():
    logger.info("Mongodb test connection")
    client = mongodb.MongoConn()
    with client as mongo_conn:
        server_info = mongo_conn.get_connection().server_info()
        result = f"mongodb: {server_info.get('version', 'Unknown')}"
        logger.info(result)
        return result
    
def test_connection_to_minio():
    logger.info("Minio test connection")
    client = minio.MinioConn()
    with client as minio_conn:
        try:
            if minio_conn.bucket_exists():
                return "Bucket exist"
            else:
                return "Bucket not exist"
        except Exception as err:
            logger.exception(f"Unexpected error occurred while testing minio connection. {str(err)}")
            raise
    
def test_connection_to_rabbit():
    logger.info("RabbitMQ test connection")
    try:
        objData = {
            "name": "rabbitmq",
            "message": "Hello RabbitMQ!"
        }
        publisher.publish_message(queue_name="webhook_tasks", task_data=objData)
        return "RabbitMQ: Connection successful. Queue 'webhook_tasks' declared."
    except Exception as e:
        logger.error(f"Failed to publish message to RabbitMQ: {e}")
        raise
    
def test_connection_to_clickhouse():
    logger.info("Clickhouse test connection")
    client = clickhouse.ClickHouseConn()
    with client as clickhouse_conn:
        result = clickhouse_conn.query("SELECT 1")
        if result:
            logging.info("ClickHouse: Connection successful")
            return "ClickHouse: Connection successful"
        else:
            logging.error("ClickHouse: Connection test failed")
            raise ValueError("ClickHouse: Connection test failed")
        
def test_redis_worker():
    logger.info("Redis worker test connection")
    try:
        queue_manager = RedisQueueManager(queue_name="otp_tasks")
        queue_manager.enqueue_task({"email": "aldian.mm.02@gmail.com", "otp": "123456", "subject":"Login with OTP", "body":f"Berikut kode OTP Anda: 123456"})
        return "Redis worker: Task enqueued successfully."
    except Exception as e:
        logger.error(f"Failed to publish message to Redis: {e}")
        raise