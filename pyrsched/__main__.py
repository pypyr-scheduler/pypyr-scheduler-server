import os
import shutil
import argparse
import logging
from pathlib import Path


from .app import create_app


def main(args):
    print(args)
    path = Path(os.path.abspath(__file__)).parent
    config_file = path / ".." / "conf" / "pyrsched.dev.ini"
    app = create_app(config_file.resolve())
    app.run(port=8080)


class WideDefaulsHelpFormatter(argparse.HelpFormatter):
    """
    HelpFormattet which tries to use a given amount of the terminal width.

    The maximum line length is determines by the class attribute ``percentage_of_line_length``.
    This defaults to the full width (1.0). Override this class and set your own percentage.
    Add more formatting features by adding more superclasses to your formatter:

    >>> import argparse
    >>> class ThreeQuarterWidthDefaultsHelpFormatter(WideDefaulsHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    ...     percentage_of_line_length = 0.75
    >>> parser = argparse.ArgumentParser(formatter_class=ThreeQuarterWidthDefaultsHelpFormatter)
    >>> arg = parser.add_argument(
    ...     "-l", "-long_help",
    ...     help="This is a really long help message but should be displayed in one line."
    ... )
    >>> parser.parse_args(["-h"])  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    SystemExit: 0
    usage: [-h] [-l L]

    optional arguments:
    -h, --help          show this help message and exit
    -l L, -long_help L  This is a really long help message but should be displayed in one line. (default: None)

    This is an example if the line length exceeds the maximum of 100%:
    >>> import argparse
    >>> class TooWideHelpFormatter(WideDefaulsHelpFormatter):
    ...     percentage_of_line_length = 1.5
    >>> parser = argparse.ArgumentParser(formatter_class=TooWideHelpFormatter)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: ValueError: Line length percentage can't exceed 1.0 (full width; actual value: 1.5)
    """

    percentage_of_line_length = 1.0

    def __init__(self, *args, **kwargs):
        if self.percentage_of_line_length > 1.0:
            raise ValueError(
                f"Line length percentage can't exceed 1.0 (full width; actual value: {self.percentage_of_line_length})"
            )
        max_columns = int(shutil.get_terminal_size().columns * self.percentage_of_line_length)
        super().__init__(max_help_position=min(60, int(max_columns / 3)), width=max_columns, *args, **kwargs)


class ThreeQuarterWidthDefaultsHelpFormatter(WideDefaulsHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    percentage_of_line_length = 0.75


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
