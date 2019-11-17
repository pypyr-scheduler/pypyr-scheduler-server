class TestJobManagement:
    endpoint = '/jobs'

    def test_job_create(self, testapp, pipeline):
        uploaded_filename = "test_pipeline_create_job.yaml"
        pipe = pipeline.load("pipeline_now.yaml")
        files = [("body", str(pipe['file'])), ]
        testapp.post(f"/pipelines/{uploaded_filename}", upload_files=files)
        res = testapp.post(f'{self.endpoint}/{uploaded_filename}/10', expect_errors=True)
        print(res)
