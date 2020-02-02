"""
This is an example showing how to make the scheduler into a remotely accessible service.
It uses RPyC to set up a service through which the scheduler can be made to add, modify and remove
jobs.

To run, first install RPyC using pip. Then change the working directory to the ``rpc`` directory
and run it with ``python -m server``.
"""

import logging
import logging.config
import uuid

import rpyc
import psutil

from dataclasses import dataclass, field, asdict
from pathlib import Path
from copy import deepcopy

from rpyc.utils.server import ThreadedServer
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.base import JobLookupError
from pypyr.pipelinerunner import main as pipeline_runner

from .utils import import_external

NEW_JOB_MAX_INSTANCES = 1

class ServerWrapper(object):
    def __init__(self):
        self._logger = logging.getLogger("pyrsched-server.ServerWrapper")
        self._scheduler = BackgroundScheduler()   
        self._server = ThreadedServer(
            SchedulerService(scheduler=self._scheduler), 
            port=12345, 
            protocol_config={
                'allow_public_attrs': True,
            }, 
            logger=logger
        )

    def shutdown(self):
        self._server.close()
        self._scheduler.shutdown()

    def start(self):
        self._scheduler.start() 
        self._server.start()
        

class SchedulerService(rpyc.Service):
    def __init__(self, scheduler=None, logger=None):
        self._logger = logger or logging.getLogger("pyrsched.RPCService")
        self._scheduler = scheduler        

    def _marshal_job(self, job):
        """ make a data structure which is able to be submitted over the RPC line"""
        marshalled_job = job.__getstate__()
        return marshalled_job

    def exposed_add_job(self, pipeline_name, interval=60):
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
                'log_level': logging.INFO,
                'log_path': str(log_filename),
            }
        )

        return job.id
 
    def exposed_modify_job(self, job_id, jobstore=None, **changes):
        return self._scheduler.modify_job(job_id, jobstore, **changes)

    def exposed_reschedule_job(self, job_id, jobstore=None, trigger=None, **trigger_args):
        return self._scheduler.reschedule_job(job_id, jobstore, trigger, **trigger_args)

    def exposed_pause_job(self, job_id, jobstore=None):
        return self._scheduler.pause_job(job_id, jobstore)

    def exposed_start_job(self, job_id):
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
    
    def exposed_get_job(self, job_id):
        self._logger.info(f"get_job({job_id})")
        job = self._scheduler.get_job(job_id)
        return self._marshal_job(job)

    def exposed_list_jobs(self):
        self._logger.info(f"CALL: list_jobs")
        job_list = self._scheduler.get_jobs()
        return [self._marshal_job(job) for job in job_list]

    def exposed_state(self):
        self._logger.debug("CALL: state")
        job_list = self._scheduler.get_jobs()
        state_obj = {
            "run_state": self._scheduler.state,
            "is_running": self._scheduler.running,
            "total_jobs": len(job_list),
            "job_list": [self._marshal_job(job) for job in job_list],
            "cpu_load": psutil.getloadavg(),
        }
        return state_obj

if __name__ == '__main__': 
    imported_logging_config = import_external(Path("../../conf/logging_config.py"), "log_config")
    logging.config.dictConfig(imported_logging_config)
    logger = logging.getLogger("pyrsched.server")

    # patch the set_logging_config method to ust the logging formatter used in our config
    # look for the handler named "default" in the handler list. There is no dict lookup though.
    default_handler = next((handler for handler in logging.getLogger("pyrsched").handlers if handler.get_name() == "default"), None)

    if default_handler:
        import pypyr.log.logger 
        # we won't restore the old function, no need to save it.
        # old_set_logging_config = pypyr.log.logger.set_logging_config

        def new_set_logging_config(log_level, handlers):
            pass
            logging.basicConfig(
                format=default_handler.formatter._fmt,
                # datefmt='%Y-%m-%d %H:%M:%S',
                level=log_level,
                handlers=handlers)
        pypyr.log.logger.set_logging_config = new_set_logging_config
    # done patching, pypyr now uses our own log format

    logger.info("starting scheduler")
    server = ServerWrapper()
    try:
        server.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        logger.info("shutting down scheduler.")
        server.shutdown()
        logger.info("scheduler shutdown complete.")




# def main(args):  # pragma: no cover
#     try:
#         import coloredlogs
#         coloredlogs.install()
#     except ImportError:
#         pass

