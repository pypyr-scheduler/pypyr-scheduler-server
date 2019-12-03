import os
import argparse
import logging
from pathlib import Path

from apextras.formatter import ThreeQuarterWidthDefaultsHelpFormatter

from .app import create_app, PYRSCHED_DEFAULTS


def main(args):  # pragma: no cover   
    path = Path(os.path.abspath(__file__)).parent.parent
    config_file = path / PYRSCHED_DEFAULTS['config']['config']
    # config_file = ### VALUE FROM COMMAND LINE ###
    app = create_app(config_file.resolve(), args=args)
    app.run(
        debug = app.app.iniconfig.get('flask', 'debug').upper() == "TRUE",
        host = app.app.iniconfig.get('flask', 'host'),
        port = app.app.iniconfig.get('flask', 'port'),
    )


def flatten_dict(in_dict):
    out_dict = dict()
    for section in in_dict:
        for k, v in in_dict[section].items():
            out_dict[k] = v
    return out_dict


class FakeDefaultsHelpFormatter(argparse.HelpFormatter):
    fake_defaults = flatten_dict(PYRSCHED_DEFAULTS)

    def _get_help_string(self, action):
        help = action.help
        if '%(default)' not in action.help:
            if action.dest in self.fake_defaults:
                help += f' (default: {self.fake_defaults[action.dest]}).'
        return help


def create_parser():
    parser = argparse.ArgumentParser(
        prog="pyrsched",
        formatter_class=FakeDefaultsHelpFormatter,  # ThreeQuarterWidthDefaultsHelpFormatter,
        argument_default=None,
        description="pypyr-scheduler, the pypyr scheduler. All options except the configuration part can be "
        "overridden in the configuration file."
    )

    # config
    config_group = parser.add_argument_group("Configuration")
    config_group.add_argument(
        "-c", "--config", metavar="CONFIG", help="Configuration file"
    )
    config_group.add_argument(
        "-s", "--show-config", action="store_true", help="Show effective configuration and exit"
    )
    config_group.add_argument(
        "--json", action="store_true", help="Print config in json instead of a human readable "
        "format. This is only used if the --show-config flag is set"
    )

    # log
    log_group = parser.add_argument_group("Logging", description="Control logging. Section [logging] in .ini")
    log_group.add_argument(
        "-l",
        "--log-level",
        metavar="LEVEL",
        type=str,
        help="Main log level, as log-level string (i.e.: 'INFO', 'DEBUG')",
    )
    log_group.add_argument(
        "-lp",
        "--log-path",
        metavar="LOGPATH",
        help="Log path. Relative to the program directory or absolute",
    )
    log_group.add_argument(
        "-lc",
        "--log-config",
        metavar="LOGCONFIG",
        help="Python module which contains the log configuration",
    )

    # pipelines
    pipeline_group = parser.add_argument_group("Pipelines", description="Control how pipelines are managed. "
                                               "Section [pipelines] in .ini")
    pipeline_group.add_argument(
        "--enable-upload",
        action="store_true",
        help="Activate the pipeline file server. This can be useful if you don't want to provide your own",
    )

    pipeline_group.add_argument(
        "-p",
        "--pipeline-dir",
        metavar="PIPELINE_PATH",
        help="Pipeline upload directory. Relative to the program directory or absolute",
    )

    api_group = parser.add_argument_group(
        "API",
        description="Control the API endpoint. These options are basically forwarded to the underlying Flask server. "
                    "Section [flask] in .ini",
    )
    api_group.add_argument("--host", metavar="HOST", help="The host interface to bind on")
    api_group.add_argument("--port", metavar="PORT", help="The port to listen to")
    api_group.add_argument("--debug", metavar="DEBUG", help="Include debugging information")

    return parser

if __name__ == "__main__":  # pragma: no cover    
    parser = create_parser()
    main(parser.parse_args())
