import logging.config

from dotenv import load_dotenv

import logstash

load_dotenv()


def create_dev_logger():
    """Create the application logger."""
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            },
            "json": {
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            },
        },
        "handlers": {
            "standard": {
                "class": "logging.StreamHandler",
                "formatter": "json",
            },
        },
        "loggers": {"": {"handlers": ["standard"], "level": logging.INFO}},
    }

    logging.config.dictConfig(config)

    logger = logging.getLogger(__name__)

    return logger


def create_prod_logger():
    """Create the application logger."""
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            },
            "json": {
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            },
        },
        "handlers": {
            "standard": {
                "class": "logging.StreamHandler",
                "formatter": "json",
            },
        },
        "loggers": {"": {"handlers": ["standard"], "level": logging.INFO}},
    }

    logging.config.dictConfig(config)

    logger = logging.getLogger(__name__)

    return logger


LOGGER = create_dev_logger()
