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

@pytest.fixture
def api():
    config_file = '../config/unit_test_config.py'
    app = create_app(config_file)
    app.config['TESTING'] = True
    api = app.test_client()

    return api


def test_converter_cancel(api):
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
        if resp_body['status'] == 'running':
            break

        time.sleep(1)

    response = api.delete(URL + f'/api/converter/job/{rid}')

    assert response.status_code == 200


# def test_converter_rapid_local_error(api):
#     files = []
#     for dirpath, dirnames, filenames in os.walk('test/sample_log/rapid'):
#         for file in filenames:
#             # files.append(('files', open(os.path.join(dirpath, file), 'rb')))
#             files.append(open(os.path.join(dirpath, file), 'rb'))
#
#     # response = api.post(URL+'/api/converter/file', files=files)
#     response = api.post(URL + '/api/converter/file', data={'files': files})
#
#     resp_body = json.loads(response.data)
#     print(resp_body)
#
#     data = {
#         "source": "local",
#         "config": {
#             "host": "10.1.31.195",
#             "port": 3000,
#             "user": "Administrator",
#             "password": "5f4dcc3b5aa765d61d8327deb882cf99"
#         },
#         "file": resp_body['fid']
#     }
#
#     print(data)
#     headers = {'Content-Type': 'application/json; charset=utf-8'}
#
#     response = api.post(URL + '/api/converter/job', data=json.dumps(data), headers=headers)
#
#     resp_body = json.loads(response.data)
#     rid = resp_body['rid']
#     print(rid)
#
#     while True:
#         response = api.get(URL + '/api/converter/job/'+ rid)
#         resp_body = json.loads(response.data)
#         print(resp_body['status'])
#         if resp_body['status'] == 'error':
#             break
#
#         time.sleep(1)
#
#     assert resp_body['status'] == 'error'


# def test_converter_rapid(api):
#     data = {
#         "source": "rapid",
#         "config": {
#             "host": "10.1.31.195",
#             "port": 3000,
#             "user": "Administrator",
#             "password": "5f4dcc3b5aa765d61d8327deb882cf99"
#         },
#         "before": 100,
#         "plan_id": [26],
#         "created": "2021-05-25 12:24:51",
#         "site": "BSOT"
#     }
#
#     print(data)
#     headers = {'Content-Type': 'application/json; charset=utf-8'}
#
#     response = api.post(URL + '/api/converter/job', data=json.dumps(data), headers=headers)
#
#     resp_body = json.loads(response.data)
#     rid = resp_body['rid']
#     print(rid)
#
#     while True:
#         response = api.get(URL + '/api/converter/job/'+ rid)
#         resp_body = json.loads(response.data)
#         print(resp_body['status'])
#         if resp_body['status'] == 'success':
#             break
#
#         time.sleep(1)
#
#     assert resp_body['status'] == 'success'
