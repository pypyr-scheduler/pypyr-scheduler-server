import logging
import logging.config
import uuid
import os
import threading

import psutil
import click

from dataclasses import dataclass, field, asdict
from pathlib import Path
from copy import deepcopy

from multiprocessing.managers import BaseManager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.base import JobLookupError
from pypyr.pipelinerunner import main as pipeline_runner

from .utils import import_external, import_external_attribute
from . import logger


NEW_JOB_MAX_INSTANCES = 1

class ServerWrapper(object):
    def __init__(self, conf_dir):
        self._conf_dir = conf_dir        
        self._config_file = Path(self._conf_dir) / "scheduler_config.py"
        self._logger = logger.getChild("ServerWrapper")

        self._config = import_external(self._config_file)
        logging.config.dictConfig(self._config.log_config)

        self._monkeypatch_pypyr_logging()

    def _check_authkey(self):
        # generate an authkey if it was not provided via environment
        authkey = os.environ.get("PYRSCHED_SECRET", None)
        if not authkey:
            self._logger.warning("WARNING! Shared secret not set. Use the following generated secret for the clients:")
            authkey = uuid.uuid4()
        else:
            self._logger.warning("WARNING! Using shared secret from the environment:")                
        self._logger.warning(authkey)
        return authkey

    def shutdown(self):
        # self._server.shutdown()
        try:
            self._scheduler.shutdown()
        except:
            pass

    def start(self):
        if self._logger.level <= logging.DEBUG:
            self._logger.debug("Starting server with config:")
            for k,v in self._config.pypyr.items():
                self._logger.debug(f"{k}: {v}")    
              
        try:
            scheduler_config = deepcopy(self._config.apscheduler)  

            scheduler = BackgroundScheduler(scheduler_config)   

            class SchedulerManager(BaseManager): pass  
            authkey = self._check_authkey()
            service = SchedulerService(scheduler=scheduler, config=self._config, logger=self._logger)          
            SchedulerManager.register("scheduler", callable=lambda: service)

            manager = SchedulerManager(address=("", self._config.pypyr.get("server_port", 12345)), authkey=str(authkey).encode("utf-8"))
            server = manager.get_server()

            scheduler.start() 
            server.serve_forever()

        except OSError as ose:
            self._logger.error(ose.strerror)

    def _monkeypatch_pypyr_logging(self):
        import pypyr.log.logger 
        # look for the handler named "default" in the handler list. There is no dict lookup though.
        def new_set_root_logger(root_log_level, log_path=None):
            handlers = []
            if log_path:
                file_handler = logging.FileHandler(log_path)
                handlers.append(file_handler)

            pypyr.log.logger.set_logging_config(root_log_level, handlers=handlers)
            pypyr.log.logger.set_up_notify_log_level()

            root_logger = logging.getLogger("pypyr")
            root_logger.debug(
                "Root logger %s configured with level %s",
                root_logger.name, root_log_level)

        pypyr.log.logger.set_root_logger = new_set_root_logger
        # done patching, pypyr now uses our own log format


class PipelineLoggingContext:
    def __init__(self, logger, handler=None):
        self.logger = logger
        self.handler = handler
        self.lock = threading.Lock()

    def __enter__(self):
        if self.handler:
            self.lock.acquire()
            self.logger.addHandler(self.handler)

    def __exit__(self, et, ev, tb):
        if self.handler:
            self.logger.removeHandler(self.handler)
            self.lock.release()


def job_function(pipeline_name, log_path, log_level, log_format):
    logger = logging.getLogger("pypyr")    
    log_filename = Path(log_path) / f'{pipeline_name}.log'
    pipeline_handler = logging.FileHandler(log_filename)
    pipeline_handler.setFormatter(logging.Formatter(fmt=log_format))
    
    with PipelineLoggingContext(logger, handler=pipeline_handler):
        pipeline_runner(pipeline_name, pipeline_context_input='', working_dir=Path("."), log_level=log_level, log_path=None)

