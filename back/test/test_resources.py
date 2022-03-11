import pytest
import json
import time
import os
import shutil

from flaskapp.mpa_analysis_tool import create_app
from config import unit_test_config as config
from dao.dao_management_setting import DAOMGMTSetting

URL = 'http://localhost:5000'
TEST_LOG_PATH = 'test/sample_log/PLATEAUTOFOCUSCOMPENSATION'
VALIDATION_JSON_PATH = 'test/validation_json'
LOG_NAME = 'PLATEAUTOFOCUSCOMPENSATION'

@pytest.fixture
def api():
    config_file = '../config/unit_test_config.py'
    app = create_app(config_file)
    app.config['TESTING'] = True
    api = app.test_client()

    return api


def test_resources_main(api):
    response = api.get(URL + f'/api/resources/main')

    assert response.status_code == 200


def test_resources_about(api):
    response = api.get(URL + f'/api/resources/about')

    assert response.status_code == 200


def test_category(api):
    data = {
        'category': [
            {
                'category_id': None,
                'title': 'TEST'
            }
        ]
    }

    headers = {'Content-Type': 'application/json; charset=utf-8'}
    response = api.post(URL + f'/api/resources/main/category', data=json.dumps(data), headers=headers)
    resp_body = json.loads(response.data)

    assert response.status_code == 200

    title_list = list()
    for item in resp_body['body']:
        title_list.append(item['title'])

    assert 'TEST' in title_list


def test_new_step1(api):
    response = api.get(URL + f'/api/resources/new/step1')
    resp_body = json.loads(response.data)
    assert response.status_code == 200

    title_list = list()
    for item in resp_body['category']['options']:
        title_list.append(item['title'])

    assert 'TEST' in title_list


def test_new_step2(api):
    response = api.get(URL + f'/api/resources/new/step2')
    resp_body = json.loads(response.data)

    assert response.status_code == 200


def test_new_step3(api):
    response = api.get(URL + f'/api/resources/new/step3')
    resp_body = json.loads(response.data)

    assert response.status_code == 200


def test_new_step3_addrule(api):
    log_name = 'PLATEAUTOFOCUSCOMPENSATION'
    response = api.get(URL + f'/api/resources/new/step3/{log_name}')
    resp_body = json.loads(response.data)

    assert response.status_code == 200


def test_base_rule(api):
    log_name = 'PLATEAUTOFOCUSCOMPENSATION'
    rule_id = 9
    response = api.get(URL + f'/api/resources/{log_name}/{rule_id}')
    resp_body = json.loads(response.data)

    assert response.status_code == 200
    assert 'convert' in resp_body

    convert = resp_body['convert']

    item_list = ['info', 'header', 'custom', 'columns']
    key_list = [key for key in convert.keys()]
    for item in item_list:
        assert item in key_list

    log_name = 'a'
    response = api.get(URL + f'/api/resources/{log_name}/{rule_id}')
    resp_body = json.loads(response.data)

    assert response.status_code == 200
    assert 'convert' in resp_body

    convert = resp_body['convert']

    item_list = ['info', 'header', 'custom', 'columns']
    key_list = [key for key in convert.keys()]
    for item in item_list:
        assert item in key_list


def test_new(api):
    with open(os.path.join(VALIDATION_JSON_PATH, 'new_function.json'), 'r') as f:
        json_data = json.load(f)

    headers = {'Content-Type': 'application/json; charset=utf-8'}

    response = api.post(URL + '/api/resources/new', data=json.dumps(json_data), headers=headers)
    resp_body = json.loads(response.data)

    assert response.status_code == 200

    func_id = resp_body['func_id']

    script_file_path = 'resource/script'
    script_file_name = 'preprocess.py'
    shutil.copy(os.path.join(script_file_path, script_file_name), script_file_name)

    files = {
        'preprocess': open(script_file_name, 'rb'),
        'analysis': open(script_file_name, 'rb')
    }

    response = api.post(URL + f'/api/resources/scripts/{func_id}', data=files)
    if response.status_code != 200:
        resp_body = json.loads(response.data)
        print(resp_body)

    assert response.status_code == 200


def test_edit_step1(api):
    response = api.get(URL + f'/api/resources/edit/step1')
    resp_body = json.loads(response.data)
    assert response.status_code == 200


def test_edit_step2(api):
    func_id = 6
    response = api.get(URL + f'/api/resources/edit/step2/{func_id}')
    resp_body = json.loads(response.data)

    assert response.status_code == 200

    rule_list = list()
    for item in resp_body['items']:
        for sub_item in item['items']:
            if sub_item['target'] == 'rule_name':
                for rule in sub_item['options']:
                    if rule['id'] is not None:
                        rule_list.append(rule['id'])

    if len(rule_list):
        rule_id = rule_list[0]
        response = api.delete(URL + f'/api/resources/rule/{rule_list[0]}')
        resp_body = json.loads(response.data)

        assert response.status_code == 200

        resp_list = list()
        for item in resp_body['options']:
            if item['id'] is not None:
                resp_list.append(item['id'])

        assert rule_id not in resp_list


def test_edit_step3_addrule(api):
    log_name = 'PLATEAUTOFOCUSCOMPENSATION'
    func_id = 1
    response = api.get(URL + f'/api/resources/edit/step3/{func_id}/{log_name}')
    resp_body = json.loads(response.data)

    assert response.status_code == 200


def test_remote_tables(api):
    db_id = 19
    response = api.get(URL + f'/api/resources/remote/tables/{db_id}')
    resp_body = json.loads(response.data)

    assert response.status_code == 200
    assert type(resp_body) == list


