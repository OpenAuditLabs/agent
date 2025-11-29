import json
import logging

DEFAULT_LOG_FORMAT = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
DEFAULT_LOG_FORMATTER = logging.Formatter(DEFAULT_LOG_FORMAT)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_record)


def setup_logger(name: str, level: int = logging.INFO, json_format: bool = False) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        logger.setLevel(level)
        for h in logger.handlers:
            h.setLevel(level)
        return logger

    logger.setLevel(level)
    handler = logging.StreamHandler()
    if json_format:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(DEFAULT_LOG_FORMATTER)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
