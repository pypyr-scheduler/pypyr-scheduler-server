import logging
import logging.config
import os
import threading
import uuid
from copy import deepcopy
from multiprocessing.managers import BaseManager
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler

from . import logger
from .service import SchedulerService
from .utils import import_external

class ServerWrapper(object):
    def __init__(self, conf_dir):
        self._conf_dir = conf_dir
        self._config_file = Path(self._conf_dir) / "scheduler_config.py"
        self._logger = logger.getChild("ServerWrapper")

        self._config = import_external(self._config_file)
        logging.config.dictConfig(self._config.log_config)

    def _check_authkey(self):
        # generate an authkey if it was not provided via environment
        authkey = os.environ.get("PYRSCHED_SECRET", None)
        if not authkey:
            self._logger.warning(
                "WARNING! Shared secret not set. Use the following generated secret for the clients:"
            )
            authkey = uuid.uuid4()
        else:
            self._logger.warning("WARNING! Using shared secret from the environment:")
        self._logger.warning(authkey)
        return authkey

    def shutdown(self):  # pragma: no cover
        # self._server.shutdown()
        try:
            self._scheduler.shutdown()
        except:
            pass

    def start(self):  # pragma: no cover
        if self._logger.level <= logging.DEBUG:
            self._logger.debug("Starting server with config:")
            for k, v in self._config.pypyr.items():
                self._logger.debug(f"{k}: {v}")

        try:
            scheduler_config = deepcopy(self._config.apscheduler)
            scheduler = BackgroundScheduler(scheduler_config)

            class SchedulerManager(BaseManager):
                pass

            authkey = self._check_authkey()
            service = SchedulerService(
                scheduler=scheduler, config=self._config, logger=self._logger
            )
            SchedulerManager.register("scheduler", callable=lambda: service)

            manager = SchedulerManager(
                address=("", self._config.pypyr.get("server_port", 12345)),
                authkey=str(authkey).encode("utf-8"),
            )
            server = manager.get_server()

            scheduler.start()
            server.serve_forever()

        except OSError as ose:
            self._logger.error(ose.strerror)
            