def test_remote_equipments(api):
    db_id = 19
    table_name = 'adc_measurement'
    response = api.get(URL + f'/api/resources/remote/equipments/{db_id}/{table_name}')
    resp_body = json.loads(response.data)

    assert response.status_code == 200
    assert 'user_fab' in resp_body
    assert 'equipment_name' in resp_body


def test_remote_date(api):
    db_id = 19
    table_name = 'adc_measurement'
    equipment_name = 'BSOT_Fab1_MPA_1'
    response = api.get(URL + f'/api/resources/remote/date/{db_id}/{table_name}/{equipment_name}')
    resp_body = json.loads(response.data)

    assert response.status_code == 200
    assert 'start' in resp_body
    assert 'end' in resp_body


# OLD
# def test_resources_job(api):
#     global rid
#     files = []
#     for dirpath, dirnames, filenames in os.walk(TEST_LOG_PATH):
#         for file in filenames:
#             # files.append(('files', open(os.path.join(dirpath, file), 'rb')))
#             files.append(open(os.path.join(dirpath, file), 'rb'))
#
#     # response = api.post(URL+'/api/converter/file', files=files)
#     response = api.post('http://10.1.31.195:5000' + '/api/converter/file', data={'files': files})
#
#     resp_body = json.loads(response.data)
#     print(resp_body)
#
#     data = {
#         "log_name": LOG_NAME,
#         "source": "local",
#         "file": resp_body['fid'],
#         "equipment_type": "G803"
#     }
#     print(data)
#     headers = {'Content-Type': 'application/json; charset=utf-8'}
#
#     response = api.post('http://10.1.31.195:5000' + '/api/converter/job', data=json.dumps(data), headers=headers)
#
#     assert response.status_code == 200
#
#     resp_body = json.loads(response.data)
#     rid = resp_body['rid']
#     print(rid)
#
#     while True:
#         response = api.get('http://10.1.31.195:5000' + '/api/converter/job/'+ rid)
#         resp_body = json.loads(response.data)
#         print(resp_body['status'])
#         if resp_body['status'] == 'success':
#             break
#
#         time.sleep(1)
#
#     assert resp_body['status'] == 'success'
#
#
# def test_main_page(api):
#     response = api.get(URL + '/main')
#
#     assert response.status_code == 200
#
#     response = api.get(URL + '/js/app.e1d1fed5b7d3a8653a20.js')
#
#     assert response.status_code == 200
#
#     response = api.get(URL + '/fonts/memjYa2wxmKQyPMrZX79wwYZQMhsyuSLhovSZSk.woff2')
#
#     assert response.status_code == 200
#
#     response = api.get(URL + '/app.css')
#
#     assert response.status_code == 200
#

#
#

#
# def test_resources_mgmt(api):
#     response = api.get(URL + f'/api/resources/mgmt')
#
#     assert response.status_code == 200
#
#     resp_body = json.loads(response.data)
#     print(resp_body)
#
#
# def test_resources_settings_afc(api):
#     dao_mgmt = DAOMGMTSetting()
#
#     dao_mgmt.execute(
#         '''
#         update settings.management_setting set host=null where target='remote'
#         '''
#         )
#
#     response = api.get(URL + f'/api/resources/settings/afc')
#
#     assert response.status_code == 200
#
#     resp_body = json.loads(response.data)
#     print(resp_body)
#
#     args = dict()
#     args['target'] = 'remote'
#     args['host'] = 'http://10.1.31.184'
#
#     res_form = dao_mgmt.update_db_setting(**args)
#     assert res_form.res is True
#
#     response = api.get(URL + f'/api/resources/settings/afc')
#
#     assert response.status_code == 200
#
#     resp_body = json.loads(response.data)
#     print(resp_body)
#
# def test_resources_settings_prescan(api):
#     response = api.get(URL + f'/api/resources/settings/prescan')
#
#     assert response.status_code == 200
#
#     resp_body = json.loads(response.data)
#     print(resp_body)
#
#
# def test_resources_settings_tiltmeasure(api):
#     response = api.get(URL + f'/api/resources/settings/tiltmeasure')
#
#     assert response.status_code == 200
#
#     resp_body = json.loads(response.data)
#     print(resp_body)
#
#
# def test_resources_settings_mountpress(api):
#     response = api.get(URL + f'/api/resources/settings/mountpress')
#
#     assert response.status_code == 200
#
#     resp_body = json.loads(response.data)
#     print(resp_body)
#
#
# def test_resources_settings_lipsfocus(api):
#     response = api.get(URL + f'/api/resources/settings/lipsfocus')
#
#     assert response.status_code == 200
#
#     resp_body = json.loads(response.data)
#     print(resp_body)
#
#
# def test_resources_settings_date(api):
#     dao_mgmt = DAOMGMTSetting()
#
#     dao_mgmt.execute(
#         '''
#         update settings.management_setting set host=null where target='remote'
#         '''
#         )
#
#     response = api.get(URL + f'/api/resources/settings/date/PLATEAUTOFOCUSCOMPENSATION/BSOT_s2_SBPCN480_G147')
#
#     assert response.status_code == 400
#
#     resp_body = json.loads(response.data)
#     print(resp_body)
#
#     args = dict()
#     args['target'] = 'remote'
#     args['host'] = 'http://10.1.31.184/'
#
#     res_form = dao_mgmt.update_db_setting(**args)
#     assert res_form.res is True
#
#     response = api.get(URL + f'/api/resources/settings/date/PLATEAUTOFOCUSCOMPENSATION/BSOT_s2_SBPCN480_G147')
#
#     resp_body = json.loads(response.data)
#     print(resp_body)
#
#     assert response.status_code == 200
