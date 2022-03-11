import logging
import os
from flask import request, Response, json, make_response, jsonify
from flask_restx import Resource, Namespace, fields
import requests
from werkzeug.datastructures import FileStorage
import traceback

from config import app_config
from common.utils.response import make_json_response, ResponseForm
from dao.dao_management_setting import DAOMGMTSetting
from dao.dao_base import DAOBaseClass
from dao.dao_function import DAOFunction
from dao.dao_graph import DAOGraph
from dao.dao_history import DAOHistory
from service.resources.service_resources import ResourcesService

logger = logging.getLogger(app_config.LOG)

RESOURCES = Namespace(name='RESOURCES', description='Management Setting変更をためのAPI。')

date_response_model = RESOURCES.model('date_response_model', {
    'start': fields.String(description='Logの開始時間', example='2021-01-01'),
    'end': fields.String(description='Logの終了時間', example='2021-03-03'),
})


@RESOURCES.route('/<string:page>')
@RESOURCES.param('page', 'ページ名')
class PAGEResources(Resource):
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self, page):
        """
        ページ毎の構成情報を提供。
        """
        logger.info(str(request))

        try:
            resp_form = self.get_page_resource(page)

            if resp_form.res:
                return make_json_response(**resp_form.data)
            else:
                logger.debug(f'get page resource failed : {resp_form.msg}')
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def get_page_resource(self, page):
        if page == 'main':
            return self.get_main_resource()
        elif page == 'about':
            return self.get_about_resource()
        else:
            return ResponseForm(res=False, msg='Not Found')

    def get_main_resource(self):
        try:
            with open(os.path.join(app_config.RESOURCE_PATH, app_config.RSC_JSON_MAIN), 'r') as f:
                json_data = json.load(f)

            dao_category = DAOBaseClass(table_name='analysis.category')
            dao_function = DAOFunction()
            category_df = dao_category.fetch_all()
            function_df = dao_function.fetch_all()

            if 'title' in json_data:
                json_data['title'] = app_config.APP_NAME

            if 'navibar' in json_data:
                for i in range(len(category_df)):
                    obj = dict()
                    obj['category_id'] = category_df['id'].values[i]
                    obj['title'] = category_df['title'].values[i]
                    obj['func'] = []

                    functions = function_df[function_df['category_id'] == obj['category_id']].reset_index(drop=True)
                    functions.sort_values(by='id', inplace=True)
                    for j in range(len(functions)):
                        sub_func = dict()
                        sub_func['title'] = functions['title'].values[j]
                        sub_func['func_id'] = functions['id'].values[j]
                        obj['func'].append(sub_func)

                    json_data['navibar'].append(obj)

            if 'body' in json_data:
                for i in range(len(category_df)):
                    obj = dict()
                    obj['category_id'] = category_df['id'].values[i]
                    obj['title'] = category_df['title'].values[i]
                    obj['func'] = []

                    functions = function_df[function_df['category_id'] == obj['category_id']].reset_index(drop=True)
                    functions.sort_values(by='id', inplace=True)
                    for j in range(len(functions)):
                        sub_func = dict()
                        sub_func['title'] = functions['title'].values[j]
                        sub_func['func_id'] = functions['id'].values[j]
                        info = dict()
                        source_type = functions['source_type'].values[j]
                        info['Source'] = source_type

                        resp_form = dao_function.get_source_info(sub_func['func_id'])
                        if resp_form.res:
                            source_info = resp_form.data
                            if source_type == 'local':
                                info['Log Name'] = source_info['log_name']
                            elif source_type == 'remote':
                                info['Table'] = source_info['table_name']
                            elif source_type == 'multi':
                                info['subfunc'] = source_info['sub_func_id'].tolist()

                        sub_func['info'] = info
                        obj['func'].append(sub_func)

                    json_data['body'].append(obj)

            if 'footer' in json_data:
                if 'copyright' in json_data['footer']:
                    json_data['footer']['copyright'] = app_config.APP_COPYRIGHT

                if 'version' in json_data['footer']:
                    json_data['footer']['version'] = f'Ver. {app_config.APP_VERSION}'

            return ResponseForm(res=True, data=json_data)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_about_resource(self):
        try:
            with open(os.path.join(app_config.RESOURCE_PATH, app_config.RSC_JSON_ABOUT), 'r') as f:
                json_data = json.load(f)

            if 'version' in json_data:
                json_data['version'] = app_config.APP_VERSION

            if 'app_mode' in json_data:
                json_data['app_mode'] = app_config.APP_MODE

            if 'copyright' in json_data:
                json_data['copyright'] = app_config.APP_COPYRIGHT

            if 'licenses' in json_data:
                with open('LICENSE.md', 'r', encoding='utf-8') as f:
                    md = f.read()
                json_data['licenses'] = md

            return ResponseForm(res=True, data=json_data)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))


