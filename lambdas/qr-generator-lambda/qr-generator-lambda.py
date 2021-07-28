import segno
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    logger.info(event)

    status = "Success"

    value = {
        "status": status
    }

    return json.dumps(value)
