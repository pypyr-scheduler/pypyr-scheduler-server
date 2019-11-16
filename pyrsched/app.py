import logging
import os
import configparser

import connexion

from flask import g

def create_app(config_file, **api_extra_args):
    logging.basicConfig(level=logging.INFO)
    
    config = configparser.ConfigParser()
    logging.info(f"trying to load {config_file}")
    config.read(config_file)

    path = Path(os.path.abspath(__file__)).parent

    api_extra_args['validate_responses'] = False

    _app = connexion.FlaskApp(__name__, specification_dir='../conf/')
    _app.add_api('pypyr-scheduler.v1.yaml', **api_extra_args)

    _app.app.config.from_mapping({
        'PYRSCHED_PIPELINES_BASE_PATH': str((path / ".." / "pipelines_test").resolve()),
        'ENV': 'development',
        'DEBUG': True,
    })

    _app.app.scheduler = {'key': 'value'}

    # _app.app.after_request(after_request)

    return _app

# def after_request(res):
#     logging.info("after request")
#     res.direct_passthrough = False
#     return res