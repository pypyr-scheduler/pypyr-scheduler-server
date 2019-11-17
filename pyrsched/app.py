import logging

import connexion
from flask_ini import FlaskIni
from apscheduler.schedulers.background import BackgroundScheduler


def create_app(config_file, **api_extra_args):
    logging.basicConfig(level=logging.INFO)

    # We have to turn off response validation for now until
    # zalando/connexion/#401 is fixed
    api_extra_args["validate_responses"] = False

    _app = connexion.FlaskApp(__name__, specification_dir="../conf/")
    _app.add_api("pypyr-scheduler.v1.yaml", **api_extra_args)

    with _app.app.app_context():
        logging.info(f"trying to load {config_file}")
        _app.app.iniconfig = FlaskIni()
        _app.app.iniconfig.read(config_file)

        _app.app.scheduler = BackgroundScheduler()

    # _app.app.after_request(after_request)

    return _app
