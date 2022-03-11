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


def test_local(api):
    response = api.get(URL + '/api/setting/local')
    resp_body = json.loads(response.data)

    with open(os.path.join(RESOURCE_PATH, RSC_JSON_MGMT_LOCAL), 'r') as f:
        json_data = json.load(f)

        config = get_db_config()
        if 'items' in json_data:
            for item in json_data['items']:
                target = item['target']
                if target == 'username':
                    target = 'user'
                item['content'] = config[target]

    assert resp_body == json_data


def test_remote(api):
    response = api.get(URL + '/api/setting/remote')

    assert response.status_code == 200

def test_tables(api):
    response = api.get(URL + '/api/setting/tables')

    assert response.status_code == 200


def test_remote_status(api):
    db_id = 1
    response = api.get(URL + f'/api/setting/remote/{db_id}/status')
    resp_body = json.loads(response.data)

    assert response.status_code == 400
    assert 'msg' in resp_body

    db_id = 6
    response = api.get(URL + f'/api/setting/remote/{db_id}/status')
    resp_body = json.loads(response.data)

    assert response.status_code == 200

    diff = dict()
    diff['id'] = db_id
    diff['sts'] = 'success'
    assert resp_body['id'] == db_id
    assert resp_body == diff


def test_remote_add(api):
    params = {
        'host': 'localhost',
        'port': '5432',
        'username': 'postgres',
        'dbname': 'analysistool',
        'password': 'mandoo2525'
    }
    print(params)

    response = api.post(URL + f'/api/setting/remote', query_string=params)
    resp_body = json.loads(response.data)

    assert response.status_code == 400
    assert 'msg' in resp_body

    params = {
        'host': 'localhost',
        'port': '5432',
        'username': 'postgres',
        'dbname': 'analysistool',
        'password': 'postgres'
    }
    print(params)

    response = api.post(URL + f'/api/setting/remote', query_string=params)
    resp_body = json.loads(response.data)

    assert response.status_code == 200
    assert resp_body['name'] == f"{params['dbname']}@{params['host']}"
    assert resp_body['sts'] == 'success'


def test_remote_get_info(api):
    db_id = 1
    response = api.get(URL + f'/api/setting/remote/{db_id}')
    resp_body = json.loads(response.data)

    assert response.status_code == 400
    assert 'msg' in resp_body

    db_id = 6
    response = api.get(URL + f'/api/setting/remote/{db_id}')
    resp_body = json.loads(response.data)

    assert response.status_code == 200
    assert 'host' in resp_body
    assert 'port' in resp_body
    assert 'username' in resp_body
    assert 'dbname' in resp_body
    assert 'password' in resp_body


def test_remote_put(api):
    db_id = 0
    params = {
        'host': 'localhost',
        'port': '5432',
        'username': 'aaa',
        'dbname': 'analysistool',
        'password': 'mandoo2525'
    }
    print(params)

    response = api.put(URL + f'/api/setting/remote/{db_id}', query_string=params)
    resp_body = json.loads(response.data)

    assert response.status_code == 400
    assert 'msg' in resp_body

    params = {
        'host': 'localhost',
        'port': '5432',
        'username': 'postgres',
        'dbname': 'analysistool',
        'password': 'postgres'
    }
    print(params)

    response = api.put(URL + f'/api/setting/remote/{db_id}', query_string=params)
    resp_body = json.loads(response.data)

    assert response.status_code == 400
    assert 'msg' in resp_body

    db_id = 19
    response = api.put(URL + f'/api/setting/remote/{db_id}', query_string=params)
    resp_body = json.loads(response.data)

    assert response.status_code == 200

    diff = dict()
    diff['id'] = db_id
    diff['sts'] = 'success'
    diff['name'] = f"{params['dbname']}@{params['host']}"
    assert diff == resp_body


def test_remote_delete(api):
    db_id = 0
    response = api.delete(URL + f'/api/setting/remote/{db_id}')

    assert response.status_code == 400

    params = {
        'host': 'localhost',
        'port': '5432',
        'username': 'postgres',
        'dbname': 'analysistool',
        'password': 'postgres'
    }

    response = api.post(URL + f'/api/setting/remote', query_string=params)
    resp_body = json.loads(response.data)

    assert response.status_code == 200

    db_id = resp_body['id']

    response = api.delete(URL + f'/api/setting/remote/{db_id}')
    resp_body = json.loads(response.data)

    assert response.status_code == 200
    assert resp_body['id'] == db_id


def test_local_update(api):
    params = {
        'host': 'localhost',
        'port': '5432',
        'username': 'postgres',
        'dbname': 'analysistool',
        'password': 'mandoo2525'
    }

    response = api.put(URL + f'/api/setting/local', query_string=params)

    assert response.status_code == 400

    params = {
        'host': 'localhost',
        'port': '5432',
        'username': 'postgres',
        'dbname': 'analysistool',
        'password': 'postgres'
    }

    response = api.put(URL + f'/api/setting/local', query_string=params)
    assert response.status_code == 200

def test_connection_check(api):
    params = {
        'host': 'localhost',
        'port': '5432',
        'username': 'postgres',
        'dbname': 'analysistool',
        'password': 'mandoo2525'
    }

    print(params)

    response = api.post(URL + f'/api/setting/connection-check', query_string=params)
    resp_body = json.loads(response.data)

    assert response.status_code == 400
    assert 'msg' in resp_body

    params = {
        'host': 'localhost',
        'port': '5432',
        'username': 'postgres',
        'dbname': 'analysistool',
        'password': 'postgres'
    }

    response = api.post(URL + f'/api/setting/connection-check', query_string=params)
    resp_body = json.loads(response.data)

    assert response.status_code == 200
    assert 'data' in resp_body
