import uuid
import logging
from pathlib import Path

import psutil

from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.base import JobLookupError
from pypyr.pipelinerunner import main as pipeline_runner

from .utils import PipelineLoggingContext

NEW_JOB_MAX_INSTANCES = 1

def job_function(pipeline_name, log_path, log_level, log_format, pipeline_path):
    logger = logging.getLogger("pypyr")
    log_filename = Path(log_path) / f"{pipeline_name}.log"

    # ToDo: could the handler be instantiated outside and be reused?
    pipeline_handler = logging.FileHandler(log_filename)
    pipeline_handler.setFormatter(logging.Formatter(fmt=log_format))

    with PipelineLoggingContext(logger, loglevel=log_level, handler=pipeline_handler):
        pipeline_runner(
            pipeline_name, pipeline_context_input="", working_dir=Path(pipeline_path),
        )


class SchedulerService(object):
    def __init__(self, scheduler=None, config=None, logger=None):
        self._logger = logger.getChild("service") if logger else logging.getLogger(
            "pyrsched.service"
        )
        self._config = config
        self._scheduler = scheduler

    def _marshal_job(self, job):
        """ make a data structure which is able to be submitted over the RPC line"""
        marshalled_job = job.__getstate__()
        marshalled_job["next_run_time"] = (
            marshalled_job["next_run_time"].isoformat()
            if marshalled_job["next_run_time"]
            else None
        )

        # add an "is_running" flag
        marshalled_job["is_running"] = marshalled_job["next_run_time"] is not None
        trigger = job.trigger.__getstate__()
        marshalled_job["trigger"] = {
            "interval": trigger["interval"].total_seconds(),
            "start_date": trigger["start_date"].isoformat()
            if trigger["start_date"]
            else None,
            "timezone": str(trigger["timezone"]),
        }

        return marshalled_job

    def add_job(self, pipeline_name, interval=60):
        self._logger.info(f"add_job({pipeline_name}, {interval})")

        # ToDo: lookup if a job with the same name already exists and handle duplicate job names (suffix?)

        formatters = self._config.log_config.get(
            "formatters",
            {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                }
            },
        )
        log_format = formatters["standard"]["format"]
        log_path = str(
            Path(self._config.pypyr.get("pipelines.log_path", Path("logs"))).resolve()
        )
        pipeline_path = str(
            Path(self._config.pypyr.get("pipelines.base_path", Path("pipelines"))).resolve()
        )

        job = self._scheduler.add_job(
            job_function,
            id=str(uuid.uuid4()),
            name=pipeline_name,
            trigger=IntervalTrigger(seconds=interval),
            next_run_time=None,
            args=[pipeline_name,],
            max_instances=NEW_JOB_MAX_INSTANCES,
            misfire_grace_time=None,
            coalesce=self._config.apscheduler.get("apscheduler.job_defaults.coalesce", False),
            kwargs={
                "log_path": log_path,
                "log_format": log_format,
                "log_level": self._config.pypyr.get(
                    "pipelines.log_level", logging.WARNING
                ),
                "pipeline_path": pipeline_path
            },
        )

        return job.id

    def reschedule_job(self, job_id, interval=60):
        self._logger.info(f"reschedule_job({job_id})")
        trigger = IntervalTrigger(seconds=interval)
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
        self._logger.info(f"remove_job({job_id})")
        try:
            self._scheduler.remove_job(job_id)
        finally:
            return None  # self._marshal_job(job_id)

    def get_job(self, job_id):
        self._logger.info(f"get_job({job_id})")
        job = self._scheduler.get_job(job_id)
        return self._marshal_job(job) if job is not None else None

    def list_jobs(self):
        self._logger.info(f"list_jobs()")
        job_list = self._scheduler.get_jobs()
        return [self._marshal_job(job) for job in job_list]

    def state(self):
        self._logger.info("state()")
        job_list = self._scheduler.get_jobs()
        state_obj = {
            "run_state": self._scheduler.state,
            "is_running": self._scheduler.running,
            "total_jobs": len(job_list),
            "job_list": [self._marshal_job(job) for job in job_list],
            "cpu_load": psutil.getloadavg(),
        }
        return state_obj
