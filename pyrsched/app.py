import sys
import logging
import logging.config
import argparse
import configparser
import importlib
from copy import deepcopy
from pathlib import Path

import connexion
from flask_ini import FlaskIni
from apscheduler.schedulers.background import BackgroundScheduler

from .utils import JobEncoder


PYRSCHED_DEFAULTS = {
    'config': {
        'config': 'conf/pyrsched.ini',
        'scheduler_config': 'conf/scheduler_config.py',
        'show_config': False,
        'json': False,
    },
    'logging': {
        'log_level': 'DEBUG',
        'log_path': 'logs',
        'log_config': 'conf/logging_config.py', 
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
            cli_value = getattr(args, item_name, None)
            try:
                ini_value = config.get(section, item_name)
            except configparser.NoOptionError as e:
                logger.debug(f'{section}->{item_name} not in .ini, using default value {default_value} or value from command line ({cli_value})')
                pass  # we'll use the default instead
            
            
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
    logger.info(f'app startup: {config_file}, {args}, {api_extra_args}')

    if not Path(config_file).resolve().exists():
        raise FileNotFoundError(f'ini file not found: {config_file}')

    # We have to turn off response validation for now until
    # zalando/connexion/#401 is fixed
    api_extra_args['validate_responses'] = False

    # create the API endpoints, either with or without pipeline upload
    _app = connexion.FlaskApp(__name__, specification_dir='../conf/')    

    # load configuration and interpolate it with command line args
    with _app.app.app_context():
        logger.info(f'trying to load {config_file}')
        _app.app.json_encoder = JobEncoder

        _app.app.iniconfig = FlaskIni()
        _app.app.iniconfig.read(config_file)
        
    override_defaults(_app.app.iniconfig, args, PYRSCHED_DEFAULTS)

    logging.root.setLevel(_app.app.iniconfig.get('logging', 'log_level'))
    
    # import logging config
    log_config_path = _app.app.iniconfig.get("logging", "log_config")
    imported_logging_config = import_external(log_config_path, "config")
    logging.config.dictConfig(imported_logging_config)

    if _app.app.iniconfig.get("config", "show_config").lower() == "true":
        handle_config_output(_app.app.iniconfig)
        
    # make sure the log path exists
    log_path = Path(_app.app.iniconfig.get('pipelines', 'log_path')).resolve()
    logger.info(f'logpath: {log_path}')    
    if not log_path.exists():
        logging.debug('logpath does not exist. creating.')
        log_path.mkdir()

    # create and configure scheduler
    config_path = Path(_app.app.iniconfig.get("config", "scheduler_config")).resolve()   
    imported_scheduler_config = import_external(config_path, "config")
    # apscheduler .pop()s values from this, so the original has to be preserved
    scheduler_config = deepcopy(imported_scheduler_config)  
    logger.info(scheduler_config)

    _app.app.scheduler = BackgroundScheduler(scheduler_config)    
    _app.app.scheduler.start()

    # create api
    spec_filename = 'pypyr-scheduler.v1.without-pipelines.yaml'
    if _app.app.iniconfig.get("pipelines", "enable_upload"):
        spec_filename = 'pypyr-scheduler.v1.yaml'
    logger.info(f'loading API spec {spec_filename}')
    _app.add_api(spec_filename, **api_extra_args)

    return _app

def import_external(file_name, attribute_name):
    logger = logging.getLogger('pyrsched.import')
    logger.info(f'importing {attribute_name} from {file_name}')
    module_file = Path(file_name).resolve()
    if not module_file.exists():
        raise FileNotFoundError(f"{module_file} not found.")
    module_path = module_file.parent
    if not module_path in sys.path:
        logger.info(f'{module_path} not in sys.path, adding it')
        sys.path.insert(0, str(module_path))

    imported_module = importlib.import_module(module_file.stem)
    attribute = getattr(imported_module, attribute_name)
    return attribute
