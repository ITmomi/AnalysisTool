import pytest
import json
import os
import shutil

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

def test_preview_step2_local(api):
    files = []
    filepath = 'test/sample_log'
    filename = '20210901_TEST.txt'
    shutil.copy(os.path.join(filepath, filename), filename)

    files.append(open(filename, 'rb'))

    script_file_path = 'resource/script'
    script_file_name = 'preprocess.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)
    script_file = [open(script_file_name, 'rb')]

    params = {
        'source': 'local',
        'use_script': True
    }

    # response = api.post(URL+'/api/converter/file', files=files)
    response = api.post(URL + '/api/preview/samplelog', data={'files': files, 'script_file': script_file}, query_string=params)
    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200


def test_preview_step2_remote(api):
    files = []
    filepath = 'test/sample_log'
    filename = '20210901_TEST.txt'
    shutil.copy(os.path.join(filepath, filename), filename)

    files.append(open(filename, 'rb'))

    script_file_path = 'resource/script'
    script_file_name = 'preprocess.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)
    script_file = [open(script_file_name, 'rb')]

    params = {
        'source': 'remote',
        'use_script': True,
        'equipment_name': 'BSOT_Fab1_MPA_2',
        'table_name': 'adc_measurement',
        'db_id': 2,
        'start': '2019-05-21 12:25:35',
        'end': '2019-05-22 12:25:35'
    }

    # response = api.post(URL+'/api/converter/file', files=files)
    response = api.post(URL + '/api/preview/samplelog', data={'files': files, 'script_file': script_file}, query_string=params)
    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200


def test_preview_step2_sql(api):
    files = []
    filepath = 'test/sample_log'
    filename = '20210901_TEST.txt'
    shutil.copy(os.path.join(filepath, filename), filename)

    files.append(open(filename, 'rb'))

    script_file_path = 'resource/script'
    script_file_name = 'preprocess.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)
    script_file = [open(script_file_name, 'rb')]

    params = {
        'source': 'sql',
        'use_script': True,
        'db_id': 2,
        'sql': "select * from adc_measurement where log_time >= '2019-05-21 12:25:35' and log_time <= '2019-05-22 12:25:35'"
               " and equipment_name='BSOT_Fab1_MPA_2'"
    }

    # response = api.post(URL+'/api/converter/file', files=files)
    response = api.post(URL + '/api/preview/samplelog', data={'files': files, 'script_file': script_file}, query_string=params)
    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200