@RESOURCES.route('/settings/<int:func_id>')
@RESOURCES.param('func_id', 'Function ID')
class SETTINGSResource(Resource):
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self, func_id):
        """
        機能毎の設定画面構成情報を提供。
        """
        logger.info(str(request))

        try:
            resp_form = self.get_settings_resource(func_id)

            if resp_form.res:
                return make_json_response(**resp_form.data)
            else:
                logger.debug(f'get settings resource failed : {resp_form.msg}')
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def get_settings_resource(self, func_id):
        dao_func = DAOFunction()
        resp_form = dao_func.get_function_info(func_id)
        if not resp_form.res:
            return ResponseForm(res=False, msg='get function info fail.')

        title = resp_form.data['title']
        source_type = resp_form.data['source_type']

        resource_service = ResourcesService()
        base_form = resource_service.get_base_form()
        base_form['title'] = title

        if source_type == 'multi':
            resp_form = resource_service.get_setting_multi_form(func_id)
            if not resp_form.res:
                return resp_form
            base_form = resp_form.data
        else:
            if source_type == 'local':
                resp_form = resource_service.get_setting_local_form(func_id)
            elif source_type == 'remote':
                resp_form = resource_service.get_setting_remote_form(func_id)
            elif source_type == 'sql':
                resp_form = resource_service.get_setting_sql_form(func_id)
            else:
                return ResponseForm(res=False, msg=' Unknown Source type.')

            if resp_form.res:
                base_form['form'][source_type] = resp_form.data
                base_form['formList'].append({'key': source_type, 'type': source_type})

        history_df = dao_func.fetch_all(table='history.history', args={'where': f"func_id='{func_id}'"})
        for i in range(len(history_df)):
            key = history_df['title'].values[i]
            history_id = history_df['id'].values[i]

            if source_type == 'local':
                resp_form = resource_service.get_setting_local_his_form(func_id, history_id)
            elif source_type == 'remote':
                resp_form = resource_service.get_setting_remote_his_form(func_id, history_id)
            elif source_type == 'sql':
                resp_form = resource_service.get_setting_sql_his_form(func_id, history_id)
            elif source_type == 'multi':
                base_form['formList'].append({'title': key, 'type': 'history', 'history_id': history_id})
                continue
            else:
                return ResponseForm(res=False, msg=' Unknown Source type.')

            if resp_form.res:
                base_form['form'][key] = resp_form.data
                base_form['formList'].append({'key': key, 'type': 'history', 'history_id': history_id})

        source_list = [key for key in base_form['form'].keys()]

        for source in source_list:
            for setting in base_form['form'][source]:
                for item in setting['items']:
                    if item['target'] == 'source':
                        item['options'] = source_list

        return ResponseForm(res=True, data=base_form)


@RESOURCES.route('/settings/history/<int:history_id>')
@RESOURCES.param('history_id', 'History ID')
class SETTINGSHistoryResource(Resource):
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self, history_id):
        """
        Get setting info for multifunction's history.
        """
        logger.info(str(request))

        try:
            resp_form = self.get_settings_history_resource(history_id)

            if resp_form.res:
                return make_json_response(**resp_form.data)
            else:
                logger.debug(f'get settings resource failed : {resp_form.msg}')
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def get_settings_history_resource(self, history_id):
        dao_history = DAOHistory()
        dao_func = DAOFunction()
        row = dao_history.fetch_one(args={'where': f"id={history_id}"})
        if row is None:
            return ResponseForm(res=False, msg='get history info fail.')

        title = row['title']

        resource_service = ResourcesService()
        base_form = resource_service.get_base_form()
        base_form['title'] = title

        resp_form = dao_history.get_multi_info(history_id)
        if not resp_form.res:
            return resp_form

        multi_info_df = resp_form.data
        for i in range(len(multi_info_df)):
            sub_source_type = multi_info_df['source_type'].values[i]
            sub_func_id = multi_info_df['sub_func_id'].values[i]
            if sub_source_type == 'local':
                resp_form = resource_service.get_setting_multi_local_his_form(multi_info_df.iloc[i].to_dict())
            elif sub_source_type == 'remote':
                resp_form = resource_service.get_setting_multi_remote_his_form(multi_info_df.iloc[i].to_dict())
            elif sub_source_type == 'sql':
                resp_form = resource_service.get_setting_multi_sql_his_form(multi_info_df.iloc[i].to_dict())
            else:
                return ResponseForm(res=False, msg=' Unknown Source type.')

            if not resp_form.res:
                return resp_form

            form = resp_form.data

            resp_form = dao_func.get_category_info(sub_func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='get category info fail.')

            category = resp_form.data['title']

            resp_form = dao_func.get_function_info(sub_func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='get function info fail.')

            func_info = resp_form.data

            key = None
            for setting in form:
                for item in setting['items']:
                    if item['target'] == 'func_name':
                        key = item['content'] = f"{category}/{func_info['title']}/Tab Name: {multi_info_df['tab_name'].values[i]}"

            if key is None:
                return ResponseForm(res=False, msg='Form Key go wrong.')

            base_form['form'][key] = form

            list_item = {
                'key': key,
                'source_type': sub_source_type,
                'tab_name': multi_info_df['tab_name'].values[i],
                'rid': multi_info_df['rid'].values[i],
                'sub_func_id': sub_func_id
            }

            if sub_source_type == 'local':
                list_item['fid'] = multi_info_df['fid'].values[i]
            elif sub_source_type == 'remote':
                list_item['db_id'] = multi_info_df['db_id'].values[i]
                list_item['table_name'] = multi_info_df['table_name'].values[i]
                list_item['equipment_name'] = multi_info_df['equipment_name'].values[i]
                list_item['period_start'] = multi_info_df['period_start'].values[i]
                list_item['period_end'] = multi_info_df['period_end'].values[i]
            elif sub_source_type == 'sql':
                list_item['db_id'] = multi_info_df['db_id'].values[i]
                list_item['sql'] = multi_info_df['sql'].values[i]

            base_form['formList'].append(list_item)

        source_list = [key for key in base_form['form'].keys()]

        for source in source_list:
            for setting in base_form['form'][source]:
                for item in setting['items']:
                    if item['target'] == 'source':
                        item['options'] = source_list

        return ResponseForm(res=True, data=base_form)


