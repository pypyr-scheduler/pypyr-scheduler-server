import logging
import logging.config
import uuid
import os

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

from .utils import import_external
from . import logger


NEW_JOB_MAX_INSTANCES = 1

class ServerWrapper(object):
    def __init__(self, conf_dir):
        self._conf_dir = conf_dir        
        self._config_file = Path(self._conf_dir) / "scheduler_config.py"
        self._logger = logger.getChild("ServerWrapper")
        self._configure_logging()
        self._scheduler = self._make_scheduler()
        self._service = self._make_service_class() 
        self._server = self._make_shared_memory_server()

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

    def _make_shared_memory_server(self):        
        class SchedulerManager(BaseManager): pass        
        SchedulerManager.register("scheduler", callable=lambda: self._service)

        authkey = self._check_authkey()
        manager = SchedulerManager(address=("", 12345), authkey=str(authkey).encode("utf-8"))
        try:
            server = manager.get_server()
        except OSError as ose:
            self._logger.exception(ose)
            return None
        return server

    def _configure_logging(self):
        imported_logging_config = import_external(self._config_file.resolve(), "log_config")
        logging.config.dictConfig(imported_logging_config)
        self._logger.debug(f"loaded logging config from {self._config_file}")

    def _make_scheduler(self):
        self._logger.debug(f"loading scheduler config from {self._config_file}")
        imported_scheduler_config = import_external(self._config_file.resolve(), "apscheduler")

        # apscheduler .pop()s values from this, so the original has to be preserved
        scheduler_config = deepcopy(imported_scheduler_config)  

        self._logger.debug("config loaded, creating scheduler")
        return BackgroundScheduler(scheduler_config)   

    def _make_service_class(self):
        self._logger.debug(f"loading pypyr config from {self._config_file}")
        self._pypyr_config = import_external(self._config_file.resolve(), "pypyr")  
        if self._logger.level <= logging.DEBUG:
            for k,v in self._pypyr_config.items():
                self._logger.debug(f"{k}: {v}")        
        service = SchedulerService(scheduler=self._scheduler, pypyr_config=self._pypyr_config, logger=self._logger)
        return service

    def shutdown(self):
        # self._server.shutdown()
        self._scheduler.shutdown()

    def start(self):
        if self._server:
            self._scheduler.start() 
            self._server.serve_forever()
        else:
            raise ConnectionError("Could not start server instance.")

class SchedulerService(object):
    def __init__(self, scheduler=None, pypyr_config=None, logger=None, ):
        self._logger = logger or logging.getLogger("pyrsched.RPCService")
        self._pypyr_config = pypyr_config        
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
        log_filename = Path("./logs") / f'{pipeline_name}.log'
        job = self._scheduler.add_job(
            pipeline_runner,
            id=str(uuid.uuid4()),
            name=pipeline_name,
            trigger=IntervalTrigger(seconds=interval),
            next_run_time=None,
            args=[pipeline_name, ],
            max_instances=NEW_JOB_MAX_INSTANCES,
            kwargs={
                'pipeline_context_input': '',
                'working_dir': Path("."), # base_path,
                'log_level': self._pypyr_config.get("pipelines.log_level", logging.INFO),
                'log_path': str(log_filename),
            }
        )

        return job.id
 
    def exposed_modify_job(self, job_id, jobstore=None, **changes):
        return self._scheduler.modify_job(job_id, jobstore, **changes)

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

    def exposed_remove_job(self, job_id, jobstore=None):
        self._scheduler.remove_job(job_id, jobstore)
    
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
    logger.info("starting scheduler")
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
