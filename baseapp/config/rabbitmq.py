import pika,logging
from baseapp.config import setting

logger = logging.getLogger()

class RabbitMqConn:
    def __init__(self, host=None, port=None):
        config = setting.get_settings()
        self.host = host or config.rabbitmq_host
        self.port = port or config.rabbitmq_port
        self.connection = None
        self.channel = None
    
    def __enter__(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host, port=self.port)
            )
            self.channel = self.connection.channel()
            logger.info("RabbitMQ connection and channel established.")
            return self.channel  # Return channel for usage in 'with' block
        except Exception as e:
            logger.exception(f"Failed to connect to RabbitMQ: {e}")
            self.connection = None
            self.channel = None
            return None
    
    def get_connection(self):
        if not self.connection or self.connection.is_closed:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.host, port=self.port)
                )
                logger.info("RabbitMQ connection established.")
            except Exception as e:
                logger.exception(f"Failed to reconnect to RabbitMQ: {e}")
                self.connection = None
        return self.connection

    def get_channel(self):
        if not self.channel or self.channel.is_closed:
            conn = self.get_connection()
            if conn:
                try:
                    self.channel = conn.channel()
                    logger.info("RabbitMQ channel created.")
                except Exception as e:
                    logger.exception(f"Failed to create RabbitMQ channel: {e}")
                    self.channel = None
        return self.channel

    def close(self):
        if self.channel and self.channel.is_open:
            try:
                self.channel.close()
                logger.info("RabbitMQ channel closed.")
            except Exception as e:
                logger.exception(f"Error while closing RabbitMQ channel: {e}")
        if self.connection and self.connection.is_open:
            try:
                self.connection.close()
                logger.info("RabbitMQ connection closed.")
            except Exception as e:
                logger.exception(f"Error while closing RabbitMQ connection: {e}")

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()