#     config_from_args = getattr(args, "config", None)
#     if config_from_args:
#         config_file = Path(config_from_args)
#     else:
#         config_file = path = (
#             Path(os.path.abspath(__file__)).parent
#             / PYRSCHED_DEFAULTS["config"]["config"]
#         )

#     # startServer(config_file.resolve())
#     app = create_app(config_file.resolve(), args=args)
#     app.run(
#         debug=app.app.iniconfig.get("flask", "debug").upper() == "TRUE",
#         host=app.app.iniconfig.get("flask", "host"),
#         port=app.app.iniconfig.get("flask", "port"),
#     )


# def flatten_dict(in_dict):
#     out_dict = dict()
#     for section in in_dict:
#         for k, v in in_dict[section].items():
#             out_dict[k] = v
#     return out_dict


# class FakeDefaultsHelpFormatter(argparse.HelpFormatter):
#     fake_defaults = flatten_dict(PYRSCHED_DEFAULTS)

#     def _get_help_string(self, action):
#         help = action.help
#         if "%(default)" not in action.help:
#             if action.dest in self.fake_defaults:
#                 help += f" (default: {self.fake_defaults[action.dest]})."
#         return help


# def create_parser():
#     parser = argparse.ArgumentParser(
#         prog="pyrsched",
#         formatter_class=FakeDefaultsHelpFormatter,  # ThreeQuarterWidthDefaultsHelpFormatter,
#         argument_default=None,
#         description="pypyr-scheduler, the pypyr scheduler. All options except the configuration part can be "
#         "overridden in the configuration file.",
#     )

#     # config
#     config_group = parser.add_argument_group("Configuration")
#     config_group.add_argument(
#         "-c", "--config", metavar="CONFIG", help="Configuration file"
#     )
#     config_group.add_argument(
#         "-s",
#         "--show-config",
#         action="store_true",
#         help="Show effective configuration and exit",
#     )
#     config_group.add_argument(
#         "--json",
#         action="store_true",
#         help="Print config in json instead of a human readable "
#         "format. This is only used if the --show-config flag is set",
#     )
#     config_group.add_argument(
#         "-sc",
#         "--scheduler-config",
#         metavar="SCHEDULERCONF",
#         help="Scheduler configuration file",
#     )
#     config_group.add_argument(
#         "--spec-dir", metavar="SPECDIR", help="Connexion specification directory"
#     )

#     # log
#     log_group = parser.add_argument_group(
#         "Logging", description="Control logging. Section [logging] in .ini"
#     )
#     log_group.add_argument(
#         "-l",
#         "--log-level",
#         metavar="LEVEL",
#         type=str,
#         help="Main log level, as log-level string (i.e.: 'INFO', 'DEBUG')",
#     )
#     log_group.add_argument(
#         "-lp",
#         "--log-path",
#         metavar="LOGPATH",
#         help="Log path. Relative to the program directory or absolute",
#     )
#     log_group.add_argument(
#         "-lc",
#         "--log-config",
#         metavar="LOGCONFIG",
#         help="Python module which contains the log configuration",
#     )

#     # pipelines
#     pipeline_group = parser.add_argument_group(
#         "Pipelines",
#         description="Control how pipelines are managed. " "Section [pipelines] in .ini",
#     )
#     pipeline_group.add_argument(
#         "--enable-upload",
#         action="store_true",
#         help="Activate the pipeline file server. This can be useful if you don't want to provide your own",
#     )

#     pipeline_group.add_argument(
#         "-p",
#         "--pipeline-dir",
#         metavar="PIPELINE_PATH",
#         help="Pipeline upload directory. Relative to the program directory or absolute",
#     )

#     api_group = parser.add_argument_group(
#         "API",
#         description="Control the API endpoint. These options are basically forwarded to the underlying Flask server. "
#         "Section [flask] in .ini. Note that these values may be overridden by a production server loke uwsgi.",
#     )
#     api_group.add_argument(
#         "--host", metavar="HOST", help="The host interface to bind on"
#     )
#     api_group.add_argument("--port", metavar="PORT", help="The port to listen to")
#     api_group.add_argument(
#         "--debug", metavar="DEBUG", help="Include debugging information"
#     )

#     return parser


# if __name__ == "__main__":  # pragma: no cover
#     parser = create_parser()
#     main(parser.parse_args())
