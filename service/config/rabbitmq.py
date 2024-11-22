import pika,logging
from config import setting

logger = logging.getLogger()

class RabbitMq:
    def __init__(self, host=None, port=None):
        config = setting.get_settings()
        self.host = host or config.rabbitmq_host
        self.port = port or config.rabbitmq_port

        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, port=self.port))
            self.channel = self.connection.channel()
        except Exception as e:
            logger.exception(f"Failed to connect to RabbitMQ: {e}")
            self.connection = None
            self.channel = None

    def close(self):
        if self.channel and self.channel.is_open:
            self.channel.close()
        if self.connection and self.connection.is_open:
            self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()