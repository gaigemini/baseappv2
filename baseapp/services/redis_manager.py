import argparse
import time
import logging.config
from baseapp.services.redis_queue import RedisQueueManager
from baseapp.services.redis_worker import RedisWorker

import logging.config
logging.config.fileConfig('logging.conf')
from logging import getLogger
logger = getLogger("rabbit")

if __name__ == "__main__":
    # Buat parser untuk argumen command-line
    parser = argparse.ArgumentParser(description="Redis Worker Manager")
    parser.add_argument(
        '--queue', 
        type=str, 
        required=True, 
        help="Nama antrian yang akan di-consume."
    )
    args = parser.parse_args()
    queue_name = args.queue

    logger.info(f"Starting Redis worker for queue: '{queue_name}'...")
    
    queue_manager = RedisQueueManager(queue_name=queue_name)
    worker = RedisWorker(queue_manager)
    worker.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info(f"Stopping Redis worker for queue: '{queue_name}'...")
        worker.stop()
        logger.info("Worker stopped gracefully.")