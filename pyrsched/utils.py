from pathlib import Path

from flask import make_response, current_app
from werkzeug.utils import secure_filename
from connexion.apps.flask_app import FlaskJSONEncoder
from apscheduler.job import Job
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from datetime import datetime, timedelta
from pytz.tzfile import DstTzInfo
from types import ModuleType

def empty_response():
    res = make_response('', 204)
    res.headers = {}
    res.content_length = 0
    return res


def make_target_filename(filename):
    filename = secure_filename(filename)
    base_path = Path(current_app.iniconfig.get('pipelines', 'base_path'))
    return (base_path / filename).resolve()


class JobEncoder(FlaskJSONEncoder):
    """
    JSONEncoder for `apscheduler.job.Job` and `apscheduler.triggers.interval.IntervalTrigger` class.

    This encoder uses the `__getstate__` internal method of these classes to
    generate a json serializable data structure, mainly to output it over the REST-API.

    It also uses sensible string represenations for `pytz.tzfile.DstTzInfo`,
    `datetime.datetime` and `datetime.timedelta`.
    """
    def default(self, o):
        if isinstance(o, (Job, IntervalTrigger, DateTrigger)):
            return o.__getstate__()

        if isinstance(o, DstTzInfo):
            return o.zone

        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, timedelta):
            return str(o)

        if isinstance(o, ModuleType):
            # if o.__name__ == "settings":
            return o.__name__

        return FlaskJSONEncoder.default(self, o)
