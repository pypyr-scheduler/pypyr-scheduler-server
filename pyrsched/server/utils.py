import logging
import sys
import importlib
import threading 

from pathlib import Path

from . import logger as pyrsched_logger

logger = pyrsched_logger.getChild('import')

def resolve_module_file(file_name):
    module_file = Path(file_name)
    if not module_file.is_absolute():
        module_file = Path(__file__).parent.parent.parent / module_file
    if not module_file.exists():
        raise FileNotFoundError(f"{module_file} not found.")
    return module_file

def check_search_path(module_file):
    module_path = module_file.parent.resolve()
    if not str(module_path) in sys.path:
        logger.info(f'{module_path} not in sys.path, adding it')
        sys.path.insert(0, str(module_path))

def import_external_attribute(file_name, attribute_name):  # pragma: no cover; this is not used
    imported_module = import_external(file_name)
    logger.info(f'importing {attribute_name} from {imported_module}')
    attribute = getattr(imported_module, attribute_name)
    return attribute

def import_external(file_name):
    logger.info(f'importing {file_name}')
    module_file = resolve_module_file(file_name)
    check_search_path(module_file)
    imported_module = importlib.import_module(module_file.stem)
    return imported_module


class PipelineLoggingContext:
    def __init__(self, logger, loglevel=None, handler=None):
        self.logger = logger
        self.handler = handler
        self.loglevel = loglevel
        self.lock = threading.Lock()

    def __enter__(self):
        self.lock.acquire()
        if self.loglevel is not None:
            self._old_level = self.logger.level
            self.logger.setLevel(self.loglevel)
        if self.handler:
            self.logger.addHandler(self.handler)

    def __exit__(self, et, ev, tb):
        self.lock.release()
        if self.loglevel is not None:
            self.logger.setLevel(self._old_level)
        if self.handler:
            self.logger.removeHandler(self.handler)