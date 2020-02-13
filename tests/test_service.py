import pytest
import logging

"""
These tests invoke the scheduler service class directly (i.e. bypassing any ipc stuff).
"""

class TestJobExecution:
    def test_job_function(self, caplog):
        from pyrsched.server.service import job_function

        # this runs one pipeline with custom configuration. 
        # Its function is checked by its log messages 
        # (see: https://docs.pytest.org/en/latest/logging.html#caplog-fixture).
        job_function("helloworld", "logs", logging.INFO, None, "tests/testdata")
        
        # at least one entry in the log has the level NOTIFY
        notify_records = [r for r in caplog.records if r.levelname == "NOTIFY"]
        assert len(notify_records) > 0

        # one of these entries contains the job output: "Hello World!"
        assert any("Hello World!" in r.getMessage() for r in notify_records)


class TestState:
    def test_blank(self, scheduler_service):
        scheduler_blank_state = scheduler_service.state()

        # scheduler is not running
        assert scheduler_blank_state["run_state"] == 0
        assert not scheduler_blank_state["is_running"]

        # no jobs are stored 
        assert scheduler_blank_state["total_jobs"] == 0
        assert len(scheduler_blank_state["job_list"]) == 0    


class TestGetJobs:
    def test_list_empty(self, scheduler_service):
        # with a fresh SchedulerService, 
        # there should be no jobs in the store
        jobs = scheduler_service.list_jobs()
        assert len(jobs) == 0

    def test_get_not_available(self, scheduler_service):
        # try to get a non existant hob
        job = scheduler_service.get_job("some-unknown-id")

        # ...which should be None
        assert job is None

    def test_get_existing(self, scheduler_service):
        # add a job and retrieve it again wit "get"
        job_id = scheduler_service.add_job("testpipeline")        
        job = scheduler_service.get_job(job_id)

        # this should return the job which was added before
        assert job_id == job["id"]

class TestAddRemove:
    def test_add_first(self, scheduler_service):
        # add a job
        job_id = scheduler_service.add_job("testpipeline")
        assert job_id is not None

        # so the list of jobs should be at length 1 now
        jobs = scheduler_service.list_jobs()
        assert len(jobs) == 1
        
        # and that one element is the job we've added above
        job = jobs[0]
        assert job['id'] == job_id

    def test_add_two(self, scheduler_service):
        # add two different jobs
        job_id1 = scheduler_service.add_job("testpipeline")
        assert job_id1 is not None

        job_id2 = scheduler_service.add_job("helloworld")
        assert job_id2 is not None

        # so there should be 2 jobs now 
        jobs = scheduler_service.list_jobs()
        assert len(jobs) == 2
        
        # and these jobs are the same as added above
        # NOTE: this assumes, that the order is retained in the job store
        job1 = jobs[0]
        assert job1['id'] == job_id1

        job2 = jobs[1]
        assert job2['id'] == job_id2

    def test_remove(self, scheduler_service):
        # add a job and remove it immediately
        job_id = scheduler_service.add_job("testpipeline")
        job = scheduler_service.remove_job(job_id)

        # so we expect that no job is in the jobstore
        jobs = scheduler_service.list_jobs()
        assert len(jobs) == 0

    def test_remove_nonexistent(self, scheduler_service):
        # try to remove a job that does not exist
        job = scheduler_service.remove_job("not-a-job-id")

class TestRunPause:
    """
    This tests operations involved in starting a job on the scheduler.
    Since the scheduler instance is not running, there will be no real
    job execution, but this is not in scope of the tests. The scheduler
    API behaves the same even if the scheduler is not running.
    """
    def test_start(self, scheduler_service):
        # add a job and start it
        job_id = scheduler_service.add_job("testpipeline")
        job = scheduler_service.start_job(job_id)

        # it is expected, that the job is scheduler, i.e. it has a predicted next run time
        assert job["next_run_time"] is not None

    def test_start_nonexistent(self, scheduler_service):
        # try to start a job which not exists
        job = scheduler_service.start_job("not-a-job-id")

        # the scheduler should do nothing and return None
        assert job is None

    def test_pause(self, scheduler_service):
        # ass a job and start it
        job_id = scheduler_service.add_job("testpipeline")
        job = scheduler_service.start_job(job_id)
        
        # it should be scheduled 
        # NOTE: this dupes ``test_start``
        assert job["next_run_time"] is not None
        
        # pause the running job
        job = scheduler_service.pause_job(job_id)

        # it is expected that the job has no next run time
        assert job["next_run_time"] is None
        
    def test_pause_nonexistent(self, scheduler_service):
        # try to pause a job which does not exist
        job = scheduler_service.pause_job("not-a-job-id")

        # it is expected for the scheduler to do nothing and just return None
        assert job is None

    def test_reschedule(self, scheduler_service):
        # add a job 
        job_id = scheduler_service.add_job("testpipeline", interval=10)

        # check if the interval was taken correctly
        job = scheduler_service.get_job(job_id)
        assert job["trigger"]["interval"] == pytest.approx(10.0)

        # reschedule the job
        job = scheduler_service.reschedule_job(job_id, interval=30)

        # rescheduling starts the job 
        assert job["next_run_time"] is not None

        # and the interval should have changed
        assert job["trigger"]["interval"] == pytest.approx(30.0)

    def test_reschedule_nonexistent(self, scheduler_service):
        # try to reschedule a job that does not exist
        job = scheduler_service.reschedule_job("not-a-job-id")

        # the scheduler should do nothing and return None
        assert job is None
