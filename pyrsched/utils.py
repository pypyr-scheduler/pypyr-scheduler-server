import logging
from pathlib import Path
from datetime import timedelta

from flask import make_response, current_app
from werkzeug.utils import secure_filename
from connexion.apps.flask_app import FlaskJSONEncoder


logger = logging.getLogger(__name__)


def empty_response():
    res = make_response('', 204)
    res.headers = {}
    res.content_length = 0
    return res


def make_target_filename(filename):
    filename = secure_filename(filename)
    base_path = Path(current_app.iniconfig.get('pipelines', 'base_path'))
    return (base_path / filename).resolve()


def find_job(job_identifier):
    """Finds a Job. 

    The job_identifier is either a job-id (uuid) or the job name.
    The list of jobs is searched twice, forst for id and if there was no job found for
    the name. 
    """ 
    jobs = current_app.scheduler.get_jobs()
    logger.info(f'found jobs: {jobs}')
    for job in jobs:
        if job.id == job_identifier:
            return job
    for job in jobs:
        if job.name == job_identifier:
            return job     
    return None       
    

class JobEncoder(FlaskJSONEncoder):
    """
    JSONEncoder for `apscheduler.job.Job` and `apscheduler.triggers.interval.IntervalTrigger` class.

    This encoder uses the `__getstate__` internal method of these classes to
    generate a json serializable data structure, mainly to output it over the REST-API.

    It also uses sensible string represenations for `pytz.tzfile.DstTzInfo`,
    `datetime.datetime` and `datetime.timedelta`.
    """
    def default(self, o):
        # apscheduler objects tend to store its internal state in a __state__
        # attribute, which is accessible through the __getstate__()-method.
        if hasattr(o, '__getstate__'):
            return o.__getstate__()

        # pytz timezones. Instead of checking the type, check if the `zone`-attribute
        # is present.
        # Special case: UTC is a singletone, the class and object are equivalent. And
        # it's located in another package, so...
        if hasattr(o, 'zone'):
            return o.zone

        # timedelta is not serialized by connexion's serializer...
        if isinstance(o, timedelta):
            return str(o)

        # job classes have a reference to their job functions
        # use this if problems with that occur.
        # if isinstance(o, ModuleType):
        #     return o.__name__

        return FlaskJSONEncoder.default(self, o)
