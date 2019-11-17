class TestJobManagement:
    endpoint = '/jobs'

    def test_job_create(self, testapp, temp_pipeline):
        uploaded_filename = "test_pipeline_create_job.yaml"
        # upload a pipeline
        pipeline = temp_pipeline.make_pipeline()
        files = [("body", str(pipeline['file'])), ]
        testapp.post(f"/pipelines/{uploaded_filename}", upload_files=files)
        res = testapp.post(f'{self.endpoint}/{uploaded_filename}/10', expect_errors=True)
        print(res)
