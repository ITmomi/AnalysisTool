import pytest
import os
from flask import Response, request, make_response, jsonify
import json
import time
from flask import Flask, render_template, g, send_from_directory
from common.utils.response import make_json_response
from config.unit_test_config import *
from flaskapp.mpa_analysis_tool import create_app

URL = 'http://localhost:5000'

@pytest.fixture
def api():
    config_file = '../config/unit_test_config.py'
    app = create_app(config_file)
    app.config['TESTING'] = True
    api = app.test_client()

    return api

def test_convertor_job(api):
    app = Flask(__name__, static_folder='../web/static/', template_folder='../web/static')

    @app.route('/main', methods=['GET'])
    def catch_all():
        g.jinja2_test = 'made by gtttpark!'
        return render_template('index.html')

    @app.route('/main/notsupport', methods=['GET'])
    def nosupport():
        return render_template('notsupport.html')

    @app.route('/main/<path:filename>', methods=['GET'])
    def nosupport_svg(filename):
        root_dir = os.getcwd()
        return send_from_directory(os.path.join(root_dir, STATIC_PATH), filename)

    @app.route('/js/<path:filename>')
    def serve_static_js(filename):
        root_dir = os.getcwd()
        print(root_dir, STATIC_JS_PATH, filename)
        print(os.path.join(root_dir, STATIC_JS_PATH))
        return send_from_directory(os.path.join(root_dir, STATIC_JS_PATH), filename)

    @app.route('/<path:filename>')
    def serve_static(filename):
        root_dir = os.getcwd()
        return send_from_directory(os.path.join(root_dir, STATIC_PATH), filename)

    @app.route('/fonts/<path:filename>')
    def serve_static_fonts(filename):
        root_dir = os.getcwd()
        return send_from_directory(os.path.join(root_dir, STATIC_PONTS_PATH), filename)

    @app.route('/api/resources/main', methods=['GET'])
    def resources_main():
        print(f'[{request.method}]/api/resources/main')
        response = api.get('http://localhost:5000/api/resources/main')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    # resources
    @app.route('/api/resources/about', methods=['GET'])
    def resources_about():
        print(f'[{request.method}]/api/resources/about')
        response = api.get('http://localhost:5000/api/resources/about')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/<string:page>', methods=['GET'])
    def resources_page(page):
        print(f'[{request.method}]/api/resources/{page}')
        response = api.get(f'http://localhost:5000/api/resources/{page}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/settings/<int:func_id>', methods=['GET'])
    def resources_settings(func_id):
        print(f'[{request.method}]/api/resources/settings/{func_id}')
        response = api.get(f'http://localhost:5000/api/resources/settings/{func_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/settings/history/<int:history_id>', methods=['GET'])
    def resources_settings_history(history_id):
        print(f'[{request.method}]/api/resources/settings/history/{history_id}')
        response = api.get(f'http://localhost:5000/api/resources/settings/history/{history_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/settings/date/<string:log_name>/<string:equipment>', methods=['GET'])
    def resources_settings_date(log_name, equipment):
        print(f'[{request.method}]/api/resources/settings/date/{log_name}/{equipment}')
        response = api.get(f'http://localhost:5000/api/resources/settings/history/{log_name}/{equipment}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/main/category', methods=['POST'])
    def resources_main_category():
        print(f'[{request.method}]/api/resources/main/category')
        response = api.post('http://localhost:5000/api/resources/main/category')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/new/step1', methods=['GET'])
    def resources_new_step1():
        print(f'[{request.method}]/api/resources/new/step1')
        response = api.get('http://localhost:5000/api/resources/new/step1')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/new/step2', methods=['GET'])
    def resources_new_step2():
        print(f'[{request.method}]/api/resources/new/step2')
        response = api.get('http://localhost:5000/api/resources/new/step2')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/new/step2/settings/<int:func_id>', methods=['GET'])
    def resources_new_step2_settings(func_id):
        print(f'[{request.method}]/api/resources/new/step2/settings/{func_id}')
        response = api.get(f'http://localhost:5000/api/resources/new/step2/settings/{func_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/remote/tables/<int:db_id>', methods=['GET'])
    def resources_remote_tables(db_id):
        print(f'[{request.method}]/api/resources/remote/tables/{db_id}')
        response = api.get(f'http://localhost:5000/api/resources/remote/tables/{db_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/remote/equipments/<int:db_id>/<string:table_name>', methods=['GET'])
    def resources_remote_equipments(db_id, table_name):
        print(f'[{request.method}]/api/resources/remote/equipments/{db_id}/{table_name}')
        response = api.get(f'http://localhost:5000/api/resources/remote/equipments/{db_id}/{table_name}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/remote/date/<int:db_id>/<string:table_name>/<string:equipment_name>')
    def resources_date(db_id, table_name, equipment_name, methods=['GET']):
        print(f'[{request.method}]/api/resources/remote/date/{db_id}/{table_name}/{equipment_name}')
        response = api.get(f'http://localhost:5000/api/resources/remote/date/{db_id}/{table_name}/{equipment_name}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/new/step3', methods=['GET'])
    def resources_new_step3():
        print(f'[{request.method}]/api/resources/new/step3')
        response = api.get('http://localhost:5000/api/resources/new/step3')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/new/step3/<string:log_name>', methods=['GET'])
    def resources_new_step3_logname(log_name):
        print(f'[{request.method}]/api/resources/new/step3/{log_name}')
        response = api.get(f'http://localhost:5000/api/resources/new/step3/{log_name}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/<string:log_name>/<int:rule_id>', methods=['GET'])
    def resources(log_name, rule_id):
        print(f'[{request.method}]/api/resources/{log_name}/{rule_id}')
        response = api.get(f'http://localhost:5000/api/resources/{log_name}/{rule_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/new', methods=['POST'])
    def resources_new():
        print(f'[{request.method}]/api/resources/new')
        data = request.json
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = api.post('http://localhost:5000/api/resources/new', data=json.dumps(data), headers=headers)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/scripts/<int:func_id>', methods=['POST'])
    def resources_scripts(func_id):
        print(f'[{request.method}]/api/resources/scripts/{func_id}')
        response = api.post(f'http://localhost:5000/api/resources/scripts/{func_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/edit/step1/<int:func_id>', methods=['GET'])
    def resources_edit_step1(func_id):
        print(f'[{request.method}]/api/resources/edit/step1/{func_id}')
        response = api.get(f'http://localhost:5000/api/resources/edit/step1/{func_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/edit/step2/<string:func_id>', methods=['GET'])
    def resources_edit_step2(func_id):
        print(f'[{request.method}]/api/resources/edit/step2/{func_id}')
        response = api.get(f'http://localhost:5000/api/resources/edit/step2/{func_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/rule/<int:rule_id>', methods=['DELETE'])
    def resources_rule(rule_id):
        print(f'[{request.method}]/api/resources/rule/{rule_id}')
        response = api.delete(f'http://localhost:5000/api/resources/rule/{rule_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/edit/step3/<int:func_id>/<string:log_name>', methods=['GET'])
    def resources_edit_step3(func_id, log_name):
        print(f'[{request.method}]/api/resources/edit/step3/{func_id}/{log_name}')
        response = api.get(f'http://localhost:5000/api/resources/edit/step3/{func_id}/{log_name}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/edit/step3/<int:func_id>', methods=['GET'])
    def resources_edit_step3_nolog(func_id, log_name):
        print(f'[{request.method}]/api/resources/edit/step3/{func_id}')
        response = api.get(f'http://localhost:5000/api/resources/edit/step3/{func_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/edit/step3/<int:func_id>/<string:log_name>/<int:rule_id>', methods=['GET'])
    def resources_edit_step3_rule(func_id, log_name, rule_id):
        print(f'[{request.method}]/api/resources/edit/step3/{func_id}/{log_name}/{rule_id}')
        response = api.get(f'http://localhost:5000/api/resources/edit/step3/{func_id}/{log_name}/{rule_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/edit/<int:func_id>', methods=['POST'])
    def resources_edit(func_id):
        print(f'[{request.method}]/api/resources/edit/{func_id}')
        response = api.post(f'http://localhost:5000/api/resources/edit/{func_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/func/<int:func_id>', methods=['DELETE'])
    def resources_func(func_id):
        print(f'[{request.method}]/api/resources/func/{func_id}')
        response = api.delete(f'http://localhost:5000/api/resources/func/{func_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/graph/<int:func_id>', methods=['POST'])
    def resources_graph(func_id):
        print(f'[{request.method}]/api/resources/graph/{func_id}')
        response = api.post(f'http://localhost:5000/api/resources/graph/{func_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/resources/graph/<int:func_id>/<int:graph_id>', methods=['PUT'])
    def resources_graph_id(func_id, graph_id):
        print(f'[{request.method}]/api/resources/graph/{func_id}/{graph_id}')
        response = api.put(f'http://localhost:5000/api/resources/graph/{func_id}/{graph_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    # preview
    @app.route('/api/preview/samplelog', methods=['POST'])
    def preview_samplelog():
        print(f'[{request.method}]/api/preview/samplelog')
        response = api.post('http://localhost:5000/api/preview/samplelog', query_string=request.form, data=request.files)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/preview/samplelog/multi', methods=['POST'])
    def preview_samplelog_multi():
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        print(f'[{request.method}]/api/preview/samplelog/multi')
        print(f'request.form : {request.form}')
        print(f'request.args : {request.args}')
        print(f'request.data : {request.data}')
        # response = api.post('http://localhost:5000/api/preview/samplelog/multi', query_string=request.form)
        response = api.post('http://localhost:5000/api/preview/samplelog/multi', data=request.data, headers=headers)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/preview/convert', methods=['POST'])
    def preview_convert():
        print(f'[{request.method}]/api/preview/convert')
        response = api.post('http://localhost:5000/api/preview/convert', query_string=request.form, data=request.files)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/preview/converted', methods=['POST'])
    def preview_converted():
        print(f'[{request.method}]/api/preview/converted')
        response = api.post('http://localhost:5000/api/preview/converted', query_string=request.form, data=request.files)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/preview/filter', methods=['POST'])
    def preview_filter():
        print(f'[{request.method}]/api/preview/filter')
        data = request.json
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = api.post('http://localhost:5000/api/preview/filter', data=json.dumps(data), headers=headers)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/preview/analysis', methods=['POST'])
    def preview_analysis():
        print(f'[{request.method}]/api/preview/analysis')
        response = api.post('http://localhost:5000/api/preview/analysis', query_string=request.form, data=request.files)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/preview/analysis/multi', methods=['POST'])
    def preview_analysis_multi():
        print(f'[{request.method}]/api/preview/analysis/multi')
        response = api.post('http://localhost:5000/api/preview/analysis/multi', query_string=request.form, data=request.files)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/preview/sql', methods=['POST'])
    def preview_sql():
        print(f'[{request.method}]/api/preview/sql')
        response = api.post('http://localhost:5000/api/preview/sql', query_string=request.form)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    # setting
    @app.route('/api/setting/local', methods=['GET'])
    def setting_local():
        print(f'[{request.method}]/api/setting/local')
        response = api.get('http://localhost:5000/api/setting/local')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/setting/remote', methods=['GET'])
    def setting_remote():
        print(f'[{request.method}]/api/setting/remote')
        response = api.get('http://localhost:5000/api/setting/remote')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/setting/tables', methods=['GET'])
    def setting_tables():
        print('/api/setting/tables')
        response = api.get('http://localhost:5000/api/setting/tables')
        tmp_str = response.data.decode('ascii')
        response = make_response(jsonify(eval(tmp_str)), 200)
        return response

    @app.route('/remote/<int:db_id>/status', methods=['GET'])
    def setting_remote_dbid_status(db_id):
        print(f'[{request.method}]/api/setting/remote/{db_id}/status')
        response = api.get(f'http://localhost:5000/api/setting/remote/{db_id}/status')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/remote/<int:db_id>', methods=['GET', 'PUT', 'DELETE'])
    def setting_remote_dbid(db_id):
        print(f'[{request.method}]/api/setting/remote/{db_id}')
        if request.method == 'GET':
            response = api.get(f'http://localhost:5000/api/setting/remote/{db_id}', query_string=request.form)
        elif request.method == 'DELLETE':
            response = api.delete(f'http://localhost:5000/api/setting/remote/{db_id}', query_string=request.form)
        else:
            response = api.put(f'http://localhost:5000/api/setting/remote/{db_id}', query_string=request.form)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/connection-check', methods=['POST'])
    def setting_connectioncheck():
        print(f'[{request.method}]/api/setting/connection-check')
        response = api.post('http://localhost:5000/api/setting/connection-check', query_string=request.form)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    # analysis
    @app.route('/api/analysis/default/local/<int:func_id>/<string:rid>', methods=['GET'])
    def analysis_default_local(func_id, rid):
        print(f'[{request.method}]/api/analysis/default/local/{func_id}/{rid}')
        response = api.get(f'http://localhost:5000/api/analysis/default/local/{func_id}/{rid}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/analysis/default/remote/<int:func_id>/<string:rid>', methods=['GET'])
    def analysis_default_remote(func_id, rid):
        print(f'[{request.method}]/api/analysis/default/remote/{func_id}/{rid}')
        response = api.get(f'http://localhost:5000/api/analysis/default/remote/{func_id}/{rid}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/analysis/default/sql/<int:func_id>/<string:rid>', methods=['GET'])
    def analysis_default_sql(func_id, rid):
        print(f'[{request.method}]/api/analysis/default/sql/{func_id}/{rid}')
        response = api.get(f'http://localhost:5000/api/analysis/default/sql/{func_id}/{rid}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/analysis/default/history/<int:func_id>/<int:history_id>', methods=['GET'])
    def analysis_default_history(func_id, history_id):
        print(f'[{request.method}]/api/analysis/default/history/{func_id}/{history_id}')
        response = api.get(f'http://localhost:5000/api/analysis/default/history/{func_id}/{history_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/analysis/default/multi/<int:func_id>', methods=['PUT', 'GET'])
    def analysis_default_multi(func_id):
        print(f'[{request.method}]/api/analysis/default/multi/{func_id}')
        if request.method == 'PUT':
            response = api.put(f'http://localhost:5000/api/analysis/default/multi/{func_id}')
        else:
            response = api.get(f'http://localhost:5000/api/analysis/default/multi/{func_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/analysis/<int:func_id>/<string:rid>', methods=['GET'])
    def analysis(func_id, rid):
        print(f'[{request.method}]/api/analysis/{func_id}/{rid}')
        # response = api.get(f'http://localhost:5000/api/analysis/{func_id}/{rid}', query_string=request.form)
        response = api.get(f'http://localhost:5000/api/analysis/{func_id}/{rid}', query_string=request.args)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/analysis/multi/<int:func_id>', methods=['GET'])
    def analysis_multi(func_id):
        print(f'[{request.method}]/api/analysis/multi/{func_id}')
        # response = api.get(f'http://localhost:5000/api/analysis/multi/{func_id}', query_string=request.form)
        response = api.get(f'http://localhost:5000/api/analysis/multi/{func_id}', query_string=request.args)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/analysis/data/<int:func_id>/<string:rid>', methods=['GET'])
    def analysis_data(func_id, rid):
        print(f'[{request.method}]/api/analysis/data/{func_id}/{rid}')
        # response = api.get(f'http://localhost:5000/api/analysis/data/{func_id}/{rid}', query_string=request.form)
        response = api.get(f'http://localhost:5000/api/analysis/data/{func_id}/{rid}', query_string=request.args)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/analysis/data/multi/<int:func_id>', methods=['GET'])
    def analysis_data_multi(func_id):
        print(f'[{request.method}]/api/analysis/data/multi/{func_id}')
        # response = api.get(f'http://localhost:5000/api/analysis/data/multi/{func_id}', query_string=request.form)
        response = api.get(f'http://localhost:5000/api/analysis/data/multi/{func_id}', query_string=request.args)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/analysis/remote/<int:func_id>', methods=['POST'])
    def analysis_remote(func_id):
        print(f'[{request.method}]/api/analysis/remote/{func_id}')
        data = request.json
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = api.post(f'http://localhost:5000/api/analysis/remote/{func_id}', data=json.dumps(data), headers=headers)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/analysis/sql/<int:func_id>', methods=['POST'])
    def analysis_sql(func_id):
        print(f'[{request.method}]/api/analysis/sql/{func_id}')
        data = request.json
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = api.post(f'http://localhost:5000/api/analysis/sql/{func_id}', data=json.dumps(data), headers=headers)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/analysis/history/<int:func_id>/<int:history_id>', methods=['GET'])
    def analysis_history(func_id, history_id):
        print(f'[{request.method}]/api/analysis/history/{func_id}/{history_id}')
        response = api.get(f'http://localhost:5000/api/analysis/history/{func_id}/{history_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/analysis/history/new', methods=['POST'])
    def analysis_history_new():
        print(f'[{request.method}]/api/analysis/history/new')
        data = request.json
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = api.post('http://localhost:5000/api/analysis/history/new', data=json.dumps(data), headers=headers)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/analysis/history/<int:history_id>', methods=['DELETE'])
    def analysis_historyid(history_id):
        print(f'[{request.method}]/api/analysis/history/{history_id}')
        print(type(history_id))
        response = api.delete(f'http://localhost:5000/api/analysis/history/{history_id}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    #converter
    @app.route('/api/converter/job', methods=['POST'])
    def converter_job():
        print(f'[{request.method}]/api/converter/job')
        data = request.json
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = api.post('http://localhost:5000/api/converter/job', data=json.dumps(data), headers=headers)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/converter/job/<string:rid>', methods=['GET', 'DELETE'])
    def converter_job_rid_get(rid):
        print(f'[{request.method}]/api/converter/job/{rid}')
        if request.method == 'GET':
            response = api.get(f'http://localhost:5000/api/converter/job/{rid}')
        else:
            response = api.delete(f'http://localhost:5000/api/converter/job/{rid}')
        response = make_response(response.data, 200)
        response.headers['Content-type'] = 'application/json; charset=utf-8'
        return response

    @app.route('/api/converter/file', methods=['POST'])
    def converter_file():
        print(f'[{request.method}]/api/converter/file')
        response = api.post('http://localhost:5000/api/converter/file', query_string=request.form, data=request.files)
        tmp_str = response.data.decode('ascii')
        response = make_response(jsonify(eval(tmp_str)), 200)
        return response

    # dbimport
    @app.route('/api/import/rules', methods=['POST'])
    def import_rules():
        print(f'[{request.method}]/api/import/rules')
        response = api.post('http://localhost:5000/api/import/rules')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/import/function', methods=['POST'])
    def import_function():
        print(f'[{request.method}]/api/import/function')
        response = api.post('http://localhost:5000/api/import/function')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    #export
    @app.route('/api/export/rules', methods=['GET'])
    def export_rules():
        print(f'[{request.method}]/api/export/rules')
        response = api.get('http://localhost:5000/api/export/rules')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/export', methods=['POST'])
    def export():
        print(f'[{request.method}]/api/export')
        response = api.post('http://localhost:5000/api/export')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/export/function', methods=['GET'])
    def export_function():
        print(f'[{request.method}]/api/export/rules')
        response = api.get('http://localhost:5000/api/export/rules')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    # overlay
    @app.route('/api/overlay/convert', methods=['POST'])
    def overlay_convert():
        print(f'[{request.method}]/api/overlay/convert')
        response = api.post('http://localhost:5000/api/overlay/convert', query_string=request.form, data=request.files)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/overlay/info/<string:category>/<string:rid>', methods=['GET'])
    def overlay_info(category, rid):
        print(f'[{request.method}]/api/overlay/info/{category}/{rid}')
        response = api.get(f'http://localhost:5000/api/overlay/info/{category}/{rid}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/overlay/status/<string:category>/<string:rid>', methods=['GET'])
    def overlay_status_category_rid(category, rid):
        print(f'[{request.method}]/api/overlay/status/{category}/{rid}')
        response = api.get(f'http://localhost:5000/api/overlay/status/{category}/{rid}')
        response = make_response(response.data, 200)
        response.headers['Content-type'] = 'application/json; charset=utf-8'
        return response

    @app.route('/api/overlay/analysis', methods=['POST'])
    def overlay_analysis():
        print(f'[{request.method}]/api/overlay/analysis')
        data = request.json
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = api.post('http://localhost:5000/api/overlay/analysis', query_string=request.form, data=json.dumps(data), headers=headers)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/overlay/setting/<string:fab_nm>', methods=['GET'])
    def overlay_status_fab(fab_nm):
        print(f'[{request.method}]/api/overlay/setting/{fab_nm}')
        response = api.get(f'http://localhost:5000/api/overlay/setting/{fab_nm}')
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/overlay/cpvs/load', methods=['POST'])
    def overlay_cpvs_load():
        print(f'[{request.method}]/api/overlay/cpvs/load')
        response = api.post('http://localhost:5000/api/overlay/cpvs/load', data=request.files)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/overlay/<string:category>/cpvs/preset', methods=['POST'])
    def overlay_cpvs_preset(category):
        print(f'[{request.method}]/api/overlay/cpvs/preset')
        data = request.json
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = api.post(f'http://localhost:5000/api/overlay/{category}/cpvs/preset', data=json.dumps(data), headers=headers)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/overlay/<string:category>/cpvs/preset/<int:preset_id>', methods=['GET', 'PUT', 'DELETE'])
    def overlay_cpvs_presetid(category, preset_id):
        print(f'[{request.method}]/api/overlay/{category}/cpvs/preset/{preset_id}')
        data = request.json
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        if request.method == 'GET':
            response = api.get(f'http://localhost:5000/api/overlay/{category}/cpvs/preset/{preset_id}', data=json.dumps(data), headers=headers)
        elif request.method == 'PUT':
            response = api.put(f'http://localhost:5000/api/overlay/{category}/cpvs/preset/{preset_id}', data=json.dumps(data), headers=headers)
        else:
            response = api.delete(f'http://localhost:5000/api/overlay/{category}/cpvs/preset/{preset_id}', data=json.dumps(data), headers=headers)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/overlay/etc/<string:fab_nm>', methods=['PUT'])
    def overlay_etc(fab_nm):
        print(f'[{request.method}]/api/overlay/etc/{fab_nm}')
        data = request.json
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = api.put(f'http://localhost:5000/api/overlay/etc/{fab_nm}', data=json.dumps(data), headers=headers)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/overlay/remote/equipments', methods=['GET'])
    def overlay_remote_equipments():
        print(f'[{request.method}]/api/overlay/remote/equipments')
        response = api.get(f'http://localhost:5000/api/overlay/remote/equipments', query_string=request.form)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    @app.route('/api/overlay/remote/info', methods=['GET'])
    def overlay_remote_info():
        print(f'[{request.method}]/api/overlay/remote/info')
        response = api.get(f'http://localhost:5000/api/overlay/remote/info', query_string=request.form)
        resp_body = json.loads(response.data)
        return make_json_response(**resp_body)

    app.config['DEBUG'] = False
    app.run(threaded=True, host='0.0.0.0')


# @pytest.fixture
# def api():
#     app = create_app('../config.py')
#     app.config['TESTING'] = True
#     api = app.test_client()
#
#     return api

# def test_sample():
#     # GET /
#     # HTTP Status Code : 200
#     time.sleep(1)
#     response = requests.get('http://localhost:5000/main')
#     assert response.status_code == 200