@RESOURCES.route('/settings/date/<string:log_name>/<string:equipment>')
@RESOURCES.param('log_name', 'LOG名')
@RESOURCES.param('equipment', '装置名')
class DateResource(Resource):
    @RESOURCES.doc(model=date_response_model)
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self, log_name, equipment):
        """
        該当装置のLogの開始・終了区間情報を提供。
        """
        logger.info(str(request))

        try:
            resp_form = self.get_start_end_date(log_name, equipment)

            if resp_form.res:
                return make_json_response(**resp_form.data)
            else:
                logger.debug(f'get start end date failed : {resp_form.msg}')
                return make_json_response(status=resp_form.status, msg=resp_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=resp_form.status, msg=str(e))

    def get_start_end_date(self, log_name, equipment):
        try:
            dao_mgmt = DAOMGMTSetting()
            mgmt_df = dao_mgmt.fetch_all()
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e), status=400)

        db_remote_df = mgmt_df[mgmt_df['target'] == 'remote'].reset_index()
        isnull = db_remote_df['host'].isnull().values.any()
        if not isnull:
            host = db_remote_df['host'][0]
            while host[-1] == '/':
                host = host[:-1]

            url = host + app_config.API_GET_DATE + f'/{log_name}/{equipment}'
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    return ResponseForm(res=True, data=response.json())
                else:
                    return ResponseForm(res=False, msg=response.text, status=response.status_code)

            except Exception as e:
                logger.error(str(e))
                logger.error(traceback.format_exc())
                return ResponseForm(res=False, msg=str(e), status=400)

        else:
            return ResponseForm(res=False, msg='Set remote server info first.', status=400)


