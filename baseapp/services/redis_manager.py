import argparse
import time
import logging.config
from baseapp.services.redis_queue import RedisQueueManager
# Importing the worker classes
from baseapp.services._redis_worker.email_worker import EmailWorker
from baseapp.services._redis_worker.delete_file_worker import DeleteFileWorker

import logging.config
logging.config.fileConfig('logging.conf')
from logging import getLogger
logger = getLogger("rabbit")

WORKER_MAP = {
    "otp_tasks": EmailWorker,
    "minio_delete_file_tasks": DeleteFileWorker
}

if __name__ == "__main__":
    # Buat parser untuk argumen command-line
    parser = argparse.ArgumentParser(description="Redis Worker Manager")
    parser.add_argument(
        '--queue', 
        type=str, 
        required=True, 
        choices=WORKER_MAP.keys(),
        help="Nama antrian yang akan di-consume."
    )
    args = parser.parse_args()
    queue_name = args.queue

    # Dapatkan class Worker yang sesuai dari map
    WorkerClass = WORKER_MAP.get(queue_name)
    if not WorkerClass:
        logger.error(f"No worker class found for queue: '{queue_name}'")
        exit(1)

    logger.info(f"Starting {WorkerClass.__name__} for queue: '{queue_name}'...")
    
    queue_manager = RedisQueueManager(queue_name=queue_name)
    worker = WorkerClass(queue_manager)
    worker.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info(f"Stopping Redis worker for queue: '{queue_name}'...")
        worker.stop()
        logger.info("Worker stopped gracefully.")