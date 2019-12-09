import json
import os
import time
import logging
import argparse
from pathlib import Path

import pytest

import pyrsched.__main__ as main
from pyrsched.app import PYRSCHED_DEFAULTS as defaults
from pyrsched.app import create_app

class TestCommandline(object):
    def test_parser(self):
        parser = main.create_parser()
        assert parser.prog == "pyrsched" 

    @pytest.mark.parametrize(
        'config_section',
        defaults.keys(),
    )
    def test_show_config(self, capsys, config_section):
        args = ["--show-config", "-c", "tests/testdata/pyrsched.test.ini"]
        parser = main.create_parser()
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main.main(parser.parse_args(args))
        captured = capsys.readouterr()
        assert "[pipelines]" in captured.out

        # --show-config should exit with SystemExit        
        assert pytest_wrapped_e.type == SystemExit

    @pytest.mark.parametrize(
        'config_section',
        defaults.keys(),
    )
    def test_show_config_json(self, capsys, config_section):
        args = ["--show-config", "--json", "-c", "tests/testdata/pyrsched.test.ini"]
        parser = main.create_parser()
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main.main(parser.parse_args(args))
        captured = capsys.readouterr()

        # check if the output is json and contains the required keys
        output_data = json.loads(captured.out)
        assert output_data is not None
        assert output_data[config_section] is not None

        # --show-config should exit with SystemExit        
        assert pytest_wrapped_e.type == SystemExit        

    def test_show_help(self, capsys):
        args = ["--help"]
        parser = main.create_parser()
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main.main(parser.parse_args(args))
        captured = capsys.readouterr()

        # captured.out contains the help text,
        # we check if the invocation line contains the script name and 
        # for specific defaults
        assert "usage: pyrsched [-h]" in captured.out
        assert "(default: conf/logging_config.py)." in captured.out
        assert "Include debugging information (default: False)." in captured.out

    def test_no_log_dir(self):
        path = Path(os.path.abspath(__file__)).parent.parent
        config_file = path / 'testdata/pyrsched.test_nonexistent_logpath.ini'
        app = create_app(config_file.resolve())    

        log_path = app.app.iniconfig.get("pipelines", "log_path")    
        created_path = Path(app.app.root_path).parent / log_path
        assert created_path.exists()

        # teardown, remove created log path
        created_path.rmdir()

    def test_no_ini_file(self):
        args = ["-c", "nonexistent_ini_file.ini"]
        parser = main.create_parser()
        with pytest.raises(FileNotFoundError) as pytest_wrapped_e:
            main.main(parser.parse_args(args))
        assert pytest_wrapped_e.type == FileNotFoundError        

    def test_no_scheduler_config(self):
        args = ["-sc", "nonexistent_config.py"]
        parser = main.create_parser()
        with pytest.raises(FileNotFoundError) as pytest_wrapped_e:
            main.main(parser.parse_args(args))
        assert pytest_wrapped_e.type == FileNotFoundError     