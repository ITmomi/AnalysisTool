import pytest
import requests
import json
import time
import os

from flaskapp.mpa_analysis_tool import create_app

URL = 'http://localhost:5000'
TEST_LOG_PATH = 'test/sample_log/MountPressLog'
VALIDATION_JSON_PATH = 'test/validation_json'
VALIDATION_JSON_FILE = 'validation_mountpress.json'
LOG_NAME = 'MountPressLog'

rid = None


@pytest.fixture
def api():
    config_file = '../config/unit_test_config.py'
    app = create_app(config_file)
    app.config['TESTING'] = True
    api = app.test_client()

    return api


def test_convertor_job(api):
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

    assert response.status_code == 200

    resp_body = json.loads(response.data)
    rid = resp_body['rid']
    print(rid)


def test_convertor_get_job(api):
    global rid

    while True:
        response = api.get(URL + '/api/converter/job/'+ rid)
        resp_body = json.loads(response.data)
        print(resp_body['status'])
        if resp_body['status'] == 'success':
            break

        time.sleep(1)

    assert resp_body['status'] == 'success'


def test_converter_get_lists_default(api):
    global rid

    response = api.get(URL + '/api/analysis/lists/' + LOG_NAME + '/' + rid)
    resp_body = json.loads(response.data)

    with open(os.path.join(VALIDATION_JSON_PATH, VALIDATION_JSON_FILE), 'r') as f:
        json_data = json.load(f)

    assert resp_body == json_data['lists_default']


def test_analysis_get_summary_default(api):
    global rid

    param = {
        "start": "2017-04-29 00:00:00",
        "end": "2017-04-29 23:59:59"
    }
    print(param)

    response = api.get(URL + f'/api/analysis/summaries/{LOG_NAME}/{rid}', query_string=param)
    resp_body = json.loads(response.data)
    print(resp_body)

    with open(os.path.join(VALIDATION_JSON_PATH, VALIDATION_JSON_FILE), 'r') as f:
        json_data = json.load(f)

    assert resp_body == json_data['summary_default']


def test_analysis_get_detail_default(api):
    global rid

    param = {
        "start": "2017-04-29 00:00:00",
        "end": "2017-04-29 23:59:59",
        "group_by": "period",
        "group_value": "4h",
        "group_selected": ["2017-04-29 08:00:00", "2017-04-29 12:00:00"],

    }
    print(param)

    response = api.get(URL + f'/api/analysis/details/{LOG_NAME}/{rid}', query_string=param)
    resp_body = json.loads(response.data)
    print(resp_body)

    with open(os.path.join(VALIDATION_JSON_PATH, VALIDATION_JSON_FILE), 'r') as f:
        json_data = json.load(f)

    assert resp_body == json_data['detail_default']