class SchedulerService(object):
    def __init__(self, scheduler=None, config=None, logger=None):
        self._logger = logger.getChild("service") or logging.getLogger("pyrsched.service")
        self._config = config        
        self._scheduler = scheduler        

    def _marshal_job(self, job):
        """ make a data structure which is able to be submitted over the RPC line"""
        marshalled_job = job.__getstate__()
        marshalled_job["next_run_time"] = marshalled_job["next_run_time"].isoformat() if marshalled_job["next_run_time"] else None
        
        # add an "is_running" flag
        marshalled_job["is_running"] = marshalled_job["next_run_time"] is not None
        trigger = job.trigger.__getstate__()
        marshalled_job["trigger"] = {
            "interval": trigger["interval"].total_seconds(),
            "start_date": trigger["start_date"].isoformat() if trigger["start_date"] else None,
            "timezone": str(trigger["timezone"]),
        }
        
        return marshalled_job


    def add_job(self, pipeline_name, interval=60):
        self._logger.info(f"add_job({pipeline_name}, {interval})")

        # ToDo: lookup if a job with the same name already exists and handle duplicate job names (suffix?)

        formatters = self._config.log_config.get("formatters", {"standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}})
        log_format = formatters["standard"]["format"]

        job = self._scheduler.add_job(
            job_function,
            id=str(uuid.uuid4()),
            name=pipeline_name,
            trigger=IntervalTrigger(seconds=interval),
            next_run_time=None,
            args=[pipeline_name, ],
            max_instances=NEW_JOB_MAX_INSTANCES,
            kwargs={
                "log_path": Path(self._config.pypyr.get("pipelines.log_path", Path("logs"))),
                "log_format": log_format,  
                "log_level": self._config.pypyr.get("pipelines.log_level", logging.WARNING),
            }
        )

        return job.id

    def reschedule_job(self, job_id, interval=60):
        self._logger.info(f"reschedule_job({job_id})")
        trigger=IntervalTrigger(seconds=interval)
        try:
            job = self._scheduler.reschedule_job(job_id, trigger=trigger)
        except JobLookupError as jle:
            self._logger.exception(jle, exc_info=False)
            return None            
        return self._marshal_job(job)

    def pause_job(self, job_id):
        self._logger.info(f"pause_job({job_id})")
        try:
            job = self._scheduler.pause_job(job_id)
        except JobLookupError as jle:
            self._logger.exception(jle, exc_info=False)
            return None
        return self._marshal_job(job)

    def start_job(self, job_id):
        """ Start a job. 

        To start a job, it has to be present in the jobstore, otherwise this method
        will return ``None`` over the wire. 

        If the job exists in the jobstore, the scheduler is advised to start the job.

        :param job_id: The ID of the job to be started
        :type job_id: string
        :return: the job which was started or None if the job was not found in the jobstore
        :rtype: Job state or None
        """
        self._logger.info(f"start_job({job_id})")
        try:
            job = self._scheduler.resume_job(job_id)
        except JobLookupError as jle:
            self._logger.exception(jle, exc_info=False)
            return None
        return self._marshal_job(job)

    def remove_job(self, job_id):
        self._scheduler.remove_job(job_id)
        return None  # self._marshal_job(job_id)
    
    def get_job(self, job_id):
        self._logger.info(f"get_job({job_id})")
        job = self._scheduler.get_job(job_id)
        return self._marshal_job(job)

    def list_jobs(self):
        self._logger.info(f"list_jobs()")
        job_list = self._scheduler.get_jobs()
        return [self._marshal_job(job) for job in job_list]

    def state(self):
        self._logger.debug("state()")
        job_list = self._scheduler.get_jobs()
        state_obj = {
            "run_state": self._scheduler.state,
            "is_running": self._scheduler.running,
            "total_jobs": len(job_list),
            "job_list": [self._marshal_job(job) for job in job_list],
            "cpu_load": psutil.getloadavg(),
        }
        return state_obj

@click.command()
@click.option("-c", "--conf", "conf_dir", default="conf", help="config directory")
def cli(conf_dir):    
    click.echo(f"Starting scheduler. Config: {Path(conf_dir).resolve()}")
    server = ServerWrapper(conf_dir)
    try:
        server.start()
    except (KeyboardInterrupt, SystemExit, ConnectionError) as e:
        logger.info("Shutdown signal received.")
        # logger.exception(e)
    finally:
        logger.info("Shutting down scheduler.")
        server.shutdown()
        logger.info("Scheduler shutdown complete.")

if __name__ == '__main__': 
    cli(prog_name='pyrsched-server')