def test_preview_convert(api):
    # case1
    # 샘플 데이터 O, 룰 정보 O, Script 사용 O
    json_data = []
    filepath = VALIDATION_JSON_PATH
    filename = 'convert_preview_sample.json'
    shutil.copy(os.path.join(filepath, filename), filename)

    json_data.append(open(filename, 'rb'))

    script_file_path = 'resource/script'
    script_file_name = 'convert.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)
    script_file = [open(script_file_name, 'rb')]

    params = {
        'use_script': 'true'
    }

    response = api.post(URL + '/api/preview/convert', data={'json_data': json_data, 'script_file': script_file},
                        query_string=params)
    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200

    # case2
    # 샘플 데이터 O, 룰 정보 O, Script 사용 X
    json_data = []
    filepath = VALIDATION_JSON_PATH
    filename = 'convert_preview_sample.json'
    shutil.copy(os.path.join(filepath, filename), filename)

    json_data.append(open(filename, 'rb'))

    script_file_path = 'resource/script'
    script_file_name = 'convert.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)
    script_file = [open(script_file_name, 'rb')]

    params = {
        'use_script': False
    }

    response = api.post(URL + '/api/preview/convert', data={'json_data': json_data, 'script_file': script_file},
                        query_string=params)
    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200

    # # case3
    # # 샘플 데이터 O, 룰 정보 X, Script 사용 O
    json_data = []
    filepath = VALIDATION_JSON_PATH
    filename = 'convert_preview_sample_no_rule.json'
    shutil.copy(os.path.join(filepath, filename), filename)

    json_data.append(open(filename, 'rb'))

    script_file_path = 'resource/script'
    script_file_name = 'convert.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)
    script_file = [open(script_file_name, 'rb')]

    params = {
        'use_script': 'true'
    }

    response = api.post(URL + '/api/preview/convert', data={'json_data': json_data, 'script_file': script_file},
                        query_string=params)
    # resp_body = json.loads(response.data)
    # print(resp_body)

    assert response.status_code == 400
    #
    # # case4
    # # 샘플 데이터 O, 룰 정보 X, Script 사용 X
    json_data = []
    filepath = VALIDATION_JSON_PATH
    filename = 'convert_preview_sample_no_rule.json'
    shutil.copy(os.path.join(filepath, filename), filename)

    json_data.append(open(filename, 'rb'))

    script_file_path = 'resource/script'
    script_file_name = 'convert.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)
    script_file = [open(script_file_name, 'rb')]

    params = {
        'use_script': False
    }

    response = api.post(URL + '/api/preview/convert', data={'json_data': json_data, 'script_file': script_file},
                        query_string=params)
    # resp_body = json.loads(response.data)
    # print(resp_body)

    assert response.status_code == 400

    # case5
    # 샘플 데이터 X, 룰 정보 O, Script 사용 O
    json_data = []
    filepath = VALIDATION_JSON_PATH
    filename = 'convert_preview_sample_no_data.json'
    shutil.copy(os.path.join(filepath, filename), filename)

    json_data.append(open(filename, 'rb'))

    script_file_path = 'resource/script'
    script_file_name = 'convert.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)
    script_file = [open(script_file_name, 'rb')]

    params = {
        'use_script': 'true'
    }

    response = api.post(URL + '/api/preview/convert', data={'json_data': json_data, 'script_file': script_file},
                        query_string=params)
    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200

    # case6
    # 샘플 데이터 X, 룰 정보 O, Script 사용 X
    json_data = []
    filepath = VALIDATION_JSON_PATH
    filename = 'convert_preview_sample_no_data.json'
    shutil.copy(os.path.join(filepath, filename), filename)

    json_data.append(open(filename, 'rb'))

    script_file_path = 'resource/script'
    script_file_name = 'convert.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)
    script_file = [open(script_file_name, 'rb')]

    params = {
        'use_script': False
    }

    response = api.post(URL + '/api/preview/convert', data={'json_data': json_data, 'script_file': script_file},
                        query_string=params)
    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200

    # case7
    # 샘플 데이터 X, 룰 정보 X, Script 사용 O
    json_data = []
    filepath = VALIDATION_JSON_PATH
    filename = 'convert_preview_sample_no_data_rule.json'
    shutil.copy(os.path.join(filepath, filename), filename)

    json_data.append(open(filename, 'rb'))

    script_file_path = 'resource/script'
    script_file_name = 'convert.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)
    script_file = [open(script_file_name, 'rb')]

    params = {
        'use_script': 'true'
    }

    response = api.post(URL + '/api/preview/convert', data={'json_data': json_data, 'script_file': script_file},
                        query_string=params)
    # resp_body = json.loads(response.data)
    # print(resp_body)

    assert response.status_code == 400

    # case8
    # 샘플 데이터 X, 룰 정보 X, Script 사용 X
    json_data = []
    filepath = VALIDATION_JSON_PATH
    filename = 'convert_preview_sample_no_data_rule.json'
    shutil.copy(os.path.join(filepath, filename), filename)

    json_data.append(open(filename, 'rb'))

    script_file_path = 'resource/script'
    script_file_name = 'convert.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)
    script_file = [open(script_file_name, 'rb')]

    params = {
        'use_script': False
    }

    response = api.post(URL + '/api/preview/convert', data={'json_data': json_data, 'script_file': script_file},
                        query_string=params)
    # resp_body = json.loads(response.data)
    # print(resp_body)

    assert response.status_code == 400


