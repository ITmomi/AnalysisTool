import pytest
import json
import time
import os

from flaskapp.mpa_analysis_tool import create_app

URL = 'http://localhost:5000'
TEST_LOG_PATH = 'test/sample_log/LipsFocus'
VALIDATION_JSON_PATH = 'test/validation_json'
VALIDATION_JSON_FILE = 'validation_lipsfocus.json'
LOG_NAME = 'LiPSFocus'

rid = None


@pytest.fixture
def api():
    config_file = '../config/unit_test_config.py'
    app = create_app(config_file)
    app.config['TESTING'] = True
    api = app.test_client()

    return api


def test_parameter(api):
    global rid
    files = []
    for dirpath, dirnames, filenames in os.walk(TEST_LOG_PATH):
        for file in filenames:
            # files.append(('files', open(os.path.join(dirpath, file), 'rb')))
            files.append(open(os.path.join(dirpath, file), 'rb'))

    # response = api.post(URL+'/api/converter/file', files=files)
    response = api.post(URL + '/api/converter/file', data={'files': files})

    resp_body = json.loads(response.data)
    print(resp_body)

    data = {
        "log_name": LOG_NAME,
        "source": "local",
        "file": resp_body['fid'],
        "equipment_type": "G803"
    }
    print(data)
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    response = api.post(URL + '/api/converter/job', data=json.dumps(data), headers=headers)

    resp_body = json.loads(response.data)
    rid = resp_body['rid']
    print(rid)

    while True:
        response = api.get(URL + '/api/converter/job/'+ rid)
        resp_body = json.loads(response.data)
        print(resp_body['status'])
        if resp_body['status'] == 'success':
            break

        time.sleep(1)

    assert resp_body['status'] == 'success'


def test_parameter_is_period_valid_1(api):
    global rid
    params = {
        'one_period': '0h',
        'adj_period': None,
        'list_group': None
    }

    print(params)
    response = api.get(URL + '/api/analysis/lists/' + LOG_NAME + '/' + rid, query_string=params)

    assert response.status_code == 400

    print(json.loads(response.data))


def test_parameter_is_period_valid_2(api):
    global rid
    params = {
        'one_period': '0',
        'adj_period': None,
        'list_group': None
    }

    print(params)
    response = api.get(URL + '/api/analysis/lists/' + LOG_NAME + '/' + rid, query_string=params)

    assert response.status_code == 400

    print(json.loads(response.data))


def test_parameter_is_period_valid_3(api):
    global rid
    params = {
        'one_period': 'hh',
        'adj_period': None,
        'list_group': None
    }

    print(params)
    response = api.get(URL + '/api/analysis/lists/' + LOG_NAME + '/' + rid, query_string=params)

    assert response.status_code == 400

    print(json.loads(response.data))


def test_parameter_is_period_valid_4(api):
    global rid
    params = {
        'one_period': '0z',
        'adj_period': None,
        'list_group': None
    }

    print(params)
    response = api.get(URL + '/api/analysis/lists/' + LOG_NAME + '/' + rid, query_string=params)

    assert response.status_code == 400

    print(json.loads(response.data))


def test_parameter_is_period_valid_5(api):
    global rid
    params = {
        'one_period': '1h',
        'adj_period': '0d',
        'list_group': None
    }

    print(params)
    response = api.get(URL + '/api/analysis/lists/' + LOG_NAME + '/' + rid, query_string=params)

    assert response.status_code == 400

    print(json.loads(response.data))


def test_parameter_is_period_valid_6(api):
    global rid
    params = {
        'one_period': '1d',
        'adj_period': '0h',
        'list_group': None
    }

    print(params)
    response = api.get(URL + '/api/analysis/lists/' + LOG_NAME + '/' + rid, query_string=params)

    assert response.status_code == 400

    print(json.loads(response.data))


def test_parameter_is_period_valid_7(api):
    global rid
    params = {
        'one_period': '5h',
        'adj_period': '0h',
        'list_group': None
    }

    print(params)
    response = api.get(URL + '/api/analysis/lists/' + LOG_NAME + '/' + rid, query_string=params)

    assert response.status_code == 400

    print(json.loads(response.data))


def test_parameter_is_period_valid_8(api):
    global rid
    params = {
        'one_period': '-5h',
        'adj_period': '0h',
        'list_group': None
    }

    print(params)
    response = api.get(URL + '/api/analysis/lists/' + LOG_NAME + '/' + rid, query_string=params)

    assert response.status_code == 400

    print(json.loads(response.data))


def test_parameter_is_period_valid_9(api):
    global rid
    params = {
        'one_period': '4h',
        'adj_period': '25h',
        'list_group': None
    }

    print(params)
    response = api.get(URL + '/api/analysis/lists/' + LOG_NAME + '/' + rid, query_string=params)

    assert response.status_code == 400

    print(json.loads(response.data))


def test_parameter_is_period_valid_10(api):
    global rid
    params = {
        'one_period': '7d',
        'adj_period': '32d',
        'list_group': None
    }

    print(params)
    response = api.get(URL + '/api/analysis/lists/' + LOG_NAME + '/' + rid, query_string=params)

    assert response.status_code == 400

    print(json.loads(response.data))