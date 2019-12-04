import sys
import logging
import logging.config
import argparse
import configparser
import importlib
from pathlib import Path

import connexion
from flask_ini import FlaskIni
from apscheduler.schedulers.background import BackgroundScheduler

from .utils import JobEncoder


PYRSCHED_DEFAULTS = {
    'config': {
        'config': 'conf/pyrsched.dev.ini',
        'scheduler_config': 'conf/scheduler_config.py',
        'show_config': False,
        'json': False,
    },
    'logging': {
        'log_level': 'DEBUG',
        'log_path': 'logs',
        'log_config': 'pyrsched.log.config',
    },
    'pipelines': {
        'enable_upload': False,
        'pipeline_dir': 'pipelines',
    },
    'flask': {
        'host': '0.0.0.0',
        'port': 5000,
        'debug': False,
    },
}


def override_defaults(config, args, defaults):
    # override defaults with .ini values if present
    # override .ini values with command line arguments if they differ from the defaults
    logger = logging.getLogger(__name__)

    for section in defaults:
        for item_name, default_value in defaults[section].items():
            # create section in .ini if it does not exist
            if not config.has_section(section):
                config.add_section(section)

            ini_value = None
            try:
                ini_value = config.get(section, item_name)
            except configparser.NoOptionError as e:
                pass  # we'll use the default instead
            cli_value = getattr(args, item_name, None)
            
            value = default_value
            if ini_value:
                value = ini_value
            if cli_value:
                value = cli_value

            logger.debug(f'{section}->{item_name}: D"{default_value}"->I"{ini_value}"->C"{cli_value}"->[{value}]')
            config.set(section, item_name, str(value))


def handle_config_output(config):
    if config.get("config", "json").lower() == "true":
        import json
        output = {}
        for section in config.sections():
            output[section] = {}
            for item_name in config.options(section):
                output[section][item_name] = config.get(section, item_name)
        print(json.dumps(output))
    else:
        for section in config.sections():
            print(f'[{section}]')
            for item_name in config.options(section):
                print(f'\t{item_name} = {config.get(section, item_name)}')
    sys.exit(0)


def create_app(config_file, args=argparse.Namespace(), **api_extra_args):
    loglevel = getattr(args, "log_level", None) or PYRSCHED_DEFAULTS['logging']['log_level']
    logging.basicConfig(level=loglevel)  # effective log level ist set after config interpolation
    logger = logging.getLogger('pyrsched')
    logger.info(f'app startup: {args}')

    # We have to turn off response validation for now until
    # zalando/connexion/#401 is fixed
    api_extra_args['validate_responses'] = False

    # create the API endpoints, either with or without pipeline upload
    _app = connexion.FlaskApp(__name__, specification_dir='../conf/')    

    # load configuration and interpolate it with command line args
    with _app.app.app_context():
        logger.info(f'trying to load {config_file}')
        _app.app.json_encoder = JobEncoder

        _app.app.iniconfig = config = FlaskIni()
        _app.app.iniconfig.read(config_file)
        
        override_defaults(config, args, PYRSCHED_DEFAULTS)

        logging.root.setLevel(config.get('logging', 'log_level'))
        
        # import logging config
        module_name, attribute = config.get('logging', 'log_config').rsplit('.', maxsplit=1)

        log_config = getattr(importlib.import_module(module_name), attribute)
        logger.debug(f'loading config from {module_name}.{attribute}')
        logging.config.dictConfig(log_config)

    if _app.app.iniconfig.get("config", "show_config").lower() == "true":
        handle_config_output(_app.app.iniconfig)
        
    # make sure the log path exists
    log_path = Path(_app.app.iniconfig.get('pipelines', 'log_path')).resolve()
    logging.info(f'logpath: {log_path}')    
    if not log_path.exists():
        logging.debug('logpath does not exist. creating.')
        log_path.mkdir()

    # create and configure scheduler

    config_path = Path(_app.app.iniconfig.get("config", "scheduler_config")).resolve()
    logging.info(f'scheduler config: {config_path}')
    logging.info(f'adding {config_path.parent} to sys.path')
    sys.path.insert(0, str(config_path.parent))

    scheduler_config = getattr(importlib.import_module(str(config_path.name).rsplit('.', maxsplit=1)[0]), "config")    

    _app.app.scheduler = BackgroundScheduler(scheduler_config)
    _app.app.scheduler.start()

    # create api
    spec_filename = 'pypyr-scheduler.v1.without-pipelines.yaml'
    if _app.app.iniconfig.get("pipelines", "enable_upload"):
        spec_filename = 'pypyr-scheduler.v1.yaml'
    logger.info(f'loading API spec {spec_filename}')
    _app.add_api(spec_filename, **api_extra_args)

    return _app
