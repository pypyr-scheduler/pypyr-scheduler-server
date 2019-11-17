from flask import make_response, current_app
from werkzeug.utils import secure_filename

from pathlib import Path


def empty_response():
    res = make_response('', 204)
    res.headers = {}
    res.content_length = 0
    return res


def make_target_filename(filename):
    filename = secure_filename(filename)
    base_path = Path(current_app.iniconfig.get('pipelines', 'base_path'))
    return (base_path / filename).resolve()
