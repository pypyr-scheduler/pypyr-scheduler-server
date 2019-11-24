import os
import argparse
import logging
from pathlib import Path
from apextras.formatter import ThreeQuarterWidthDefaultsHelpFormatter

from .app import create_app


def main(args):
    print(args)
    path = Path(os.path.abspath(__file__)).parent
    config_file = path / ".." / "conf" / "pyrsched.dev.ini"
    app = create_app(config_file.resolve())
    app.run(port=8080)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="pyrsched",
        formatter_class=ThreeQuarterWidthDefaultsHelpFormatter,
        description="pypyr-scheduler, the pypyr scheduler.",
    )

    # config
    config_group = parser.add_argument_group("Configuration")
    config_group.add_argument(
        "-c", "--config", metavar="CONFIG", default="conf/pyrsched.ini", help="Configuration file"
    )
    config_group.add_argument(
        "-s", "--show-config", action="store_true", default=False, help="Show configuration and exit"
    )

    # log
    log_group = parser.add_argument_group(
        "Logging", description="Logging options, these can be overridden in the ini-file."
    )
    log_group.add_argument(
        "-l",
        "--log-level",
        metavar="LEVEL",
        default=logging.getLevelName(logging.INFO),
        type=int,
        help="Main log level",
    )
    log_group.add_argument(
        "-lp",
        "--log-path",
        metavar="LOGPATH",
        default="logs",
        help="Log path. Relative to the program directory or absolute.",
    )

    # pipelines
    pipeline_group = parser.add_argument_group("Pipelines", description="Control how pipelines are managed.")
    pipeline_group.add_argument(
        "-p",
        "--pipeline-dir",
        metavar="PIPELINE_PATH",
        default="pipelines",
        help="Pipeline upload directory. Relative to the program directory or absolute.",
    )

    args = parser.parse_args()
    main(args)
