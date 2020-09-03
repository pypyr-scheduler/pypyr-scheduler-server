import logging
from pathlib import Path
import time

class TestLogging:
    def test_job_function_with_censor(self, caplog):
        from pyrsched.server.service import job_function

        # create log dir (on TravisCI, there is no directory configured)
        # /home/travis/build/pypyr-scheduler/pypyr-scheduler-server/logs/helloworld.log
        log_path = Path("./logs")
        log_path.mkdir(parents=True, exist_ok=True)

        # this runs one pipeline with custom configuration. 
        # Its function is checked by its log messages 
        # (see: https://docs.pytest.org/en/latest/logging.html#caplog-fixture).
        job_function("testlogcensor", "logs", logging.INFO, None, "tests/testdata", sensitive_keys=['sensitive_value', ])
        
        # caplog only sees logging.LogRecords which are then formatted with pytests logger.
        # we have to format them with our own formatter to thet it.
        from pyrsched.server.logging import SensitiveValueFormatter
        formatter = SensitiveValueFormatter(sensitive_keys=['sensitive_value', ])
        formatted_messages = [formatter.format(r) for r in caplog.records]
        print(formatted_messages)
        assert any("'sensitive_value': '*****'" in m for m in formatted_messages)

    # test if log messages are mangled between log files
    # def test_parallel(self, caplog, scheduler_service):
    #     # ass a job and start it
    #     job_id1 = scheduler_service.add_job("helloworld", interval=1)
    #     job1 = scheduler_service.start_job(job_id1)      
    #     job_id2 = scheduler_service.add_job("pipeline_now", interval=1)
    #     job2 = scheduler_service.start_job(job_id2)    

    #     time.sleep(15)

    #     for r in caplog.records:
    #         print(r.msg)
