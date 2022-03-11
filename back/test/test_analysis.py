import pytest
import json
import time
import os

from flaskapp.mpa_analysis_tool import create_app
from dao.dao_management_setting import DAOMGMTSetting

URL = 'http://localhost:5000'
TEST_LOG_PATH = 'test/sample_log/PLATEAUTOFOCUSCOMPENSATION'
VALIDATION_JSON_PATH = 'test/validation_json'
LOG_NAME = 'PLATEAUTOFOCUSCOMPENSATION'

rid = None

@pytest.fixture
def api():
    config_file = '../config/unit_test_config.py'
    app = create_app(config_file)
    app.config['TESTING'] = True
    api = app.test_client()

    return api


def test_analysis_job(api):
    global rid
    files = []
    for dirpath, dirnames, filenames in os.walk(TEST_LOG_PATH):
        for file in filenames:
            # files.append(('files', open(os.path.join(dirpath, file), 'rb')))
            files.append(open(os.path.join(dirpath, file), 'rb'))

    # response = api.post(URL+'/api/converter/file', files=files)
    response = api.post('http://10.1.31.195:5000' + '/api/converter/file', data={'files': files})

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

    response = api.post('http://10.1.31.195:5000' + '/api/converter/job', data=json.dumps(data), headers=headers)

    assert response.status_code == 200

    resp_body = json.loads(response.data)
    rid = resp_body['rid']
    print(rid)

    while True:
        response = api.get('http://10.1.31.195:5000' + '/api/converter/job/'+ rid)
        resp_body = json.loads(response.data)
        print(resp_body['status'])
        if resp_body['status'] == 'success':
            break

        time.sleep(1)

    assert resp_body['status'] == 'success'


def test_analysis_remote_error_1(api):
    args = dict()

    args['target'] = 'remote'
    args['host'] = None
    dao_mgmt = DAOMGMTSetting()
    res_form = dao_mgmt.update_db_setting(**args)
    assert res_form.res is True

    params = {
        "period": '2021-05-11~2021-09-05'
    }
    print(params)

    response = api.post(URL + f'/api/analysis/remote/{LOG_NAME}/BSOT_s2_SBPCN480_G147', query_string=params)

    assert response.status_code == 500

    resp_body = json.loads(response.data)
    print(resp_body)


def test_analysis_remote_error_2(api):
    args = dict()

    args['target'] = 'remote'
    args['host'] = 'http://10.1.31.184'
    dao_mgmt = DAOMGMTSetting()
    res_form = dao_mgmt.update_db_setting(**args)
    assert res_form.res is True

    params = {
        "period": '2021-05-11-2021-09-05'
    }
    print(params)

    response = api.post(URL + f'/api/analysis/remote/{LOG_NAME}/BSOT_s2_SBPCN480_G147', query_string=params)

    assert response.status_code == 500

    resp_body = json.loads(response.data)
    print(resp_body)


def test_analysis_remote(api):
    # args = dict()
    #
    # args['target'] = 'remote'
    # args['host'] = 'http://10.1.31.184'
    # dao_mgmt = DAOMGMTSetting()
    # res_form = dao_mgmt.update_db_setting(**args)
    # assert res_form.res is True

    params = {
        "period": '2021-05-11~2021-09-05'
    }
    print(params)

    response = api.post(URL + f'/api/analysis/remote/{LOG_NAME}/BSOT_s2_SBPCN480_G147', query_string=params)

    assert response.status_code == 200

    resp_body = json.loads(response.data)
    print(resp_body)


def test_converter_get_lists_wrong_id(api):

    response = api.get(URL + '/api/analysis/lists/' + LOG_NAME + '/' + 'wrongid')

    assert response.status_code == 500

    resp_body = json.loads(response.data)
    print(resp_body)