import pytest
import os
import logging

class TestServer:
    def test_authkey_with_env(self, scheduler_server):
        shared_secret = "not-so-secret"
        os.environ["PYRSCHED_SECRET"] = shared_secret
        assert scheduler_server._check_authkey() == shared_secret

    def test_authkey_no_env(self, caplog, scheduler_server):
        del(os.environ["PYRSCHED_SECRET"])

        with caplog.at_level(logging.WARNING):
            auth_key = scheduler_server._check_authkey()

        # the second log record contains the secret
        # this secret is expected to be in the form 
        # 12345678-1234-5678-1234-567812345678 (32 hex digits with 4 hyphens)
        assert len(caplog.records[1].getMessage()) == 36
