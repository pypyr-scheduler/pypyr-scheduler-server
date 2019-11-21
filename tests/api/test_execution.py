import time

import pytest
import apscheduler
from flask import current_app


class TestJobExecution:
    endpoint = "/jobs"

    def test_job_execution_status(self, testapp, upload_pipeline, caplog):
        # upload a runnable pipeline
        uploaded_filename = 'test_pipeline_create.yaml'
        upload_pipeline.upload('pipeline_now.yaml', uploaded_filename)
        # run it
        interval = 1
        res = testapp.post(f"{self.endpoint}/{uploaded_filename}/{interval}")
        assert res.status_int == 201
        job = res.json

        # get status (should not run)
        res = testapp.get(f"{self.endpoint}/{job['name']}/execution")
        assert not res.json["next_run_time"]

        # start the job
        res = testapp.post(f"{self.endpoint}/{job['name']}/execution")
        assert res.json["next_run_time"]

        # wait for the first job execution
        # no obious method to get a jobs execution state, 
        # so we assume that the job is done in max .5s
        # if not, the assertion below will fail anyway and somone has to look here :P
        time.sleep(1.5)

        # TODO: assertion could be too tight if a log message appears after the job execution is done
        # test if the job was executed
        assert caplog.records[-1].message.endswith("executed successfully")

    @pytest.mark.parametrize('method', ['GET', 'POST', 'DELETE'])
    def test_job_execution_non_existing(self, testapp, method):
        res = testapp.request(f"{self.endpoint}/arbitrary_nonexistent_job_name/execution", method=method, expect_errors=True)
        assert res.status_int == 404

    def test_stop_job(self, testapp, upload_pipeline):
        # upload a runnable pipeline
        uploaded_filename = 'test_pipeline_create.yaml'
        upload_pipeline.upload('pipeline_now.yaml', uploaded_filename)
        # run it
        interval = 1
        res = testapp.post(f"{self.endpoint}/{uploaded_filename}/{interval}")
        assert res.status_int == 201
        job = res.json

        # start the job
        res = testapp.post(f"{self.endpoint}/{job['name']}/execution")
        assert res.json["next_run_time"]

        # wait a bit
        time.sleep(3)

        # stop the job
        res = testapp.delete(f"{self.endpoint}/{job['name']}/execution")
        assert res.status_int == 204  # NO CONTENT

        # get status (should not run anymore )
        res = testapp.get(f"{self.endpoint}/{job['name']}/execution")
        assert not res.json["next_run_time"]        
        
