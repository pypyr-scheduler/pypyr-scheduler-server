import sys
import logging
import argparse
import configparser
from pathlib import Path

import connexion
from flask_ini import FlaskIni
from apscheduler.schedulers.background import BackgroundScheduler

from .utils import JobEncoder

CONFIG_MAPPING = {
    'debug': ('flask', 'debug'),
    'disable_upload': ('pipelines', 'disable_upload'),
    'host': ('flask', 'host'),
    'log_level': ('logging', 'log_level'),
    'log_path': ('logging', 'log_path'),
    'pipeline_dir': ('pipelines', 'base_path'),
    'port': ('flask', 'port'),
}


def create_app(config_file, args=argparse.Namespace(show_config=False), **api_extra_args):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('pyrsched')
    # We have to turn off response validation for now until
    # zalando/connexion/#401 is fixed
    api_extra_args['validate_responses'] = False

    _app = connexion.FlaskApp(__name__, specification_dir='../conf/')
    _app.add_api('pypyr-scheduler.v1.yaml', **api_extra_args)

    with _app.app.app_context():
        logger.info(f'trying to load {config_file}')
        _app.app.json_encoder = JobEncoder

        _app.app.iniconfig = config = FlaskIni()
        _app.app.iniconfig.read(config_file)
        
        # override .ini values with command line arguments if they aren't set in the .ini file
        for item_name, item_value in args.__dict__.items():            
            logger.debug(f'parsed from command line args: {item_name}={item_value}')

            try:
                section, entry_name = CONFIG_MAPPING[item_name]
                logger.debug(f'{entry_name} belongs to {section}')
                if not config.has_section(section):
                    config.add_section(section)
                    logger.debug(f'created ini section {section}')
                    
                if not config.has_option(section, entry_name):                    
                    logger.debug(f'setting {section}->{entry_name} to {item_value}')
                    config.set(section, entry_name, str(item_value))

            except KeyError:
                # no value in CONFIG_MAPPING, ignore the entry.
                logger.debug(f'{item_name} not found in mapping, ignoring')
                pass

        if args.show_config:
            if args.json:
                import json
                output = {}
                for section in config.sections():
                    output[section] = {}
                    for item_name in config.options(section):
                        output[section][item_name] = _app.app.iniconfig.get(section, item_name)
                print(json.dumps(output))
            else:
                for section in config.sections():
                    print(f'[{section}]')
                    for item_name in config.options(section):
                        print(f'\t{item_name} = {_app.app.iniconfig.get(section, item_name)}')
            sys.exit(0)

        # make sure the log path exists
        log_path = Path(_app.app.iniconfig.get('pipelines', 'log_path')).resolve()
        logging.info(f'logpath: {log_path}')
        if not log_path.exists():
            logging.debug('logpath does not exist. creating.')
            log_path.mkdir()

        _app.app.scheduler = BackgroundScheduler()
        _app.app.scheduler.start()

    return _app
