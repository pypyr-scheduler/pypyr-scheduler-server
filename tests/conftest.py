import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml



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

@pytest.fixture(scope="function")
def apscheduler_config():
    return {
        'apscheduler.jobstores.default': {
            'type': 'memory',
        },
        'apscheduler.executors.default': {
            'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
            'max_workers': '1'
        },
        'apscheduler.job_defaults.coalesce': 'false',
        'apscheduler.job_defaults.max_instances': '1',
        'apscheduler.timezone': 'Europe/Berlin',
    }

@pytest.fixture(scope="function")
def pypyr_config():
    return {
        'pipelines.base_path': 'pipelines',
        'pipelines.log_path': 'logs',
        'pipelines.log_level': 20,  ## logging.INFO,
        'server_port': 12345,
    }

@pytest.fixture(scope="function")
def logging_config():
    return {
        'version': 1, 
    }

@pytest.fixture(scope="function")
def test_config(apscheduler_config, pypyr_config, logging_config):
    c = SimpleNamespace(
        apscheduler=apscheduler_config,
        pypyr=pypyr_config,
        log_config=logging_config
    )
    return c

@pytest.fixture(scope="function")
def scheduler_service(test_config):     
    from apscheduler.schedulers.background import BackgroundScheduler
    from pyrsched.server.service import SchedulerService   

    scheduler = BackgroundScheduler(test_config.apscheduler)
    service = SchedulerService(scheduler=scheduler, config=test_config, logger=None)
    return service

@pytest.fixture(scope="function")
def scheduler_server():
    from pyrsched.server.server import ServerWrapper
    return ServerWrapper(Path("tests/testdata/"))