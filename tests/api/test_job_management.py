from datetime import timedelta
import pytest
import time
import uuid

class TestJobManagement:
    endpoint = "/jobs"

    @pytest.mark.parametrize('method', ['POST', 'PUT', 'DELETE'])
    def test_http_method_not_allowed_on_list_endpoint(self, testapp, method):
        res = testapp.request(self.endpoint, method=method, expect_errors=True)
        assert res.status_int == 405  # method not allowed

    def test_job_create(self, testapp, upload_pipeline):
        # upload a runnable pipeline
        uploaded_filename = 'test_pipeline_create.yaml'
        upload_pipeline.upload('pipeline_now.yaml', uploaded_filename)
        # run it
        interval = 10
        res = testapp.post(f"{self.endpoint}/{uploaded_filename}/{interval}")
        assert res.status_int == 201
        # check interval
        assert res.json['trigger']['interval'] == str(timedelta(seconds=interval))
        # check if the created job create in paused state
        assert not res.json['next_run_time'] 
        
    def test_job_create_with_illegal_interval(self, testapp, upload_pipeline):
        # upload a runnable test pipeline
        uploaded_filename = 'test_pipeline_create_job.yaml'
        upload_pipeline.upload('pipeline_now.yaml', uploaded_filename)

        # try to run it
        interval = 0
        res = testapp.post(f'{self.endpoint}/{uploaded_filename}/{interval}', expect_errors=True)
        assert res.status_int == 400

    def test_job_create_nonexistent_pipeline(self, testapp):
        # run a nonexistent pipeline
        res = testapp.post(f'{self.endpoint}/test_pipeline_nonexistent.yaml/10', expect_errors=True)
        assert res.status_int == 404

    def test_job_delete_by_job_id(self, testapp, upload_pipeline):
        # upload a pipeline
        uploaded_filename = 'test_pipeline_delete_job.yaml'
        upload_pipeline.upload('pipeline_now.yaml', uploaded_filename)
        
        # create a job for it
        interval = 10
        job = testapp.post(f'{self.endpoint}/{uploaded_filename}/{interval}')
        job_id = job.json['id']
        
        # delete it        
        res = testapp.delete(f'{self.endpoint}/{job_id}')
        assert res.status_int == 204

        # check if it is gone
        res = testapp.get(f'{self.endpoint}/{job_id}', expect_errors=True)    
        assert res.status_int == 404

    def test_job_delete_by_job_name(self, testapp, upload_pipeline):
        # upload a pipeline
        uploaded_filename = 'test_pipeline_delete_job.yaml'
        upload_pipeline.upload('pipeline_now.yaml', uploaded_filename)
        
        # create a job for it
        job = testapp.post(f'{self.endpoint}/{uploaded_filename}/10')
        job_name = job.json['name']
        assert job_name == 'test_pipeline_delete_job'
        
        # delete it        
        res = testapp.delete(f'{self.endpoint}/{job_name}')
        assert res.status_int == 204

        # check if it is gone
        res = testapp.get(f'{self.endpoint}/{job_name}', expect_errors=True)    
        assert res.status_int == 404

    def test_job_delete_nonexistent(self, testapp):
        # delete a nonexistent job      
        res = testapp.delete(f'{self.endpoint}/{uuid.uuid4()}', expect_errors=True)
        assert res.status_int == 404

    def test_job_get_one(self, testapp, upload_pipeline):
        # upload a pipeline
        uploaded_filename = 'test_pipeline_delete_job.yaml'
        upload_pipeline.upload('pipeline_now.yaml', uploaded_filename)
        
        # create a job for it
        job = testapp.post(f'{self.endpoint}/{uploaded_filename}/10')

        # request job info
        res = testapp.get(f'{self.endpoint}/{job.json["name"]}')    
        assert res.status_int == 200  # OK
        assert res.json['name'] == job.json['name']  # Name of returned job is the same as sent

    def test_job_get_all(self, testapp, upload_pipeline):
        # upload some pipelines and create jobs
        uploaded_ids = []
        for uploaded_filename in [
            'test_pipeline_get_all_1.yaml',
            'test_pipeline_get_all_2.yaml',
            'test_pipeline_get_all_3.yaml',
        ]:
            # use the same local pipeline, it's contents are not relevant here
            upload_pipeline.upload('pipeline_now.yaml', uploaded_filename)
            job = testapp.post(f'{self.endpoint}/{uploaded_filename}/10')
            uploaded_ids.append(job.json['id'])

        res = testapp.get(f'{self.endpoint}')
        assert res.status_int == 200
        assert len(res.json) == 3  # we uploaded 3 jobs and expect 3 jobs to be in the response
        
        downloaded_job_ids = [job['id'] for job in res.json]
        # check if ids of uploaded and downloaded jobs are the same
        assert set(uploaded_ids) == set(downloaded_job_ids)  

    def test_job_change_interval(self, testapp, upload_pipeline):
        # upload two pipelines (to switch between them)
        uploaded_filename = 'test_pipeline_change_job_interval.yaml'
        upload_pipeline.upload('pipeline_now.yaml', uploaded_filename)        

        # create a job for it
        job = testapp.post(f'{self.endpoint}/{uploaded_filename}/10')

        # change the interval
        other_job = testapp.put(f'{self.endpoint}/{job.json["id"]}/{uploaded_filename}/15')

        # check if the interval has changed
        res = testapp.get(f'{self.endpoint}/{job.json["id"]}')    
        assert res.json['trigger']['interval'] == "0:00:15"

    def test_job_change_name(self, testapp, upload_pipeline):
        # upload two pipelines (to switch between them)
        uploaded_filename_first = 'test_pipeline_change_job_name_first.yaml'
        upload_pipeline.upload('pipeline_now.yaml', uploaded_filename_first)   
        uploaded_filename_second = 'test_pipeline_change_job_name_second.yaml'
        upload_pipeline.upload('pipeline_now.yaml', uploaded_filename_second)        

        # create a job for the first one
        job = testapp.post(f'{self.endpoint}/{uploaded_filename_first}/10')

        # change the name
        other_job = testapp.put(f'{self.endpoint}/{job.json["id"]}/{uploaded_filename_second}/10')
        assert other_job.status_int == 200

        # check if the name was changed
        res = testapp.get(f'{self.endpoint}/{job.json["id"]}')   
        assert res.json['name'] == 'test_pipeline_change_job_name_second'

    def test_job_change_name_non_existant(self, testapp):
        res = testapp.put(f'{self.endpoint}/nonexistent_job/new_name_which_is_not_evaluated/10', expect_errors=True)
        assert res.status_int == 404
