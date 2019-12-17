# pragma: no cover   
import os
from pathlib import Path
from pyrsched.app import create_app, PYRSCHED_DEFAULTS
from pyrsched.__main__ import create_parser

# pass args via the --pyargv option in uwsgi
parser = create_parser()
args = parser.parse_args()

path = Path(os.path.abspath(__file__)).parent
config_file = getattr(args, "config", None) or path / PYRSCHED_DEFAULTS['config']['config']
if not config_file.is_absolute():
    config_file = Path(__file__).parent / spec_dir

app = create_app(config_file.resolve(), args=args)