def test_preview_converted(api):
    # case1
    # 샘플 데이터 O, 룰 정보 X, Script 사용 O
    json_data = []
    filepath = VALIDATION_JSON_PATH
    filename = 'convert_preview_sample_no_rule.json'
    shutil.copy(os.path.join(filepath, filename), filename)

    json_data.append(open(filename, 'rb'))

    script_file_path = 'resource/script'
    script_file_name = 'convert.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)
    script_file = [open(script_file_name, 'rb')]

    params = {
        'use_script': 'true'
    }

    response = api.post(URL + '/api/preview/converted', data={'json_data': json_data, 'script_file': script_file},
                        query_string=params)
    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200

    # case2
    # 샘플 데이터 O, 룰 정보 X, Script 사용 X
    json_data = []
    filepath = VALIDATION_JSON_PATH
    filename = 'convert_preview_sample_no_rule.json'
    shutil.copy(os.path.join(filepath, filename), filename)

    json_data.append(open(filename, 'rb'))

    script_file_path = 'resource/script'
    script_file_name = 'convert.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)
    script_file = [open(script_file_name, 'rb')]

    params = {
        'use_script': False
    }

    response = api.post(URL + '/api/preview/converted', data={'json_data': json_data, 'script_file': script_file},
                        query_string=params)
    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200

    # case3
    # 샘플 데이터 X, 룰 정보 X, Script 사용 O
    json_data = []
    filepath = VALIDATION_JSON_PATH
    filename = 'convert_preview_sample_no_data_rule.json'
    shutil.copy(os.path.join(filepath, filename), filename)

    json_data.append(open(filename, 'rb'))

    script_file_path = 'resource/script'
    script_file_name = 'convert.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)
    script_file = [open(script_file_name, 'rb')]

    params = {
        'use_script': 'true'
    }

    response = api.post(URL + '/api/preview/converted', data={'json_data': json_data, 'script_file': script_file},
                        query_string=params)
    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200

    # case4
    # 샘플 데이터 X, 룰 정보 X, Script 사용 X
    json_data = []
    filepath = VALIDATION_JSON_PATH
    filename = 'convert_preview_sample_no_data_rule.json'
    shutil.copy(os.path.join(filepath, filename), filename)

    json_data.append(open(filename, 'rb'))

    script_file_path = 'resource/script'
    script_file_name = 'convert.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)
    script_file = [open(script_file_name, 'rb')]

    params = {
        'use_script': False
    }

    response = api.post(URL + '/api/preview/converted', data={'json_data': json_data, 'script_file': script_file},
                        query_string=params)
    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200


def test_preview_filter(api):
    data = {
        "data": {
            "disp_order": [
                "status",
                "flt",
                "frt",
                "blt",
                "brt",
                "pitching",
                "rolling",
                "torsion",
                "deflection",
                "log_time"
            ],
            "row": {
                "1": {
                    "status": 0,
                    "flt": 64556,
                    "frt": 70803,
                    "blt": 69460,
                    "brt": 65765,
                    "pitching": -7,
                    "rolling": -239,
                    "torsion": -4,
                    "deflection": "*",
                    "log_time": "2021-10-01 12:45:28"
                },
                "2": {
                    "status": 0,
                    "flt": 62446,
                    "frt": 70005,
                    "blt": 71119,
                    "brt": 68889,
                    "pitching": 411,
                    "rolling": -499,
                    "torsion": -4,
                    "deflection": "*",
                    "log_time": "2021-10-01 18:39:33"
                },
                "3": {
                    "status": 0,
                    "flt": 64882,
                    "frt": 71203,
                    "blt": 69706,
                    "brt": 65858,
                    "pitching": -28,
                    "rolling": -231,
                    "torsion": -5,
                    "deflection": "*",
                    "log_time": "2021-10-01 18:39:46"
                }
            }
        },
        "filter": {
            "items": [
                {
                    "name": "filter1",
                    "type": "base_sampler",
                    "condition": "2"
                }
            ]
        }
    }

    headers = {'Content-Type': 'application/json; charset=utf-8'}

    response = api.post(URL + '/api/preview/filter', data=json.dumps(data), headers=headers)

    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200


def test_preview_analysis(api):
    # case1
    # setting
    json_data = []
    filepath = VALIDATION_JSON_PATH
    filename = 'analysis_preview_sample_setting.json'
    shutil.copy(os.path.join(filepath, filename), filename)

    json_data.append(open(filename, 'rb'))

    response = api.post(URL + '/api/preview/analysis', data={'json_data': json_data})
    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200

    # case2
    # script
    json_data = []
    filepath = VALIDATION_JSON_PATH
    filename = 'analysis_preview_sample_script.json'
    shutil.copy(os.path.join(filepath, filename), filename)

    json_data.append(open(filename, 'rb'))

    script_file_path = 'resource/script'
    script_file_name = 'generic_analysis.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)
    script_file = [open(script_file_name, 'rb')]

    params = {
        'use_script': 'true'
    }

    response = api.post(URL + '/api/preview/analysis', data={'json_data': json_data, 'script_file': script_file},
                        query_string=params)
    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200

    # case3
    # none
    json_data = []
    filepath = VALIDATION_JSON_PATH
    filename = 'analysis_preview_sample_none.json'
    shutil.copy(os.path.join(filepath, filename), filename)

    json_data.append(open(filename, 'rb'))

    response = api.post(URL + '/api/preview/analysis', data={'json_data': json_data})
    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200


def test_preview_sql(api):
    data = {
        'db_id': 3,
        'sql': "select log_time from adc_measurement where log_time > '2019-05-21' and log_time < '2019-05-31'"
    }

    headers = {'Content-Type': 'application/json; charset=utf-8'}

    response = api.post(URL + '/api/preview/sql', data=json.dumps(data), headers=headers)

    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200
