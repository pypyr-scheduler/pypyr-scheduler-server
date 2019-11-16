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
    base_path = current_app.config.get("PYRSCHED_PIPELINES_BASE_PATH", current_app.instance_path)
    return (Path(base_path) / filename).resolve()