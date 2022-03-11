import pytest
import json
import time
import os

from flaskapp.mpa_analysis_tool import create_app
from dao import get_dbinfo

URL = 'http://localhost:5000'


@pytest.fixture
def api():
    config_file = '../config/unit_test_config.py'
    app = create_app(config_file)
    app.config['TESTING'] = True
    api = app.test_client()

    return api


def test_get_dbinfo(api):
    kwargs = {
        'dbname': 'test',
        'user': 'test',
        'host': 'test',
        'password': 'test',
        'port': 'test'
    }
    resp = get_dbinfo(**kwargs)

    assert resp == kwargs