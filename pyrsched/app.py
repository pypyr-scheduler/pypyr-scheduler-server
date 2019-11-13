import logging 
import connexion


def create_app(config_object=None, **api_extra_args):
    logging.basicConfig(level=logging.INFO)

    api_extra_args['validate_responses'] = True

    app = connexion.FlaskApp(__name__, specification_dir='../conf/')
    app.add_api('pypyr-scheduler.v1.yaml', **api_extra_args)    

    return app

