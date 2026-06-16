from app.utils.logger import logger


def log_event(event: str, data: dict = None):
    # Standard structured logger for all business events
    logger.info({
        "event": event,
        "data": data or {}
    })