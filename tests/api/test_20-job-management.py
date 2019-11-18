from datetime import timedelta
import pytest
import time

class TestJobManagement:
    endpoint = "/jobs"

    @pytest.mark.parametrize("interval, expected_error_code", [(10, 201), (0, 400),])
    def test_job_create(self, testapp, pipeline, interval, expected_error_code):
        # upload a runnable test pipeline
        uploaded_filename = "test_pipeline_create_job.yaml"
        pipe = pipeline.load("pipeline_now.yaml")
        files = [
            ("body", str(pipe["file"])),
        ]
        testapp.post(f"/pipelines/{uploaded_filename}", upload_files=files)

        # run it
        res = testapp.post(f"{self.endpoint}/{uploaded_filename}/{interval}", expect_errors=True)
        assert res.status_int == expected_error_code
        if interval > 0:
            assert res.json['trigger']['interval'] == str(timedelta(seconds=interval))
            assert not res.json['next_run_time'] 
        

    def test_job_create_nonexistent_pipeline(self, testapp):
        # run a nonexistent pipeline
        res = testapp.post(f"{self.endpoint}/test_pipeline_nonexistent.yaml/10", expect_errors=True)
        assert res.status_int == 404