@RESOURCES.route('/main/category')
class MainCategory(Resource):
    parser = RESOURCES.parser()
    parser.add_argument('category', type=list, location='json', required=True, help='新規Categoryリスト')

    @RESOURCES.expect(parser)
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def post(self):
        """
        新規カテゴリー追加要請API。
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()

            logger.debug(f'args : {args}')

            dao_category = DAOBaseClass(table_name='analysis.category')

            id_list = []
            for item in args['category']:
                if item['category_id'] is not None:
                    id_list.append(item['category_id'])
                    resp_form = dao_category.update(set={'title': item['title']}, where={'id': item['category_id']})
                    if not resp_form.res:
                        return make_json_response(status=400, msg=resp_form.msg)

            category_df = dao_category.fetch_all()
            not_included_df = category_df[~category_df['id'].isin(id_list)]
            exist_system_func = False
            for i in range(len(not_included_df)):
                category_id = not_included_df['id'].values[i]
                func_df = dao_category.fetch_all(table='analysis.function', args={'where': f"category_id={category_id}"})
                for j in range(len(func_df)):
                    if func_df['system_func'].values[j]:
                        exist_system_func = True

                if exist_system_func is False:
                    dao_category.delete(where_dict={'id': category_id})

            for item in args['category']:
                if item['category_id'] is None:
                    resp_form = dao_category.insert(data={'title': item['title']})
                    if not resp_form.res:
                        return make_json_response(status=400, msg=resp_form.msg)

            resp_form = PAGEResources().get_page_resource('main')

            if resp_form.res:
                return make_json_response(**resp_form.data)
            else:
                logger.debug(f'get page resource failed : {resp_form.msg}')
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@RESOURCES.route('/new/step1')
class NewStep1(Resource):
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self):
        """
        STEP1新規ページリソース要請API。
        """
        logger.info(str(request))

        try:
            dao_category = DAOBaseClass(table_name='analysis.category')
            category_df = dao_category.fetch_all()

            options = []
            for i in range(len(category_df)):
                option = {
                    'category_id': category_df['id'][i],
                    'title': category_df['title'][i]
                }
                options.append(option)

            resp = dict()
            resp['category'] = {'options': options}

            return make_json_response(**resp)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@RESOURCES.route('/new/step2')
class NewStep2(Resource):
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self):
        """
        STEP2新規ページリソース要請API。
        """
        logger.info(str(request))

        try:
            resp_form = self.get_step2_resource()

            if resp_form.res:
                return make_json_response(**resp_form.data)
            else:
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.debug('Exception occurs while get step2 resource.')
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def get_step2_resource(self):
        resource_service = ResourcesService()
        base_form = resource_service.get_base_form()

        resp_form = resource_service.get_step2_local_form()
        if resp_form.res:
            base_form['form']['local'] = resp_form.data
            base_form['formList'].append('local')

        resp_form = resource_service.get_step2_remote_form()
        if resp_form.res:
            base_form['form']['remote'] = resp_form.data
            base_form['formList'].append('remote')

        resp_form = resource_service.get_step2_sql_form()
        if resp_form.res:
            base_form['form']['sql'] = resp_form.data
            base_form['formList'].append('sql')

        source_list = [key for key in base_form['form'].keys()]

        for source in source_list:
            for setting in base_form['form'][source]:
                for item in setting['items']:
                    if item['target'] == 'source':
                        item['options'] = source_list

        return ResponseForm(res=True, data=base_form)


@RESOURCES.route('/new/step2/settings/<int:func_id>')
@RESOURCES.param('func_id', 'Function ID')
class NewStep2Settings(Resource):
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self, func_id):
        """
        Get Setting information for each functions.
        """
        logger.info(str(request))

        try:
            resp_form = self.get_multi_settings_resource(func_id)

            if resp_form.res:
                return make_json_response(**resp_form.data)
            else:
                logger.debug(f'get settings resource failed : {resp_form.msg}')
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def get_multi_settings_resource(self, func_id):
        dao_func = DAOFunction()
        resp_form = dao_func.get_function_info(func_id)
        if not resp_form.res:
            return ResponseForm(res=False, msg='get function info fail.')

        title = resp_form.data['title']
        source_type = resp_form.data['source_type']

        resource_service = ResourcesService()

        base_form = dict()

        if source_type == 'local':
            resp_form = resource_service.get_step2_multi_local_form(func_id)
        elif source_type == 'remote':
            resp_form = resource_service.get_step2_multi_remote_form(func_id)
        elif source_type == 'sql':
            resp_form = resource_service.get_step2_multi_sql_form(func_id)
        else:
            return ResponseForm(res=False, msg=' Unknown Source type.')

        if resp_form.res:
            base_form['source_type'] = source_type
            base_form['form'] = resp_form.data

        return ResponseForm(res=True, data=base_form)


@RESOURCES.route('/remote/tables/<int:db_id>')
@RESOURCES.param('db_id', 'Database ID')
class STEP2Tables(Resource):
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self, db_id):
        """
        Get Log Convert Table List from Database

        :return: Table List.
        """
        logger.info(str(request))

        try:
            dao_mgmt = DAOMGMTSetting()
            df = dao_mgmt.fetch_all(args={'where': f"target = 'remote' and id = {db_id}"})

            if len(df) == 0:
                return make_json_response(status=400, msg='Cannot find any matching db id')

            # connection check
            conf = df.iloc[0].to_dict()
            conf['user'] = conf.pop('username')

            dao_remote = DAOBaseClass(**conf)
            resp_form = dao_remote.connection_check()
            if resp_form.res:
                resp_form = dao_remote.get_table_list_from_schema([app_config.SCHEMA_PUBLIC])
                if resp_form.res:
                    table_list = [table.split(sep='.')[1] for table in resp_form.data]
                    response = make_response(jsonify(table_list), 200)
                    return response
                else:
                    return ResponseForm(res=False, msg=resp_form.msg)

            else:
                logger.debug(f'connection check failed : {resp_form.msg}')
                return make_json_response(status=resp_form.status, msg=resp_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@RESOURCES.route('/remote/equipments/<int:db_id>/<string:table_name>')
@RESOURCES.param('db_id', 'Database ID')
@RESOURCES.param('table_name', 'Convert Table Name')
class STEP2Tables(Resource):
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self, db_id, table_name):
        """
        Get Equipments Information from Convert Table
        """
        logger.info(str(request))

        try:
            dao_mgmt = DAOMGMTSetting()
            df = dao_mgmt.fetch_all(args={'where': f"target = 'remote' and id = {db_id}"})

            if len(df) == 0:
                return make_json_response(status=400, msg='Cannot find any matching db id')

            # connection check
            conf = df.iloc[0].to_dict()
            conf['user'] = conf.pop('username')

            item = dict()
            item['user_fab'] = list()
            item['equipment_name'] = dict()

            dao_remote = DAOBaseClass(**conf)
            resp_form = dao_remote.connection_check()
            if resp_form.res:
                df = dao_remote.fetch_all(table=table_name, args={'select': 'equipment_name'})
                if len(df):
                    df['user_fab'] = df['equipment_name'].apply(
                        lambda x: x.split(sep='_')[0] + '/' + x.split(sep='_')[1])
                    user_fab_list = df['user_fab'].unique().tolist()

                    item['user_fab'] = user_fab_list
                    equipment = dict()
                    for user_fab in user_fab_list:
                        equipment[user_fab] = df[df['user_fab'] == user_fab]['equipment_name'].unique().tolist()

                    item['equipment_name'] = equipment

                return make_json_response(**item)
            else:
                logger.debug(f'connection check failed : {resp_form.msg}')
                return make_json_response(status=400, msg=resp_form.msg, **item)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@RESOURCES.route('/remote/date/<int:db_id>/<string:table_name>/<string:equipment_name>')
@RESOURCES.param('db_id', 'Database ID')
@RESOURCES.param('table_name', 'Convert Table Name')
@RESOURCES.param('equipment_name', 'Equipment Name')
class STEP2Tables(Resource):
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self, db_id, table_name, equipment_name):
        """
        Get Log Period
        """
        logger.info(str(request))

        try:
            dao_local = DAOMGMTSetting()
            # Get Database Info
            row = dao_local.fetch_one(args={'where': f"target = 'remote' and id = {db_id}"})
            if row is None:
                return make_json_response(status=400, msg='Cannot find any matching db id')

            db_conf = dict(row)
            db_conf['user'] = db_conf.pop('username')
            dao_remote = DAOMGMTSetting(**db_conf)
            resp_form = dao_remote.connection_check()
            if resp_form.res:
                # Get total log period.
                resp_form = dao_remote.get_log_period(table=table_name,
                                                      where={'equipment_name': equipment_name})
                if resp_form.res:
                    return make_json_response(**resp_form.data)
                else:
                    return make_json_response(status=400, msg=resp_form.msg)
            else:
                logger.debug(f'connection check failed : {resp_form.msg}')
                return make_json_response(status=400, msg=resp_form.msg)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@RESOURCES.route('/new/step3')
class NewStep3(Resource):
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self):
        """
        STEP3新規ページリソース要請API。
        """
        logger.info(str(request))

        try:
            resp_form = self.get_step3_resource()

            if resp_form.res:
                return make_json_response(**resp_form.data)
            else:
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.debug('Exception occurs while get step3 resource.')
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def get_step3_resource(self):
        resource_service = ResourcesService()

        data = dict()

        # Get Convert Infomation
        resp_form = resource_service.get_convert_info()
        if not resp_form.res:
            return resp_form

        data['convert'] = resp_form.data

        # Get Filter Infomation
        resp_form = resource_service.get_filter_info()
        if not resp_form.res:
            return resp_form

        data['filter'] = resp_form.data

        # Get Analysis Infomation
        resp_form = resource_service.get_analysis_info()
        if not resp_form.res:
            return resp_form

        data['analysis'] = resp_form.data

        # Get Visualization Infomation
        resp_form = resource_service.get_visualization_info()
        if not resp_form.res:
            return resp_form

        data['visualization'] = resp_form.data

        return ResponseForm(res=True, data=data)


@RESOURCES.route('/new/step3/<string:log_name>')
@RESOURCES.param('log_name', 'LOG名')
class NewRuleStep3(Resource):
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self, log_name):
        """
        STEP3新規Rule追加ページリソース要請API。
        """
        logger.info(str(request))

        try:
            resp_form = self.get_step3_add_rule(log_name)

            if resp_form.res:
                return make_json_response(**resp_form.data)
            else:
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.debug('Exception occurs while get step3 resource.')
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def get_step3_add_rule(self, log_name):
        resource_service = ResourcesService()

        data = dict()

        # Get Convert Infomation
        resp_form = resource_service.get_convert_info(log_name=log_name)
        if not resp_form.res:
            return resp_form

        data['convert'] = resp_form.data

        # Get Filter Infomation
        resp_form = resource_service.get_filter_info(log_name=log_name)
        if not resp_form.res:
            return resp_form

        data['filter'] = resp_form.data

        # Get Analysis Infomation
        resp_form = resource_service.get_analysis_info()
        if not resp_form.res:
            return resp_form

        data['analysis'] = resp_form.data

        # Get Visualization Infomation
        resp_form = resource_service.get_visualization_info()
        if not resp_form.res:
            return resp_form

        data['visualization'] = resp_form.data

        return ResponseForm(res=True, data=data)


@RESOURCES.route('/<string:log_name>/<int:rule_id>')
@RESOURCES.param('log_name', 'Log Name')
@RESOURCES.param('rule_id', 'Rule ID')
class GetRuleItem(Resource):
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self, log_name, rule_id):
        """
        Get rule items by rule id.
        """
        logger.info(str(request))

        try:
            resp_form = self.get_rule_items(log_name, rule_id)
            if resp_form.res:
                return make_json_response(**resp_form.data)
            else:
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.debug('Exception occurs while get rule items.')
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def get_rule_items(self, log_name, rule_id):
        resource_service = ResourcesService()

        data = dict()

        # Get Convert rule Information
        resp_form = resource_service.get_convert_rule_info(log_name=log_name, rule_id=rule_id)
        if not resp_form.res:
            return resp_form

        data['convert'] = resp_form.data

        return ResponseForm(res=True, data=data)


@RESOURCES.route('/new')
class NewFunction(Resource):
    parser = RESOURCES.parser()
    parser.add_argument('func', type=dict, location='json', required=True, help='Function Information')
    parser.add_argument('convert', type=dict, location='json', required=True, help='Convert Rule Information')
    parser.add_argument('filter', type=dict, location='json', required=True, help='Convert Filter Information')
    parser.add_argument('analysis', type=dict, location='json', required=True, help='Analysis Settings')
    parser.add_argument('visualization', type=dict, location='json', required=True, help='Visualization Settings')

    @RESOURCES.expect(parser)
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def post(self):
        logger.info(str(request))

        args = self.parser.parse_args()
        func = args['func']
        convert = args['convert']
        filter = args['filter']
        analysis = args['analysis']
        visualization = args['visualization']

        resources = ResourcesService()

        func_id = None
        log_id = None
        try:
            if func['source_type'] != 'multi':
                resp_form = resources.check_analysis_available(analysis)
                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)

            if func['source_type'] == 'local':
                if convert['mode'] == 'new':
                    resp_form = resources.insert_convert_info(convert, filter, mode=app_config.NEW_LOG)
                    if not resp_form.res:
                        if resp_form.data is not None:
                            return make_json_response(status=400, err=resp_form.data)
                        else:
                            return make_json_response(status=400, msg=resp_form.msg)

                elif convert['mode'] == 'add':
                    resp_form = resources.insert_convert_info(convert, filter, mode=app_config.ADD_RULE)
                    if not resp_form.res:
                        if resp_form.data is not None:
                            return make_json_response(status=400, err=resp_form.data)
                        else:
                            return make_json_response(status=400, msg=resp_form.msg)

                log_id = resp_form.data
                func['info'] = {'log_name': convert['log_define']['log_name']}

            dao_func = DAOFunction()

            if func['source_type'] == 'multi':
                resp_form = dao_func.insert_multi_func_info({**func,
                                                             'analysis_type': analysis['type']})
            else:
                resp_form = dao_func.insert_func_info({**func,
                                                       'analysis_type': analysis['type']})
            if not resp_form.res:
                resources.delete_id(log_id=log_id)
                return make_json_response(status=400, msg=resp_form.msg)

            func_id = resp_form.data

            if func['source_type'] == 'local':
                resp_form = dao_func.insert_convert_script(convert['script'], func_id=func_id)
                if not resp_form.res:
                    resources.delete_id(log_id=log_id, func_id=func_id)
                    return make_json_response(status=400, msg=resp_form.msg)

            resp_form = dao_func.insert_analysis_info(analysis, func_id)
            if not resp_form.res:
                resources.delete_id(log_id=log_id, func_id=func_id)
                return make_json_response(status=400, msg=resp_form.msg)

            resp_form = dao_func.insert_visual_info(visualization, func_id)
            if not resp_form.res:
                resources.delete_id(log_id=log_id, func_id=func_id)
                return make_json_response(status=400, msg=resp_form.msg)

            return make_json_response(**{'result': True, 'func_id': func_id})

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            if func_id is not None:
                resources.delete_id(log_id=log_id, func_id=func_id)

            return make_json_response(status=400, msg=str(e))


@RESOURCES.route('/scripts/<int:func_id>')
@RESOURCES.param('func_id', 'Function ID')
class ScriptsUpload(Resource):
    parser = RESOURCES.parser()
    parser.add_argument('preprocess', type=FileStorage, location='files', help='preprocess script file')
    parser.add_argument('convert', type=FileStorage, location='files', help='convert script file')
    parser.add_argument('analysis', type=FileStorage, location='files', help='analysis script file')

    @RESOURCES.expect(parser)
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def post(self, func_id):
        logger.info(str(request))

        args = self.parser.parse_args()

        try:
            dao_func = DAOFunction()
            script_table = {
                'preprocess': 'analysis.preprocess_script',
                'convert': 'analysis.convert_script',
                'analysis': 'analysis.analysis_script',
            }

            for key, file in args.items():
                if file is not None:
                    resp_form = dao_func.get_script_file_name(table=script_table[key], func_id=func_id)
                    if not resp_form.res:
                        return make_json_response(status=400, msg='Something went wrong. Check Function ID')

                    file_name = resp_form.data
                    if file_name != file.filename:
                        return make_json_response(status=400, msg='Check Script File Name.')

                    resp_form = dao_func.update_script_file(table=script_table[key], func_id=func_id, file=file)
                    if not resp_form.res:
                        return make_json_response(status=400, msg='update script file fail.')

            return Response(status=200)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@RESOURCES.route('/edit/step1/<int:func_id>')
@RESOURCES.param('func_id', 'Function ID')
class EditStep1(Resource):
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self, func_id):
        """
        STEP1編集ページリソース要請API。
        """
        logger.info(str(request))

        try:
            dao_base = DAOBaseClass()
            func = dao_base.fetch_one(table='analysis.function', args={'where': f"id='{func_id}'"})
            category_df = dao_base.fetch_all(table='analysis.category')

            options = []
            for i in range(len(category_df)):
                option = {
                    'category_id': category_df['id'].values[i],
                    'title': category_df['title'].values[i]
                }
                options.append(option)

            if func is not None:
                resp = dict()
                resp['category'] = {'options': options, 'selected': func['category_id']}
                resp['title'] = func['title']

                return make_json_response(**resp)
            else:
                return make_json_response(status=400, msg='There is no matching id.')

        except Exception as e:
            logger.debug('Exception occurs while fetch all.')
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg='Exception occurs while fetch all.')


@RESOURCES.route('/edit/step2/<string:func_id>')
@RESOURCES.param('func_id', 'Function ID')
class EditStep2(Resource):
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self, func_id):
        """
        Get Step2 Information to Edit
        """
        logger.info(str(request))

        try:
            resp_form = self.get_step2_edit_resource(func_id)

            if resp_form.res:
                return make_json_response(data=resp_form.data)
            else:
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.debug('Exception occurs while get step2 edit resource.')
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def get_step2_edit_resource(self, func_id):
        dao_func = DAOFunction()
        resp_form = dao_func.get_source_type(func_id)
        if not resp_form.res:
            return ResponseForm(res=False, msg='get source_type fail.')

        source_type = resp_form.data

        resource_service = ResourcesService()

        if source_type == 'local':
            return resource_service.get_step2_local_edit_form(func_id)
        elif source_type == 'remote':
            return resource_service.get_step2_remote_edit_form(func_id)
        elif source_type == 'sql':
            return resource_service.get_step2_sql_edit_form(func_id)
        elif source_type == 'multi':
            return resource_service.get_setting_multi_form(func_id)

        return ResponseForm(res=False, msg=' Unknown Source type.')


@RESOURCES.route('/rule/<int:rule_id>')
@RESOURCES.param('rule_id', 'Rule ID')
class DeleteRule(Resource):
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def delete(self, rule_id):
        logger.info(str(request))

        try:
            dao_base = DAOBaseClass()
            row = dao_base.fetch_one(table='cnvbase.convert_rule', args={'select': 'log_id', 'where': f"id={rule_id}"})
            if row is None:
                return make_json_response(status=400, msg='No matching rule_id.')

            log_id = row['log_id']

            dao_base.delete(table='cnvbase.convert_rule', where_dict={'id': rule_id})

            dao_convert_rule = DAOBaseClass(table_name='cnvbase.convert_rule')
            df_convert_rule = dao_convert_rule.fetch_all(args={'select': 'id, rule_name',
                                                               'where': f"log_id={log_id} and commit=true"})
            convert_rule_list = []
            for i in range(len(df_convert_rule)):
                item = dict()
                item['id'] = df_convert_rule['id'][i]
                item['rule_name'] = df_convert_rule['rule_name'][i]

                convert_rule_list.append(item)

            convert_rule_list.append({'id': None, 'rule_name': 'Add New..'})
            data = dict()
            data['options'] = convert_rule_list

            return make_json_response(**data)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@RESOURCES.route('/edit/step3/<int:func_id>/<string:log_name>')
@RESOURCES.param('func_id', 'Function ID')
@RESOURCES.param('log_name', 'LOG名')
class EditNewStep3(Resource):

    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self, func_id, log_name):
        """
        STEP3-Rule追加ページリソース要請API。
        """
        logger.info(str(request))

        try:
            resp_form = self.get_step3_add_rule(func_id, log_name)

            if resp_form.res:
                return make_json_response(**resp_form.data)
            else:
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.debug('Exception occurs while get edit step3 add rule resource.')
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def get_step3_add_rule(self, func_id, log_name):
        resource_service = ResourcesService()

        data = dict()

        # Get Convert Infomation
        resp_form = resource_service.get_convert_info(func_id=func_id, log_name=log_name)
        if not resp_form.res:
            return resp_form

        data['convert'] = resp_form.data

        # Get Filter Infomation
        resp_form = resource_service.get_filter_info(log_name=log_name)
        if not resp_form.res:
            return resp_form

        data['filter'] = resp_form.data

        # Get Analysis Infomation
        resp_form = resource_service.get_analysis_info(func_id=func_id)
        if not resp_form.res:
            return resp_form

        data['analysis'] = resp_form.data

        # Get Visualization Infomation
        resp_form = resource_service.get_visualization_info(func_id=func_id)
        if not resp_form.res:
            return resp_form

        data['visualization'] = resp_form.data

        return ResponseForm(res=True, data=data)


@RESOURCES.route('/edit/step3/<int:func_id>/<string:log_name>/<int:rule_id>')
@RESOURCES.param('func_id', 'Function ID')
@RESOURCES.param('log_name', 'LOG名')
@RESOURCES.param('rule_id', 'Rule ID')
class EditStep3(Resource):

    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def get(self, func_id, log_name, rule_id):
        """
        STEP3-Rule編集ページリソース要請API。
        """
        logger.info(str(request))

        try:
            resp_form = self.get_step3_edit_rule(func_id, log_name, rule_id)

            if resp_form.res:
                return make_json_response(**resp_form.data)
            else:
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.debug('Exception occurs while get step3 resource.')
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def get_step3_edit_rule(self, func_id, log_name, rule_id):
        resource_service = ResourcesService()

        data = dict()

        # Get Convert Infomation
        resp_form = resource_service.get_convert_info(func_id=func_id, log_name=log_name, rule_id=rule_id)
        if not resp_form.res:
            return resp_form

        data['convert'] = resp_form.data

        # Get Filter Infomation
        resp_form = resource_service.get_filter_info(log_name=log_name)
        if not resp_form.res:
            return resp_form

        data['filter'] = resp_form.data

        # Get Analysis Infomation
        resp_form = resource_service.get_analysis_info(func_id=func_id)
        if not resp_form.res:
            return resp_form

        data['analysis'] = resp_form.data

        # Get Visualization Infomation
        resp_form = resource_service.get_visualization_info(func_id=func_id)
        if not resp_form.res:
            return resp_form

        data['visualization'] = resp_form.data

        return ResponseForm(res=True, data=data)


@RESOURCES.route('/edit/<int:func_id>')
class EditFunction(Resource):
    parser = RESOURCES.parser()
    parser.add_argument('func', type=dict, location='json', required=True, help='Function Information')
    parser.add_argument('convert', type=dict, location='json', required=True, help='Convert Rule Information')
    parser.add_argument('filter', type=dict, location='json', required=True, help='Convert Filter Information')
    parser.add_argument('analysis', type=dict, location='json', required=True, help='Analysis Settings')
    parser.add_argument('visualization', type=dict, location='json', required=True, help='Visualization Settings')

    @RESOURCES.expect(parser)
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def post(self, func_id):
        logger.info(str(request))

        args = self.parser.parse_args()
        func = args['func']
        convert = args['convert']
        filter = args['filter']
        analysis = args['analysis']
        visualization = args['visualization']

        resources = ResourcesService()

        log_id = None
        try:
            if func['source_type'] != 'multi':
                resp_form = resources.check_analysis_available(analysis)
                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)

            if func['source_type'] == 'local':
                if convert['mode'] == 'add':
                    resp_form = resources.insert_convert_info(convert, filter, mode=app_config.ADD_RULE)
                    if not resp_form.res:
                        if resp_form.data is not None:
                            return make_json_response(status=400, err=resp_form.data)
                        else:
                            return make_json_response(status=400, msg=resp_form.msg)
                else:
                    resp_form = resources.insert_convert_info(convert, filter, mode=app_config.EDIT_RULE)
                    if not resp_form.res:
                        if resp_form.data is not None:
                            return make_json_response(status=400, err=resp_form.data)
                        else:
                            return make_json_response(status=400, msg=resp_form.msg)

                func['info'] = {'log_name': convert['log_define']['log_name']}

            dao_func = DAOFunction()

            if func['source_type'] == 'multi':
                resp_form = dao_func.update_multi_func_info(func={**func, 'analysis_type': analysis['type']},
                                                            func_id=func_id)
            else:
                resp_form = dao_func.update_func_info(func={**func, 'analysis_type': analysis['type']},
                                                      func_id=func_id)

            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)

            if func['source_type'] == 'local':
                resp_form = dao_func.update_convert_script(convert['script'], func_id)
                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)

            resp_form = dao_func.update_analysis_info(analysis, func_id)
            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)

            resp_form = dao_func.update_visual_info(visualization, func_id)
            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)

            return Response(status=200)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@RESOURCES.route('/func/<int:func_id>')
@RESOURCES.param('func_id', 'Function ID')
class DeleteFunction(Resource):
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def delete(self, func_id):
        logger.info(str(request))

        try:
            dao_base = DAOBaseClass()
            row_dict = dao_base.fetch_one(table='analysis.function', args={'where': f"id={func_id}"})
            if row_dict is None:
                return make_json_response(status=400, msg='No function ID.')

            if row_dict['system_func']:
                return make_json_response(status=400, msg='System function cannot be deleted.')

            if row_dict['source_type'] != 'multi':
                df = dao_base.fetch_all(table='analysis.multi_info', args={'where': f"sub_func_id={func_id}"})
                if len(df) > 0:
                    return make_json_response(status=400, msg='This function is being used on multi function.')

            dao_base.delete(table='analysis.function', where_dict={'id': func_id})

            return Response(status=200)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@RESOURCES.route('/graph/<int:func_id>')
@RESOURCES.param('func_id', 'Function ID')
class GraphAdd(Resource):
    parser = RESOURCES.parser()
    parser.add_argument('name', type=str, location='json', required=True, help='Graph Name')
    parser.add_argument('script', type=str, location='json', required=True, help='Java Script Code')

    @RESOURCES.expect(parser)
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def post(self, func_id):
        """
        Add New User Graph Type

        :param func_id: Function ID
        :return: {
                     "id":
                 }
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()

            resp_form = self.add_user_graph(func_id, **args)
            if resp_form.res:
                return make_json_response(**{'id': resp_form.data})
            else:
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def add_user_graph(self, func_id, **kwargs):
        try:
            dao_graph = DAOGraph()
            row = dao_graph.fetch_one(args={'where': f"func_id={func_id} and name='{kwargs['name']}'"})
            if row is not None:
                return ResponseForm(res=False, msg='Same name is already exist.')

            data = dict()
            data['func_id'] = func_id
            data['name'] = kwargs['name']
            data['script'] = kwargs['script']
            data['type'] = 'user'

            return dao_graph.insert(data=data, rtn_id=True)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))


