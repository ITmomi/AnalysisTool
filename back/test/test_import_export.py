import pytest
import os
import shutil
import base64
import json

from flaskapp.mpa_analysis_tool import create_app
from config.unit_test_config import *

URL = 'http://localhost:5000'
TEST_LOG_PATH = 'test/sample_log/import'
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


def test_import_export(api):
    response = api.get(URL + '/api/export/rules')

    assert response.status_code == 200

    filename = 'export.xlsx'
    with open(filename, 'wb') as f_out:
        f_out.write(response.get_data())

    if not os.path.exists(BACKUP_PATH):
        os.mkdir(BACKUP_PATH)

    files = []

    files.append(open(filename, 'rb'))

    # response = api.post(URL+'/api/converter/file', files=files)
    response = api.post(URL + '/api/import/rules', data={'files': files})

    # resp_body = json.loads(response.data)
    # print(resp_body)

    os.remove(filename)

    assert response.status_code == 200


def test_import_export_not_zip(api):
    response = api.get(URL + '/api/export/rules')

    assert response.status_code == 200

    filename = 'export.7z'
    with open(filename, 'wb') as f_out:
        f_out.write(response.get_data())

    files = []

    files.append(open(filename, 'rb'))

    # response = api.post(URL+'/api/converter/file', files=files)
    response = api.post(URL + '/api/import/rules', data={'files': files})

    # resp_body = json.loads(response.data)
    # print(resp_body)
    os.remove(filename)

    assert response.status_code == 400


def test_function_import_export(api):
    params = {
        'func_id': 1
    }

    response = api.get(URL + '/api/export/function', query_string=params)
    resp_body = json.loads(response.data)
    print(resp_body)

    assert response.status_code == 200

    filename = 'function_export.json'
    with open(filename, 'wb') as f_out:
        f_out.write(response.get_data())

    files = []

    files.append(open(filename, 'rb'))

    # response = api.post(URL+'/api/converter/file', files=files)
    response = api.post(URL + '/api/import/function', data={'files': files})

    # resp_body = json.loads(response.data)
    # print(resp_body)

    os.remove(filename)

    assert response.status_code == 200


# def test_import_export_no_match_table(api):
#     import_file = 'test/sample_log/import/no_match_table.zip'
#
#     shutil.copy(import_file, './no_match_table.zip')
#
#     files = []
#
#     files.append(open('no_match_table.zip', 'rb'))
#
#     # response = api.post(URL+'/api/converter/file', files=files)
#     response = api.post(URL + '/api/import', data={'files': files})
#
#     # resp_body = json.loads(response.data)
#     # print(resp_body)
#
#     os.remove('no_match_table.zip')
#
#     assert response.status_code == 400


# def test_import_export_data_error(api):
#     import_file = 'test/sample_log/import/data_error.zip'
#
#     shutil.copy(import_file, './data_error.zip')
#
#     files = []
#
#     files.append(open('data_error.zip', 'rb'))
#
#     # response = api.post(URL+'/api/converter/file', files=files)
#     response = api.post(URL + '/api/import', data={'files': files})
#
#     # resp_body = json.loads(response.data)
#     # print(resp_body)
#
#     os.remove('data_error.zip')
#
#     assert response.status_code == 500


# def test_export_graph(api):
#     import_file = 'test/sample_log/export_graph/summary.graph.png'
#
#     # shutil.copy(import_file, './summary.graph.png')
#
#     image = open(import_file, 'rb')
#     data = base64.b64encode(image.read())
#     image = open('summary.graph.png', 'wb')
#
#     image.write(b'data:image/png;base64,' + data)
#
#     image = open('summary.graph.png', 'rb')
#
#     files = {'files': image}
#
#     response = api.post(URL + '/api/export', data=files)
#
#     assert response.status_code == 200
#
#     filename = 'graph.zip'
#     with open(filename, 'wb') as f_out:
#         f_out.write(response.get_data())
#
#     os.remove('summary.graph.png')
