import pytest

class TestJobManagement:
    endpoint = "/status"

    @pytest.mark.parametrize('method', ['POST', 'PUT', 'DELETE'])
    def test_http_method_not_allowed_on_status_endpoint(self, testapp, method):
        res = testapp.request(self.endpoint, method=method, expect_errors=True)
        assert res.status_int == 405  # method not allowed

    def test_status(self, testapp):
        res = testapp.get(self.endpoint)
        assert res.json['is_running'] 

