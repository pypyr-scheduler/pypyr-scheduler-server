import logging
from pathlib import Path

import connexion
from flask_ini import FlaskIni
from apscheduler.schedulers.background import BackgroundScheduler

from .utils import JobEncoder


def create_app(config_file, **api_extra_args):
    logging.basicConfig(level=logging.INFO)

    # We have to turn off response validation for now until
    # zalando/connexion/#401 is fixed
    api_extra_args['validate_responses'] = False

    _app = connexion.FlaskApp(__name__, specification_dir='../conf/')
    _app.add_api('pypyr-scheduler.v1.yaml', **api_extra_args)

    with _app.app.app_context():
        logging.info(f'trying to load {config_file}')
        _app.app.json_encoder = JobEncoder

        _app.app.iniconfig = FlaskIni()
        _app.app.iniconfig.read(config_file)

        # make sure the log path exists
        log_path = Path(_app.app.iniconfig.get('pipelines', 'log_path')).resolve()
        if not log_path.exists():
            log_path.mkdir()

        _app.app.scheduler = BackgroundScheduler()
        _app.app.scheduler.start()

    return _app
