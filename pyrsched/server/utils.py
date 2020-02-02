import logging
import sys
import importlib
from pathlib import Path

def import_external(file_name, attribute_name):
    logger = logging.getLogger('pyrsched.import')
    logger.info(f'importing {attribute_name} from {file_name}')
    module_file = Path(file_name)
    if not module_file.is_absolute():
        module_file = Path(__file__).parent / module_file
    if not module_file.exists():
        raise FileNotFoundError(f"{module_file} not found.")
    module_path = module_file.parent
    if not module_path in sys.path:
        logger.info(f'{module_path} not in sys.path, adding it')
        sys.path.insert(0, str(module_path))

    imported_module = importlib.import_module(module_file.stem)
    attribute = getattr(imported_module, attribute_name)
    return attribute