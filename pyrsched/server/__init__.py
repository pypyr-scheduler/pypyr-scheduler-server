import logging
import logging.config

from pathlib import Path

from .utils import import_external

def _monkeypatch_pypyr_logging(derive_from: str, handler_name: str):
    """ Patch the set_logging_config method to use a the logging formatter used in a specified logger.

        This looks for a handler named "handler_name" at the logger "derive_from".
        If it is able to find one, the log format of that handler is copied to the
        pypyr logger.
        
        If there are multiple handlers, the first hit is chosen. This behaviour could be
        changed by iterating over the whole handler list and not stopping at the first match
        (replace ``next(...)`` below with a list comprehension).

        This action is necessary because pypyr provides no means of changing
        its log format at the moment.

        Finally pypyr is persuaded to use that new logger by replacing the function
        ``pypyr.log.logger.set_logging_config``.

        :param str derive_from: Name of the logger which is used as source.
        :param str handler_name: Name of the Handler on ``derive_from`` where the log format is taken from.
    """

    # look for the handler named "default" in the handler list. There is no dict lookup though.
    default_handler = next((
        handler for handler in logging.getLogger(derive_from).handlers if handler.get_name() == handler_name
    ), None)

    if default_handler:
        import pypyr.log.logger 
        # we won't restore the old function, no need to save it.
        # old_set_logging_config = pypyr.log.logger.set_logging_config

        def new_set_logging_config(log_level, handlers):
            pass
            logging.basicConfig(
                format=default_handler.formatter._fmt,
                # datefmt='%Y-%m-%d %H:%M:%S',
                level=log_level,
                handlers=handlers)
        pypyr.log.logger.set_logging_config = new_set_logging_config

    # done patching, pypyr now uses our own log format

imported_logging_config = import_external(Path("../../conf/logging_config.py"), "log_config")
logging.config.dictConfig(imported_logging_config)
logger = logging.getLogger("pyrsched.server")

_monkeypatch_pypyr_logging("pyrsched", "default")