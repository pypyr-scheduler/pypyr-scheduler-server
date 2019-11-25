import os
import argparse
import logging
from pathlib import Path

from apextras.formatter import ThreeQuarterWidthDefaultsHelpFormatter

from .app import create_app


def main(args):     
    path = Path(os.path.abspath(__file__)).parent.parent
    config_file = path / args.config
    app = create_app(config_file.resolve(), args=args)
    app.run(
        debug = app.app.iniconfig.get('flask', 'debug').upper() == "TRUE",
        host = app.app.iniconfig.get('flask', 'host'),
        port = app.app.iniconfig.get('flask', 'port'),
    )


def loglevel_param(value):
    """Try to make a valid loglevel out of the given input.

    If it is an `int`, return it.
    If not, try to convert the value using the logging module.
    If this is also not possible, raise an `argparse.ArgumentTypeError`.

    >>> import logging
    >>> loglevel_param(10)
    10
    >>> loglevel_param('info')
    20
    >>> loglevel_param('INFO')
    20
    >>> loglevel_param("I'm an obscure loglevel, yo'll never find me")  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    argparse.ArgumentTypeError: ...
    """
    if isinstance(value, int):
        return value
    try:
        loglevel = getattr(logging, str(value).upper())
    except AttributeError:
        raise argparse.ArgumentTypeError(f'The value "{value}" could not be mapped to a log level.')
    return loglevel


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="pyrsched",
        formatter_class=ThreeQuarterWidthDefaultsHelpFormatter,
        description="pypyr-scheduler, the pypyr scheduler. All options except the configuration part can be "
        "overridden in the configuration file."
    )

    # config
    config_group = parser.add_argument_group("Configuration")
    config_group.add_argument(
        "-c", "--config", metavar="CONFIG", default="conf/pyrsched.ini", help="Configuration file"
    )
    config_group.add_argument(
        "-s", "--show-config", action="store_true", default=False, help="Show effective configuration and exit"
    )
    config_group.add_argument(
        "--json", action="store_true", default=False, help="Print config in json instead of a human readable "
        "format. This is only used if the --show-config flag is set"
    )

    # log
    log_group = parser.add_argument_group("Logging", description="Control logging. Section [logging] in .ini")
    log_group.add_argument(
        "-l",
        "--log-level",
        metavar="LEVEL",
        default=logging.getLevelName(logging.INFO),
        type=loglevel_param,
        help="Main log level, either as log-level string (i.e.: 'INFO', 'debug') or integer log level",
    )
    log_group.add_argument(
        "-lp",
        "--log-path",
        metavar="LOGPATH",
        default="logs",
        help="Log path. Relative to the program directory or absolute",
    )

    # pipelines
    pipeline_group = parser.add_argument_group("Pipelines", description="Control how pipelines are managed. "
                                               "Section [pipelines] in .ini")
    pipeline_group.add_argument(
        "--disable-upload",
        default=False,
        action="store_true",
        help="Disable the pipeline file server. This can be useful if you want to provide your own. "
             "Just set --pipeline-dir to your upload directory",
    )

    pipeline_group.add_argument(
        "-p",
        "--pipeline-dir",
        metavar="PIPELINE_PATH",
        default="pipelines",
        help="Pipeline upload directory. Relative to the program directory or absolute",
    )

    api_group = parser.add_argument_group(
        "API",
        description="Control the API endpoint. These options are basically forwarded to the underlying Flask server. "
                    "Section [flask] in .ini",
    )
    api_group.add_argument("--host", metavar="HOST", default="0.0.0.0", help="The host interface to bind on")
    api_group.add_argument("--port", metavar="PORT", default=5000, help="The port to listen to")
    api_group.add_argument("--debug", metavar="DEBUG", default=False, help="Include debugging information")

    main(parser.parse_args())
