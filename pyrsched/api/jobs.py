import logging
import uuid

from pathlib import Path

from flask import current_app
from pypyr.pipelinerunner import main as pipeline_runner
from apscheduler.triggers.interval import IntervalTrigger

from ..utils import make_target_filename

logger = logging.getLogger(__name__)


def get_one(job_identifier):
    """
    Use job-identifier to search in both id and name
    """
    return {}


def get_all():
    print('GET /jobs')
    return {}


def create(pipeline_name, interval):
    logger.info(f'POST /jobs/{pipeline_name}/{interval}')

    if interval <= 0:
        return 'Interval must be greater than 0', 400

    pipeline_file = make_target_filename(pipeline_name)
    if not pipeline_file.exists():
        return 'Pipeline not found', 404

    if pipeline_name.endswith('.yaml'):
        pipeline_name = pipeline_name[:-5]

    # create pipeline on the scheduler
    scheduler = current_app.scheduler
    base_path = current_app.iniconfig.get('pipelines', 'base_path')
    log_path = current_app.iniconfig.get('pipelines', 'log_path')
    log_filename = Path(log_path) / f'{pipeline_name}.log'

    # TODO: add job paused (see: https://github.com/agronholm/apscheduler/issues/68)
    job = scheduler.add_job(
        pipeline_runner,
        id=str(uuid.uuid4()),
        name=pipeline_name,
        trigger=IntervalTrigger(seconds=interval),
        args=[pipeline_name, ],
        kwargs={
            'pipeline_context_input': '',
            'working_dir': base_path,
            'log_level': logging.INFO,
            'log_path': str(log_filename),
        }
    )
    logger.info(f'created job {job.name}')
    return job, 201


def delete(job_identifier):
    return {}


def change(job_identifier):
    return {}
