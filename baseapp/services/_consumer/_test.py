import logging,json
logger = logging.getLogger("rabbit")

def _runcommand(msgBody):
    try:
        logger.info("Running command with message body: %s", msgBody)
    except Exception as e:
        logger.debug(e)

if __name__ == "__main__":
    # Send a message to the queue.
    objData = {
        "name": "rabbitmq",
        "description": "test rabbitmq",
    }
    _runcommand(objData)