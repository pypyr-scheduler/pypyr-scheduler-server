import logging

from ..utils import find_job, empty_response

logger = logging.getLogger(__name__)

def status(job_identifier):
    logging.info(f'GET /jobs/{job_identifier}/execution')
    job = find_job(job_identifier)
    if not job:
        return "Job not found", 404
    return job


def start(job_identifier):
    logging.info(f'POST /jobs/{job_identifier}/execution')
    job = find_job(job_identifier)
    if not job:
        return "Job not found", 404
    job.resume()
    return job  


def pause(job_identifier):
    logging.info(f'DELETE /jobs/{job_identifier}/execution')
    job = find_job(job_identifier)
    if not job:
        return "Job not found", 404
    job.pause()
    return empty_response()    
