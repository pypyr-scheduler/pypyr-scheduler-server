import pytest

    # @pytest.mark.parametrize('method', ['POST', 'PUT', 'DELETE'])
    # def test_http_method_not_allowed_on_status_endpoint(self, testapp, method):
    #     res = testapp.request(self.endpoint, method=method, expect_errors=True)
    #     assert res.status_int == 405  # method not allowed

class TestJobExecution:
    def test_job_function(self):
        pass

class TestState:
    def test_blank(self, scheduler_service):
        scheduler_blank_state = scheduler_service.state()

        # scheduler is not running
        assert scheduler_blank_state["run_state"] == 0
        assert not scheduler_blank_state["is_running"]

        # no jobs are stored 
        assert scheduler_blank_state["total_jobs"] == 0
        assert len(scheduler_blank_state["job_list"]) == 0


class TestListJobs:
    def test_empty(self, scheduler_service):
        jobs = scheduler_service.list_jobs()
        assert len(jobs) == 0

class TestAdd:
    def test_add_first(self, scheduler_service):
        job_id = scheduler_service.add_job("testpipeline")
        assert job_id is not None

        jobs = scheduler_service.list_jobs()
        assert len(jobs) == 1
        
        job = jobs[0]
        assert job['id'] == job_id
