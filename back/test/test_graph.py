import pytest
import json
import os

from flaskapp.mpa_analysis_tool import create_app
from config.unit_test_config import *
from dao import get_db_config

URL = 'http://localhost:5000'


@pytest.fixture
def api():
    config_file = '../config/unit_test_config.py'
    app = create_app(config_file)
    app.config['TESTING'] = True
    api = app.test_client()

    return api


def test_add_edit_graph(api):
    params = {
        'name': 'test',
        'script': 'function()'
    }
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    data = json.dumps(params)

    func_id = 6

    response = api.post(URL + f'/api/resources/graph/{func_id}', data=data, headers=headers)
    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200

    graph_id = resp_body['id']

    response = api.put(URL + f'/api/resources/graph/{func_id}/0', data=data, headers=headers)

    assert response.status_code == 400

    response = api.put(URL + f'/api/resources/graph/{func_id}/{graph_id}', data=data, headers=headers)

    assert response.status_code == 400

    params = {
        'name': 'test1',
        'script': 'function()'
    }

    data = json.dumps(params)

    response = api.put(URL + f'/api/resources/graph/{func_id}/{graph_id}', data=data, headers=headers)

    assert response.status_code == 200

    response = api.delete(URL + f'/api/resources/graph/{func_id}/{graph_id}')

    assert response.status_code == 200
