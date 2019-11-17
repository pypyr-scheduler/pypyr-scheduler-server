import logging
from flask import current_app

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


def new(pipeline_id, interval):
    print(f'POST /jobs, pipeline_id:{pipeline_id}, interval:{interval}')
    return {}


def create(pipeline_name, interval):
    logger.info(f'POST /jobs/{pipeline_name}/{interval}')

    if interval <= 0:
        return "Interval must be greater than 0", 400

    pipeline_file = make_target_filename(pipeline_name)
    if not pipeline_file.exists():
        return "Pipeline not found", 404

    # create pipeline on the scheduler
    scheduler = current_app.scheduler
    print(scheduler)


def delete(job_identifier):
    return {}


def change(job_identifier):
    return {}
