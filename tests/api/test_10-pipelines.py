import pytest


class TestPipelines:
    endpoint = "/pipelines"

    def test_fetch_all(self, testapp):
        res = testapp.get(self.endpoint, headers={"Accept": "application/json"})
        data = res.json
        print("data:", data)
        assert res.status_int == 200

    @pytest.mark.parametrize("method", ["POST", "PUT", "DELETE"])
    def test_http_method_not_allowed(self, testapp, method):
        res = testapp.request(self.endpoint, method=method, expect_errors=True)
        assert res.status_int == 405  # method not allowed
