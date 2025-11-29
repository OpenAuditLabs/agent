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

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            log_record["stack"] = self.formatStack(record.stack_info)

        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "levelname",
                "pathname",
                "lineno",
                "msg",
                "args",
                "exc_info",
                "exc_text",
                "stack_info",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "asctime",
                "message",
            ]:
                log_record[key] = value

        return json.dumps(log_record)


def setup_logger(
    name: str, level: int = logging.INFO, json_format: bool = False
) -> logging.Logger:
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
