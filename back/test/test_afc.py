import pytest
import json
import time
import os

from flaskapp.mpa_analysis_tool import create_app

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

#
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

    with open(os.path.join(VALIDATION_JSON_PATH, 'validation_afc.json'), 'r') as f:
        json_data = json.load(f)

    assert resp_body == json_data['lists_default']


def test_analysis_get_summary_default(api):
    global rid

    param = {
        "start": "2021-05-12 00:00:00",
        "end": "2021-05-12 23:59:59",
        "jobname": "SCAN3X2/SCANDBG"
    }
    print(param)

    response = api.get(URL + f'/api/analysis/summaries/{LOG_NAME}/{rid}', query_string=param)
    resp_body = json.loads(response.data)
    print(resp_body)

    with open(os.path.join(VALIDATION_JSON_PATH, 'validation_afc.json'), 'r') as f:
        json_data = json.load(f)

    assert resp_body == json_data['summary_default']


def test_analysis_get_detail_default(api):
    global rid

    param = {
        "start": "2021-05-12 00:00:00",
        "end": "2021-05-12 23:59:59",
        "jobname": "SCAN3X2/SCANDBG",
        "group_by": "column",
        "group_value": "lot_id",
        "group_selected": ["-Lot1-", "-Lot3-", "-Lot4-", "-Lot5-"],

    }
    print(param)

    response = api.get(URL + f'/api/analysis/details/{LOG_NAME}/{rid}', query_string=param)
    resp_body = json.loads(response.data)
    print(resp_body)

    with open(os.path.join(VALIDATION_JSON_PATH, 'validation_afc.json'), 'r') as f:
        json_data = json.load(f)

    assert resp_body == json_data['detail_default']


@pytest.mark.parametrize('one_period', ['12h', '24h'])
@pytest.mark.parametrize('adj_period', ['0h', '1h', '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', '10h', '11h',
                                        '12h', '13h', '14h', '15h', '16h', '17h', '18h', '19h', '20h', '21h', '22h',
                                        '23h'])
@pytest.mark.parametrize('list_group', [None, 'job'])
def test_converter_get_lists_hour(api, one_period, adj_period, list_group):
    global rid

    print(one_period, adj_period, list_group)
    params = {
        'one_period': one_period,
        'adj_period': adj_period,
        'list_group': list_group
    }

    response = api.get(URL + '/api/analysis/lists/' + LOG_NAME + '/' + rid, query_string=params)

    assert response.status_code == 200

    print(json.loads(response.data))

    # resp_body = response.json()
    #
    # with open(os.path.join(VALIDATION_JSON_PATH, 'validation_afc.json'), 'r') as f:
    #     json_data = json.load(f)
    #
    # assert resp_body == json_data


@pytest.mark.parametrize('one_period', ['7d', '14d', '1m'])
@pytest.mark.parametrize('adj_period', ['0d', '1d', '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', '10d',
                                        '11d', '12d', '13d', '14d', '15d', '16d', '17d', '18d', '19d', '20d',
                                        '21d', '22d', '23d', '24d', '25d', '26d', '27d', '28d', '29d', '30d', '31d'])
@pytest.mark.parametrize('list_group', [None, 'job'])
def test_converter_get_lists_day_month(api, one_period, adj_period, list_group):
    global rid

    print(one_period, adj_period, list_group)
    params = {
        'one_period': one_period,
        'adj_period': adj_period,
        'list_group': list_group
    }

    response = api.get(URL + '/api/analysis/lists/' + LOG_NAME + '/' + rid, query_string=params)

    assert response.status_code == 200

    print(json.loads(response.data))
