import logging
import uuid

from flask import current_app
from pypyr.pipelinerunner import main as pipeline_runner

from ..utils import make_target_filename

logger = logging.getLogger(__name__)


def make_job_function(pipeline_name):
    with current_app.app_context():
        base_path = current_app.iniconfig.get('pipelines', 'base_path')
    if pipeline_name.endswith('.yaml'):
        pipeline_name = pipeline_name[:-5]

    def run_pipeline():
        pipeline_runner(
            pipeline_name,
            pipeline_context_input="",
            working_dir=base_path,
            log_level=logging.INFO,
            log_path=f'D:\\Projects\\pypyr-scheduler\\logs\\{pipeline_name}.log'  # current_app.iniconfig.get('pipelines', 'base_path'),
        )

    return run_pipeline


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
    job = scheduler.add_job(
        make_job_function(pipeline_name),
        id=str(uuid.uuid4()),
        name=pipeline_name,
    )
    logger.info(f'created job {job.name}')
    # ToDo: Modify the JSONEncoder to make it able to encode Jobs ans Triggers.
    # @see: https://connexion.readthedocs.io/en/latest/response.html#customizing-json-encoder
    return {}
    # return job


def delete(job_identifier):
    return {}


def change(job_identifier):
    return {}
