import pytest
from pathlib import Path


class TestPipelines:
    endpoint = '/pipelines'

    @pytest.mark.parametrize('method', ['POST', 'PUT', 'DELETE'])
    def test_http_method_not_allowed(self, testapp, method):
        res = testapp.request(self.endpoint, method=method, expect_errors=True)
        assert res.status_int == 405  # method not allowed

    def test_pipeline_upload_contents_match(self, testapp, temp_pipeline):
        pipeline = temp_pipeline.make_pipeline()
        files = [
            ('body', str(pipeline['file'])),
        ]
        uploaded_filename = 'test_pipeline_upload.yaml'
        res = testapp.post(f'{self.endpoint}/{uploaded_filename}', upload_files=files)
        assert res.status_int == 201

        uploaded_file = (
            Path(testapp.app.iniconfig.get('pipelines', 'base_path')) / uploaded_filename
        )
        uploaded_content = uploaded_file.read_text()
        assert pipeline['content'] == uploaded_content
        try:
            uploaded_file.unlink()
        except FileNotFoundError:
            pass

    @pytest.mark.parametrize(
        'filename',
        [
            '/etc/passwd',
            '../../bla.yaml',
            'C:/Programme/test.yaml',
            '%C3%A9%C3%A9%C3%A9',
        ],
    )
    def test_malicious_upload(self, testapp, temp_pipeline, filename):
        pipeline = temp_pipeline.make_pipeline()
        files = [
            ('body', str(pipeline['file'])),
        ]
        res = testapp.post(
            f'{self.endpoint}/{filename}', upload_files=files, expect_errors=True
        )
        assert res.status_int >= 400

    @pytest.mark.parametrize(
        'filename',
        [
            '/etc/passwd',
            '../../bla.yaml',
            'C:/Programme/test.yaml',
            '%C3%A9%C3%A9%C3%A9',
        ],
    )
    def test_pipeline_replace_malicious(self, testapp, temp_pipeline, filename):
        pipeline = temp_pipeline.make_pipeline()
        files = [
            ('body', str(pipeline['file'])),
        ]
        res = testapp.put(
            f'{self.endpoint}/{filename}', upload_files=files, expect_errors=True
        )
        assert res.status_int >= 400

    def test_pipeline_replace_missing_target(self, testapp, temp_pipeline):
        # delete target file if it exists - just for safety
        uploaded_filename = 'test_pipeline_upload_missing.yaml'
        try:
            target_file = (
                Path(testapp.app.iniconfig.get('pipelines', 'base_path')) / uploaded_filename
            )
            target_file.unlink()
            # this would be easier in 3.8:
            # there is an optional argument missing_ok=True which suppresses the exception

        except FileNotFoundError:
            pass

        pipeline = temp_pipeline.make_pipeline()
        files = [
            ('body', str(pipeline['file'])),
        ]
        res = testapp.put(
            f'{self.endpoint}/{uploaded_filename}',
            upload_files=files,
            expect_errors=True,
        )
        assert res.status_int == 404

    def test_pipeline_replace_with_other_file(self, testapp, temp_pipeline):
        # delete target file if it exists - just for safety
        uploaded_filename = 'test_pipeline_upload_replace.yaml'
        try:
            target_file = (
                Path(testapp.app.iniconfig.get('pipelines', 'base_path')) / uploaded_filename
            )
            target_file.unlink()
        except FileNotFoundError:
            pass

        # upload a new file
        pipeline = temp_pipeline.make_pipeline()
        files = [
            ('body', str(pipeline['file'])),
        ]
        res = testapp.post(f'{self.endpoint}/{uploaded_filename}', upload_files=files)
        assert res.status_int == 201

        # replace file
        other_pipeline = temp_pipeline.make_pipeline(root_element_name='elpmaxe')
        files = [
            ('body', str(other_pipeline['file'])),
        ]
        res = testapp.put(f'{self.endpoint}/{uploaded_filename}', upload_files=files)
        assert res.status_int == 204

        # check if the content of the file has changed
        uploaded_file = (
            Path(testapp.app.iniconfig.get('pipelines', 'base_path')) / uploaded_filename
        )
        uploaded_content = uploaded_file.read_text()
        assert other_pipeline['content'] == uploaded_content

        try:
            uploaded_file.unlink()
        except FileNotFoundError:
            pass

    def test_pipeline_delete(self, testapp, temp_pipeline):
        # try to delete a non existing file
        res = testapp.delete(
            f'{self.endpoint}/nonexisting_pipeline.yaml', expect_errors=True
        )
        assert res.status_int == 404

        # upload a file and expect it to be gone after deleting it
        pipeline = temp_pipeline.make_pipeline()
        files = [
            ('body', str(pipeline['file'])),
        ]
        uploaded_filename = 'test_pipeline_upload_and_delete.yaml'
        res = testapp.post(f'{self.endpoint}/{uploaded_filename}', upload_files=files)
        assert res.status_int == 201

        res = testapp.delete(f'{self.endpoint}/{uploaded_filename}')
        assert res.status_int == 204

    @pytest.mark.parametrize(
        'filename',
        [
            '/etc/passwd',
            '../../bla.yaml',
            'C:/Programme/test.yaml',
            '%C3%A9%C3%A9%C3%A9',
        ],
    )
    def test_pipeline_delete_malicious_filenames(self, testapp, filename):
        res = testapp.delete(f'{self.endpoint}/{filename}', expect_errors=True)
        assert res.status_int >= 400

    def test_pipeline_download(self, testapp, temp_pipeline):
        uploaded_filename = 'test_pipeline_download.yaml'
        # delete pipeline
        try:
            target_file = (
                Path(testapp.app.iniconfig.get('pipelines', 'base_path')) / uploaded_filename
            )
            target_file.unlink()
        except FileNotFoundError:
            pass

        # check if the pipeline is not there
        res = testapp.get(f'{self.endpoint}/{uploaded_filename}', expect_errors=True)
        assert res.status_int == 404

        # upload a pipeline
        pipeline = temp_pipeline.make_pipeline()
        files = [
            ('body', str(pipeline['file'])),
        ]
        res = testapp.post(f'{self.endpoint}/{uploaded_filename}', upload_files=files)
        assert res.status_int == 201

        # download it and check contents
        res = testapp.get(f'{self.endpoint}/{uploaded_filename}')
        assert res.body == pipeline['file'].read_bytes()

        # delete the file
        res = testapp.delete(f'{self.endpoint}/{uploaded_filename}')

    def test_list_pipelines(self, testapp, temp_pipeline):
        # upload some pipelines
        pipeline1 = temp_pipeline.make_pipeline()
        pipeline2 = temp_pipeline.make_pipeline(root_element_name='elpmaxe')
        pipeline3 = temp_pipeline.make_pipeline(root_element_name='yet_another_one')
        for p in [pipeline1, pipeline2, pipeline3]:
            files = [
                ('body', str(p['file'])),
            ]
            res = testapp.post(f'{self.endpoint}/{p["name"]}', upload_files=files)

        # download info
        res = testapp.get(self.endpoint)
        assert len(res.json) == 3

        # teardown
        for p in [pipeline1, pipeline2, pipeline3]:
            res = testapp.delete(f'{self.endpoint}/{p["name"]}')
