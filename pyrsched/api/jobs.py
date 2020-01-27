import logging
import uuid

from pathlib import Path

from flask import current_app
from pypyr.pipelinerunner import main as pipeline_runner
from apscheduler.triggers.interval import IntervalTrigger

from ..utils import empty_response, make_target_filename, find_job

logger = logging.getLogger(__name__)


def get_one(job_identifier):
    logger.info(f'GET /jobs/{job_identifier}')
    job = find_job(job_identifier)
    if not job:
        return 'Job not found', 404
    return job


def get_all():
    logger.info('GET /jobs')
    #return current_app.scheduler.get_jobs()
    return current_app.scheduler.root.get_jobs()

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
    base_path = current_app.iniconfig.get('pipelines', 'base_path')
    log_path = current_app.iniconfig.get('pipelines', 'log_path')
    log_filename = Path(log_path) / f'{pipeline_name}.log'

    # TODO: add job paused (see: https://github.com/agronholm/apscheduler/issues/68)
#    job = current_app.scheduler.add_job(
    job = current_app.scheduler.root.add_job(
        pipeline_runner,
        id=str(uuid.uuid4()),
        name=pipeline_name,
        trigger=IntervalTrigger(seconds=interval),
        next_run_time=None,
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
    logger.info(f'DELETE /jobs/{job_identifier}')
    job = find_job(job_identifier)
    if not job:
        return 'Job not found', 404
    current_app.scheduler.remove_job(job.id)      
    return empty_response()


def change(job_identifier, pipeline_name, interval):
    logger.info(f'PUT /jobs/{job_identifier}/{pipeline_name}/{interval}')
    job = find_job(job_identifier)
    if not job:
        return 'Job not found', 404

    if pipeline_name.endswith('.yaml'):
        pipeline_name = pipeline_name[:-5]

    base_path = current_app.iniconfig.get('pipelines', 'base_path')
    log_path = current_app.iniconfig.get('pipelines', 'log_path')
    log_filename = Path(log_path) / f'{pipeline_name}.log'
            
    current_app.scheduler.modify_job(
        job.id, 
        name=pipeline_name,
        trigger=IntervalTrigger(seconds=interval),
        # next_run_time=None,  # do not modify job execution state
        args=[pipeline_name, ],
        kwargs={
            'pipeline_context_input': '',
            'working_dir': base_path,
            'log_level': logging.INFO,
            'log_path': str(log_filename),
        }        
    )
    return job
