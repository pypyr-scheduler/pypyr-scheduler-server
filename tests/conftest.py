"""
derived from: https://github.com/hirose31/connexion-tiny-petstore/blob/master/tests/conftest.py
"""

import pytest
import webtest as wt

from connexion.mock import MockResolver

from pyrsched.app import create_app

@pytest.yield_fixture(scope='function')
def app():
    # _resolver = MockResolver(mock_all=True)
    _app = create_app()    

    ctx = _app.app.test_request_context()
    ctx.push()

    yield _app.app

    ctx.pop()

@pytest.fixture(scope='function')
def testapp(app):
    return wt.TestApp(app)
 
@pytest.fixture(scope='function', autouse=True)
def generate_testdata(app):
    pass