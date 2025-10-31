import logging

DEFAULT_LOG_FORMAT = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
DEFAULT_LOG_FORMATTER = logging.Formatter(DEFAULT_LOG_FORMAT)


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        logger.setLevel(level)
        for h in logger.handlers:
            h.setLevel(level)
        return logger

    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(DEFAULT_LOG_FORMATTER)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