@RESOURCES.route('/graph/<int:func_id>/<int:graph_id>')
@RESOURCES.param('func_id', 'Function ID')
@RESOURCES.param('graph_id', 'Graph ID')
class GraphEditDelete(Resource):
    parser = RESOURCES.parser()
    parser.add_argument('name', type=str, location='json', required=True, help='Graph Name')
    parser.add_argument('script', type=str, location='json', required=True, help='Java Script Code')

    @RESOURCES.expect(parser)
    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def put(self, func_id, graph_id):
        """
        Edit User Graph Type

        :param func_id: Function ID
        :param graph_id: Graph ID
        :return: Success(200)/Bad Request(400)
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()

            resp_form = self.edit_user_graph(func_id, graph_id, **args)
            if resp_form.res:
                return Response(status=200)
            else:
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def edit_user_graph(self, func_id, graph_id, **kwargs):
        try:
            dao_graph = DAOGraph()
            row = dao_graph.fetch_one(args={'where': f"func_id={func_id} and name='{kwargs['name']}'"})
            if row is not None:
                return ResponseForm(res=False, msg='Same name is already exist.')

            return dao_graph.update(set=kwargs, where={'func_id': func_id, 'id': graph_id})

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))


    @RESOURCES.response(200, 'Success')
    @RESOURCES.response(400, 'Bad Request')
    def delete(self, func_id, graph_id):
        """
        Delete User Graph Type

        :param func_id: Function ID
        :param graph_id: Graph ID
        :return: Success(200)/Bad Request(400)
        """
        logger.info(str(request))

        try:
            resp_form = self.delete_user_graph(func_id, graph_id)
            if resp_form.res:
                return Response(status=200)
            else:
                return make_json_response(status=400, msg=resp_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def delete_user_graph(self, func_id, graph_id):
        try:
            dao_graph = DAOGraph()

            return dao_graph.delete(where_dict={'func_id': func_id, 'id': graph_id}, rtn_id=True)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))
