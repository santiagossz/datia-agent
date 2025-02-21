from typing import Any
import logging

fmt = "%(levelprefix)s %(message)s\033[0m"

LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": fmt,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": fmt + "%(client_addr)s - %(status_code)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        # "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        # "uvicorn.access": {"handlers": ["access"], "propagate": False},
        "app": {"handlers": ["default"], "level": "DEBUG", "propagate": False},
    },
}

logger = logging.getLogger("app")
