logging = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(thread)x] [%(levelname)s]"
                      " %(name)s: %(message)s"
        },
        "with_function": {
            "format": "%(asctime)s [%(thread)x] [%(levelname)s]"
                      " %(name)s.%(funcName)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "d",  # days
            "interval": 1,
            "backupCount": 10,  # keep 10 Files
            "filename": "/gematik/pypyr-scheduler/log/pyrsched.log",
        },
        "console": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
        "nologging": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.NullHandler",
        }
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        },
        # pypyr logger, step execution info
        "pypyr": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        },
        # scheduler logs (web app)
        "pyrsched": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False
        },
        # scheduler logs (scheduler)
        "apscheduler": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False
        },
        # http logs (aiohttp)
        "aiohttp": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}

pipelines = {
    # pypyr appends pipelines/ to this automatically
    # "base_path": "/gematik/pypyr-scheduler/",
    "base_path": "C:\Projects\pypyr-scheduler",
}
