"""
derived from:
https://github.com/hirose31/connexion-tiny-petstore/blob/master/tests/conftest.py
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path

import pytest
import webtest as wt
import yaml

from pyrsched.app import create_app


@pytest.yield_fixture(scope="function")
def app():
    path = Path(os.path.abspath(__file__)).parent
    config_file = path / ".." / "conf" / "pyrsched.test.ini"
    
    _app = create_app(config_file.resolve())
    _app.app.testing = True

    ctx = _app.app.test_request_context()
    ctx.push()

    # delete test pipeline upload directory if present
    pipeline_base_path = Path(_app.app.iniconfig.get('pipelines', 'base_path'))
    if pipeline_base_path.exists():
        for f in pipeline_base_path.iterdir():
            f.unlink()
        pipeline_base_path.rmdir()
    # log_base_path = Path(_app.app.iniconfig.get('pipelines', 'log_path'))
    # if log_base_path.exists():
    #     for f in log_base_path.iterdir():
    #         f.unlink()
    #     log_base_path.rmdir()

    yield _app.app

    ctx.pop()


@pytest.fixture(scope="function")
def testapp(app):
    return wt.TestApp(app)


@pytest.fixture(scope="function")
def temp_pipeline(tmp_path):
    class Inner:
        def __init__(self):
            self.temp_dir = tmp_path / "pypyr_test"
            self.temp_dir.mkdir()

        def make_pipeline(self, root_element_name='example'):
            temp_path = self.temp_dir / f"testpipeline_{root_element_name}.yml"
            content = yaml.dump({
                f"{root_element_name}": ['list_entry_one', 'list_entry_two']
            })
            temp_path.write_text(content)
            return {
                'content': content,
                'file': temp_path,
                'name': f"testpipeline-{root_element_name}.yaml",
            }

    return Inner()


@pytest.fixture(scope='function')
def pipeline(path='testdata'):
    class Inner:
        def __init__(self):
            self.base_path = Path(".").resolve() / "tests" / "testdata"

        def load(self, name):
            pipeline_file = self.base_path / name
            content = yaml.full_load(pipeline_file.read_text())
            return {
                'content': content,
                'file': pipeline_file,
                'name': name,
            }

    return Inner()

@pytest.fixture(scope='function')
def upload_pipeline(pipeline, testapp):
    class Inner:
        def upload(self, local_filename, remote_filename=None):
            if not remote_filename:
                remote_filename = local_filename
            pipe = pipeline.load(local_filename)
            files = [
                ("body", str(pipe["file"])),
            ] 
            return testapp.post(f"/pipelines/{remote_filename}", upload_files=files)   
            
    return Inner()