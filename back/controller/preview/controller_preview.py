import logging
import pandas as pd
import numpy as np
from io import StringIO
import datetime
import os
import importlib
import inspect
import traceback

from flask import request, json
from flask_restx import Resource, Namespace
import requests
from werkzeug.datastructures import FileStorage
from config import app_config
from common.utils.response import make_json_response, ResponseForm
from dao import get_dbinfo
from dao.dao_management_setting import DAOMGMTSetting
from dao.dao_base import DAOBaseClass
from dao.dao_function import DAOFunction
import convert as lc
from service.analysis.service_analysis import AnalysisService
from service.resources.service_resources import ResourcesService
from service.script.service_script import ScriptService
from common.utils import preprocessing

logger = logging.getLogger(app_config.LOG)

PREVIEW = Namespace(name='PREVIEW', description='機能追加STEP別画面のPreview機能用API。')


@PREVIEW.route('/samplelog')
class SampleLog(Resource):
    parser = PREVIEW.parser()
    parser.add_argument('files', type=FileStorage, location='files', help='FILE名')
    parser.add_argument('script_file', type=FileStorage, location='files', help='Script File')
    parser.add_argument('source', required=True, type=str, help='local or remote')
    parser.add_argument('equipment_name', type=str, help='Equipment Name')
    parser.add_argument('table_name', type=str, help='Table Name')
    parser.add_argument('start', type=str, help='Get Sample Log from Start')
    parser.add_argument('end', type=str, help='Log Name')
    parser.add_argument('sql', type=str, help='SQL Query')
    parser.add_argument('use_script', type=str, help='use_script on/off')
    parser.add_argument('db_id', type=int, help='Database ID')
    parser.add_argument('func_id', type=int, help='Fucntion ID')

    @PREVIEW.expect(parser)
    @PREVIEW.response(200, 'Success')
    @PREVIEW.response(400, 'Bad Request')
    def post(self):
        """
        機能追加STEP2画面のPreview機能対応。
        """
        logger.info(str(request))

        args = self.parser.parse_args()

        logger.debug(f'args : {args}')

        f = args['files']
        script = args['script_file']
        source = args['source']
        equipment_name = args['equipment_name']
        table_name = args['table_name']
        start = args['start']
        end = args['end']
        sql = args['sql']
        db_id = args['db_id']
        use_script = True if args['use_script'] == 'true' else False
        func_id = args['func_id']

        _number_of_lines = app_config.SAMPLE_LINES

        try:
            if not os.path.exists(app_config.TEMP_PATH):
                os.mkdir(app_config.TEMP_PATH)

            if source == 'local':
                file_path = os.path.join(app_config.TEMP_PATH, f.filename)
                f.save(file_path)

                if use_script:
                    if script is not None:
                        resp_form = ScriptService().preview_preprocess_script(file_path, script)
                    elif func_id is not None:
                        dao_function = DAOFunction()
                        resp_form = dao_function.get_script('analysis.preprocess_script', func_id)
                        if not resp_form.res:
                            return make_json_response(status=400, msg=resp_form.msg)
                        script_data = resp_form.data['script']
                        file_name = resp_form.data['file_name']
                        temp_path = os.path.join(app_config.TEMP_PATH, file_name)
                        with open(temp_path, 'w') as f:
                            f.write(script_data)

                        with open(temp_path, 'rb') as f:
                            script = FileStorage(f, filename=file_name)
                            resp_form = ScriptService().preview_preprocess_script(file_path, script)
                    else:
                        return make_json_response(status=400, msg='Script not exist.')

                    if not resp_form.res:
                        return make_json_response(status=400, msg=resp_form.msg)
                    file_path = resp_form.data

                f = open(file_path, mode='r', encoding='utf-8')

                data = f.readlines()
                col_max = 0
                cnt = 0
                for line in data:
                    # col_num = len(line.decode('utf-8').split(','))
                    col_num = len(line.split(','))
                    if col_max < col_num:
                        col_max = col_num
                    cnt += 1
                    if cnt >= _number_of_lines:
                        break

                f.seek(0)
                df = pd.read_csv(f, header=None, index_col=False, nrows=_number_of_lines,
                                 skipinitialspace=True, names=range(col_max))
                df.columns = df.columns + 1
                df.index = df.index + 1
                df = df.apply(lambda x: x.str.strip() if x.dtypes == object else x)
                data = df.to_dict(orient='index')
                columns = [str(column) for column in df.columns]
                rtn = {'result': True, 'data': {'disp_order': columns, 'row': data}}

                return make_json_response(**rtn)
            elif source == 'remote' or source == 'sql':
                dao_mgmt = DAOMGMTSetting()
                df = dao_mgmt.fetch_all(args={'where': f"target = 'remote' and id = {db_id}"})

                if len(df) == 0:
                    return make_json_response(status=400, msg='Cannot find any matching db id')

                # connection check
                conf = df.iloc[0].to_dict()
                conf['user'] = conf.pop('username')

                dao_remote = DAOBaseClass(**conf)
                resp_form = dao_remote.connection_check()
                if not resp_form.res:
                    logger.debug(f'connection check failed : {resp_form.msg}')
                    return make_json_response(status=400, msg=resp_form.msg)

                if source == 'remote':
                    filter = {'equipment_name': equipment_name, 'log_time': {'start': start, 'end': end}}
                    log_count = dao_remote.load_data(table=table_name, **filter)
                    if not log_count:
                        return make_json_response(status=400, msg='There is no matching log data.')

                    df = dao_remote.get_df()
                    file_path = os.path.join(app_config.TEMP_PATH, 'remote.csv')
                else:
                    df = dao_remote.read_sql(query=sql)
                    if len(df) == 0:
                        return make_json_response(status=400, msg='There is no matching log data.')

                    file_path = os.path.join(app_config.TEMP_PATH, 'sql.csv')

                df.to_csv(file_path, header=True, index=False)

                if use_script:
                    if script is not None:
                        resp_form = ScriptService().preview_preprocess_script(file_path, script)
                    elif func_id is not None:
                        dao_function = DAOFunction()
                        resp_form = dao_function.get_script('analysis.preprocess_script', func_id)
                        if not resp_form.res:
                            return make_json_response(status=400, msg=resp_form.msg)
                        script_data = resp_form.data['script']
                        file_name = resp_form.data['file_name']
                        temp_path = os.path.join(app_config.TEMP_PATH, file_name)
                        with open(temp_path, 'w') as f:
                            f.write(script_data)

                        with open(temp_path, 'rb') as f:
                            script = FileStorage(f, filename=file_name)
                            resp_form = ScriptService().preview_preprocess_script(file_path, script)
                    else:
                        return make_json_response(status=400, msg='Script not exist.')

                    if not resp_form.res:
                        return make_json_response(status=400, msg=resp_form.msg)
                    file_path = resp_form.data

                df = pd.read_csv(file_path, header=0, index_col=False, nrows=_number_of_lines, skipinitialspace=True)

                src_col_list = []
                filter_key_list = []
                for col in df.columns:
                    if df[col].dtypes == object or df[col].dtypes == np.int64:
                        filter_key_list.append(col)
                    if df[col].dtypes == np.int64 or df[col].dtypes == float:
                        src_col_list.append(col)

                df.index = df.index + 1
                columns = [str(column) for column in df.columns]
                if 'log_time' in columns:
                    columns.remove('log_time')
                    columns.insert(0, 'log_time')

                if 'No.' in columns:
                    columns.remove('No.')
                    columns.insert(0, 'No.')

                data = df.to_dict(orient='index')

                options = dict()

                resource_service = ResourcesService()
                resp_form = resource_service.get_analysis_info(func_id=func_id)
                if resp_form.res:
                    options['analysis'] = resp_form.data

                resp_form = resource_service.get_visualization_info(func_id=func_id)
                if resp_form.res:
                    options['visualization'] = resp_form.data

                rtn = {'result': True,
                       'data': {
                           'disp_order': columns,
                           'src_col_list': src_col_list,
                           'filter_key_list': filter_key_list,
                           'row': data
                       },
                       **options
                       }

                return make_json_response(**rtn)
            else:
                return make_json_response(status=400, msg='Wrong source type.')

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@PREVIEW.route('/samplelog/multi')
class SampleLogMulti(Resource):
    parser = PREVIEW.parser()
    parser.add_argument('use_org_analysis', type=bool, location='json', required=True, help='Use Original Analysis info')
    parser.add_argument('func_list', type=list, location='json', required=True, help='Function Info List')
    parser.add_argument('func_id', type=int, location='json', help='Function ID for EDIT Mode.')

    @PREVIEW.expect(parser)
    @PREVIEW.response(200, 'Success')
    @PREVIEW.response(400, 'Bad Request')
    def post(self):
        """
        Multi機能追加STEP2画面のPreview機能対応。
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            logger.debug(f'args : {args}')

            resource_service = ResourcesService()

            use_org_analysis = args['use_org_analysis']
            func_list = args['func_list']

            if not use_org_analysis:
                data = list()
                filter_key_list = list()

                for func in func_list:
                    data_dict = dict()
                    rid = func['rid']
                    tab_name = func['tab_name']

                    convert_df = preprocessing.load_data(rid=rid)
                    if convert_df is not None:
                        convert_df.index = convert_df.index + 1

                        src_col_list = list()
                        for col in convert_df.columns:
                            if convert_df[col].dtypes == object or convert_df[col].dtypes == np.int64:
                                filter_key_list.append(col)
                            if convert_df[col].dtypes == np.int64 or convert_df[col].dtypes == float:
                                src_col_list.append(col)

                        columns = [str(column) for column in convert_df.columns]
                        if 'log_time' in columns:
                            columns.remove('log_time')
                            columns.insert(0, 'log_time')

                        if 'No.' in columns:
                            columns.remove('No.')
                            columns.insert(0, 'No.')


                        result = {'disp_order': columns,
                                  'src_col_list': src_col_list,
                                  'row': convert_df.to_dict(orient='index')}
                        data_dict[tab_name] = result
                        data.append(data_dict)
                    else:
                        data_dict[tab_name] = None
                        data.append(data_dict)

                options = dict()

                resp_form = resource_service.get_analysis_info(func_id=args.func_id)
                if resp_form.res:
                    options['analysis'] = resp_form.data

                resp_form = resource_service.get_visualization_info(func_id=args.func_id)
                if resp_form.res:
                    options['visualization'] = resp_form.data

                options['analysis']['filter_key_list'] = list(set(filter_key_list))

                rtn = {
                    'result': True,
                    'data': data,
                    **options
                }

                return make_json_response(**rtn)
            else:
                analysis = AnalysisService()
                dao_func = DAOFunction()
                data = list()
                common_axis_x = list()

                for func in func_list:
                    data_dict = dict()
                    rid = func['rid']
                    tab_name = func['tab_name']
                    func_id = func['func_id']

                    func_dict = dao_func.fetch_one(args={'select': 'analysis_type', 'where': f'id={func_id}'})
                    if func_dict is None:
                        return make_json_response(status=400, msg='no matching function id.')

                    analysis_type = func_dict['analysis_type']

                    if analysis_type == 'script':
                        # We don't use filter setting on Script Analysis.
                        filter_default = list()
                    else:
                        resp_form = dao_func.get_filter_default_info(func_id)
                        if not resp_form.res:
                            filter_default = []
                        else:
                            filter_default = resp_form.data

                    resp_form = dao_func.get_aggregation_default_info(func_id)
                    if not resp_form.res:
                        aggregation_default = dict()
                    else:
                        aggregation_default = resp_form.data

                    filter_dict = dict()
                    for item in filter_default:
                        filter_dict[item['key']] = item['val']

                    infos = dict()
                    infos['filter'] = filter_dict
                    infos['aggregation'] = aggregation_default

                    res_form = analysis.get_analysis(func_id, rid, **infos)
                    if res_form.res:
                        result = res_form.data.pop('data')
                        disp_order = result['disp_order']
                        if len(common_axis_x) == 0:
                            common_axis_x = disp_order
                        else:
                            common_axis_x = list(set(common_axis_x) & set(disp_order))
                            # common_axis_x = [x for x in common_axis_x if x in disp_order]
                        data_dict[tab_name] = result
                        data.append(data_dict)
                    else:
                        data_dict[tab_name] = None
                        data.append(data_dict)

                options = dict()

                resp_form = resource_service.get_visualization_info(func_id=args.func_id)
                if resp_form.res:
                    options['visualization'] = resp_form.data

                options['visualization']['common_axis_x'] = common_axis_x

                rtn = {
                    'result': True,
                    'data': data,
                    **options
                }
                return make_json_response(**rtn)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@PREVIEW.route('/convert')
class PreviewConvert(Resource):
    parser = PREVIEW.parser()
    parser.add_argument('json_data', type=FileStorage, location='files', required=True, help='Sample Data, Convert Rule Info')
    parser.add_argument('script_file', type=FileStorage, location='files', help='Script File')
    parser.add_argument('use_script', type=str, help='use_script on/off')
    parser.add_argument('func_id', type=int, help='Function ID')
    parser.add_argument('mode', type=str, help='new,add,edit,empty')

    @PREVIEW.expect(parser)
    @PREVIEW.response(200, 'Success')
    @PREVIEW.response(400, 'Bad Request')
    def post(self):
        """
        Get Convert Preview Data
        """
        logger.info(str(request))

        args = self.parser.parse_args()

        try:
            json_data = json.load(args['json_data'])
            script_file = args['script_file']
            use_script = True if args['use_script'] == 'true' else False
            func_id = args['func_id']
            mode = args['mode']

            data = json_data['data']
            convert = json_data['convert']
            log_define = convert.pop('log_define')

            lc_instance = lc.convert.LogConvert()
            config = get_dbinfo()
            lc_instance.set_db_config(**config)
            config['schema'] = 'convert'
            lc_instance.set_convert_db(**config)

            err = dict()
            disp_order = []
            form_list = []
            src_col_list = []
            filter_key_list = []
            err_exist = False
            for key in convert.keys():
                val = convert[key]
                err[key] = []
                for form in val:
                    form['type'] = key
                    form['rule_id'] = 0
                    form['rule_name'] = log_define['rule_name']
                    if 'row_index' in form and form['row_index'] is not None:
                        form['row_index'] = int(form['row_index'])

                    if 'col_index' in form and form['col_index'] is not None:
                        form['col_index'] = int(form['col_index'])

                    disp_order.append(form['output_column'])

                    if form['data_type'] in [lc.const.data_type_int, lc.const.data_type_float]:
                        src_col_list.append(form['output_column'])

                    if form['data_type'] in [lc.const.data_type_text, lc.const.data_type_varchar_10,
                                               lc.const.data_type_varchar_30, lc.const.data_type_varchar_50,
                                               lc.const.data_type_int, lc.const.data_type_float]:
                        filter_key_list.append(form['output_column'])

                    form_list.append(form)

            item_df = pd.DataFrame(form_list)

            if len(item_df):
                # Check header count
                if mode != 'edit':
                    header_cnt = len(item_df[item_df['type'] == lc.const.item_type_header])
                    lc_log_define = lc_instance.connect.get_log_by_name(log_define['log_name'])
                    if lc_log_define is not None:
                        rules = lc_instance.connect.get_rule_list(lc_log_define['id'], df=True)
                        if len(rules):
                            for i in range(len(rules)):
                                rule_items_df = lc_instance.connect.get_rule_items_by_id(rules['id'].values[i], df=True)
                                if len(rule_items_df) == 0:
                                    continue

                                if header_cnt == len(rule_items_df[rule_items_df['type'] == lc.const.item_type_header]):
                                    return make_json_response(status=400,
                                                              msg=f"Rule name '{rules['rule_name'].values[i]}' has the same header count.")

                if 'coef' in item_df.columns:
                    item_df['coef'] = item_df['coef'].replace({'': 0, np.nan: 0})
                    item_df = item_df.astype({'coef': int})
                item_df = item_df.replace({np.nan: None})
                for _, item in item_df.iterrows():
                    report = lc_instance.test_rule_item(item, item_df.drop(_))
                    if len(report) > 0:
                        err[item['type']].append({'index': item['index'], 'msg': report})
                        err_exist = True
            else:
                return make_json_response(status=400, msg='No Rule Item.')

            if err_exist:
                data = dict()
                data['result'] = False
                data['err'] = err
                return make_json_response(**data)

            if data is None or len(data) == 0:
                trans = {
                    lc.const.data_type_int: int,
                    lc.const.data_type_float: float,
                    lc.const.data_type_text: str,
                    lc.const.data_type_varchar_10: str,
                    lc.const.data_type_varchar_30: str,
                    lc.const.data_type_varchar_50: str,
                    lc.const.data_type_timestamp: datetime,
                    lc.const.data_type_time: datetime,
                    lc.const.data_type_bool: bool
                }

                column_type_dict = dict()
                for i in range(len(item_df)):
                    column_type_dict[item_df['output_column'].values[i]] = trans[item_df['data_type'].values[i]]

                df = preprocessing.make_dummy_data(column_type_dict)

                df.index = df.index + 1

                data = dict()
                data['result'] = True
                data['data'] = {'disp_order': disp_order,
                                'src_col_list': src_col_list,
                                'filter_key_list': filter_key_list,
                                'row': df.to_dict(orient='index')}
                return make_json_response(**data)
            else:
                lines = []
                for i in range(1, len(data['row'])+1):
                    for key, val in data['row'][str(i)].items():
                        if val is None:
                            data['row'][str(i)][key] = ''

                for i in range(1, len(data['row']) + 1):
                    # line = ','.join([str(item) for item in data['row'][str(i)].values()])
                    # lines.append(line)
                    lines.append(data['row'][str(i)])

                input_df = pd.DataFrame(lines)

                if use_script:
                    if script_file is not None:
                        resp_form = ScriptService().preview_convert_script(input_df,
                                                                           item_df,
                                                                           script_file,
                                                                           lc_instance,
                                                                           log_define['log_name'])
                    elif func_id is not None:
                        dao_function = DAOFunction()
                        resp_form = dao_function.get_script('analysis.convert_script', func_id)
                        if not resp_form.res:
                            return make_json_response(status=400, msg=resp_form.msg)
                        script_data = resp_form.data['script']
                        file_name = resp_form.data['file_name']
                        temp_path = os.path.join(app_config.TEMP_PATH, file_name)
                        with open(temp_path, 'w') as f:
                            f.write(script_data)

                        with open(temp_path, 'rb') as f:
                            script_file = FileStorage(f, filename=file_name)
                            resp_form = ScriptService().preview_convert_script(input_df, item_df, script_file, lc_instance, log_define['log_name'])
                    else:
                        return make_json_response(status=400, msg='Script not exist.')

                    if not resp_form.res:
                        return make_json_response(status=400, msg=resp_form.msg)
                    df_preview = resp_form.data
                else:
                    df_preview = lc_instance.create_convert_preview_df(input_df, item_df)
                    for i in range(len(item_df)):
                        if item_df['skip'].values[i] is True:
                            col = item_df['output_column'].values[i]
                            if col in df_preview.columns:
                                df_preview.drop(col, axis=1, inplace=True)

                if df_preview is not None:
                    df_preview.index = df_preview.index + 1

                    filter_key_list = list()
                    src_col_list = list()

                    if use_script:
                        for col in df_preview.columns:
                            if df_preview[col].dtypes == object or df_preview[col].dtypes == np.int64:
                                filter_key_list.append(col)
                            if df_preview[col].dtypes == np.int64 or df_preview[col].dtypes == float:
                                src_col_list.append(col)
                    else:
                        data_type_to_dtype = {
                            lc.const.data_type_int: np.int64,
                            lc.const.data_type_float: float,
                            lc.const.data_type_text: str,
                            lc.const.data_type_varchar_10: str,
                            lc.const.data_type_varchar_30: str,
                            lc.const.data_type_varchar_50: str,
                            lc.const.data_type_timestamp: np.datetime64,
                            lc.const.data_type_time: np.datetime64,
                            lc.const.data_type_bool: bool
                        }

                        for col in df_preview.columns:
                            dtype = data_type_to_dtype[item_df[item_df['output_column'] == col]['data_type'].values[0]]
                            if dtype == str or dtype == np.int64:
                                filter_key_list.append(col)
                            if dtype == np.int64 or dtype == float:
                                src_col_list.append(col)

                    result = {'disp_order': df_preview.columns.values.tolist(),
                            'src_col_list': src_col_list,
                            'filter_key_list': filter_key_list,
                            'row': df_preview.to_dict(orient='index')}
                    rtn = {'result': True, 'data': result}
                    return make_json_response(**rtn)
                else:
                    return make_json_response(status=400, msg='Convert Failure.')
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@PREVIEW.route('/converted')
class PreviewConverted(Resource):
    parser = PREVIEW.parser()
    parser.add_argument('json_data', type=FileStorage, location='files', required=True, help='Sample Data, Convert Rule Info')
    parser.add_argument('script_file', type=FileStorage, location='files', help='Script File')
    parser.add_argument('use_script', type=str, required=True, help='use_script on/off')
    parser.add_argument('func_id', type=int, help='Function ID')

    @PREVIEW.expect(parser)
    @PREVIEW.response(200, 'Success')
    @PREVIEW.response(400, 'Bad Request')
    def post(self):
        """
        Get Converted Preview Data when select existed log_name.
        """
        logger.info(str(request))

        args = self.parser.parse_args()

        try:
            json_data = json.load(args['json_data'])
            script_file = args['script_file']
            use_script = True if args['use_script'] == 'true' else False
            func_id = args['func_id']

            data = json_data['data']
            convert = json_data['convert']
            log_define = convert.pop('log_define')

            lc_instance = lc.convert.LogConvert()
            config = get_dbinfo()
            lc_instance.set_db_config(**config)
            config['schema'] = 'convert'
            lc_instance.set_convert_db(**config)
            lc_instance.set_extra_pkey(['request_id'])

            log_name = log_define['log_name']
            table_name = log_define['table_name']

            if data is None or len(data) == 0:
                lc_log_define = lc_instance.connect.get_log_by_name(log_name)
                if lc_log_define is None:
                    return make_json_response(status=400, msg=f"{log_name} doesn't exist.")

                rules = lc_instance.connect.get_rule_list(log_id=lc_log_define['id'])
                if len(rules) == 0:
                    return make_json_response(status=400, msg=f'no rules exist')

                # Check an output table.
                lc_instance.create_convert_result_table(lc_log_define)

                dao_base = DAOBaseClass()

                df_column_info = dao_base.get_column_info(table=f'convert.{table_name}')
                df_column_info = df_column_info[
                    ~(df_column_info['column_name'].isin(app_config.COLUMN_OMIT_LIST))]
                df_column_info.reset_index(inplace=True, drop=True)

                src_col_list = []
                filter_key_list = []

                trans = {
                    lc.const.data_type_int: int,
                    lc.const.data_type_float: float,
                    'double precision': float,
                    lc.const.data_type_text: str,
                    lc.const.data_type_varchar_10: str,
                    lc.const.data_type_varchar_30: str,
                    lc.const.data_type_varchar_50: str,
                    'character varying': str,
                    lc.const.data_type_timestamp: datetime,
                    lc.const.data_type_time: datetime,
                    lc.const.data_type_bool: bool
                }

                column_type_dict = dict()
                for i in range(len(df_column_info)):
                    column_type = df_column_info['data_type'].values[i]
                    column_name = df_column_info['column_name'].values[i]
                    if column_type in [lc.const.data_type_int, lc.const.data_type_float]:
                        src_col_list.append(df_column_info['column_name'].values[i])
                    if column_type in [lc.const.data_type_text, lc.const.data_type_bool, 'character varying', lc.const.data_type_int, lc.const.data_type_float]:
                        filter_key_list.append(df_column_info['column_name'].values[i])

                    if column_type in trans:
                        column_type_dict[column_name] = trans[column_type]
                    elif 'time' in column_type:
                        column_type_dict[column_name] = trans[lc.const.data_type_timestamp]

                df = preprocessing.make_dummy_data(column_type_dict)
                df.index = df.index + 1

                columns = df_column_info['column_name'].tolist()
                if 'log_time' in columns:
                    columns.remove('log_time')
                    columns.insert(0, 'log_time')

                if 'No.' in columns:
                    columns.remove('No.')
                    columns.insert(0, 'No.')

                rtn = {'result': True,
                       'data':
                           {'disp_order': columns,
                            'src_col_list': src_col_list,
                            'filter_key_list': filter_key_list,
                            'row': df.to_dict(orient='index')
                            }
                       }

                return make_json_response(**rtn)
            else:
                for i in range(1, len(data['row']) + 1):
                    for key, val in data['row'][str(i)].items():
                        if val is None:
                            data['row'][str(i)][key] = ''

                lines = []
                for i in range(1, len(data['row']) + 1):
                    # line = ','.join([str(item) for item in data['row'][str(i)].values()])
                    # lines.append(line)
                    lines.append(data['row'][str(i)])

                input_df = pd.DataFrame(lines)

                out_path = os.path.join(app_config.TEMP_PATH, 'temp.csv')
                if not os.path.exists(app_config.TEMP_PATH):
                    os.mkdir(app_config.TEMP_PATH)

                input_df.to_csv(out_path, header=False, index=False)

                if use_script:
                    if script_file is not None:
                        resp_form = ScriptService().run_convert_script(file_path=out_path,
                                                                       log_name=log_name,
                                                                       lc_mod=lc_instance,
                                                                       request_id='',
                                                                       script_file=script_file)
                    elif func_id is not None:
                        dao_function = DAOFunction()
                        resp_form = dao_function.get_script('analysis.convert_script', func_id)
                        if not resp_form.res:
                            return make_json_response(status=400, msg=resp_form.msg)
                        script_data = resp_form.data['script']
                        file_name = resp_form.data['file_name']
                        temp_path = os.path.join(app_config.TEMP_PATH, file_name)
                        with open(temp_path, 'w') as f:
                            f.write(script_data)

                        with open(temp_path, 'rb') as f:
                            script_file = FileStorage(f, filename=file_name)
                            resp_form = ScriptService().run_convert_script(file_path=out_path,
                                                                           log_name=log_name,
                                                                           lc_mod=lc_instance,
                                                                           request_id='',
                                                                           script_file=script_file)
                    else:
                        return make_json_response(status=400, msg='Script not exist.')

                    if not resp_form.res:
                        return make_json_response(status=400, msg=resp_form.msg)
                    df_out = resp_form.data
                else:
                    df_out = lc_instance.convert(log_name=log_name,
                                                 file=out_path,
                                                 request_id='',
                                                 equipment_name='',
                                                 insert_db=False)

                for col in app_config.COLUMN_OMIT_LIST:
                    if col in df_out.columns:
                        df_out.drop(col, axis=1, inplace=True)

                filter_key_list = []
                src_col_list = []
                for col in df_out.columns:
                    if df_out[col].dtypes == object or df_out[col].dtypes == np.int64:
                        filter_key_list.append(col)
                    if df_out[col].dtypes == np.int64 or df_out[col].dtypes == float:
                        src_col_list.append(col)

                df_out.reset_index(drop=True, inplace=True)
                df_out.index = df_out.index + 1
                columns = [str(column) for column in df_out.columns]

                data = df_out.to_dict(orient='index')

                rtn = {'result': True,
                       'data':
                           {'disp_order': columns,
                            'src_col_list': src_col_list,
                            'filter_key_list': filter_key_list,
                            'row': data
                            }
                       }

                return make_json_response(**rtn)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@PREVIEW.route('/filter')
class PreviewFilter(Resource):
    parser = PREVIEW.parser()
    parser.add_argument('data', type=dict, location='json', required=True, help='Sample Converted Data')
    parser.add_argument('filter', type=dict, location='json', required=True, help='filter info')

    @PREVIEW.expect(parser)
    @PREVIEW.response(200, 'Success')
    @PREVIEW.response(400, 'Bad Request')
    def post(self):
        """
        Get Filtered Preview Data
        """
        logger.info(str(request))

        args = self.parser.parse_args()

        try:
            lc_instance = lc.convert.LogConvert()
            config = get_dbinfo()
            lc_instance.set_db_config(**config)
            config['schema'] = 'convert'
            lc_instance.set_convert_db(**config)

            data = args['data']
            filter = args['filter']['items']

            data_df = pd.DataFrame([], columns=data['disp_order'])
            if data['row'] is not None:
                for i in range(1, len(data['row']) + 1):
                    data_df = data_df.append(data['row'][str(i)], ignore_index=True)

            filtered_df = lc_instance.create_filter_preview(data_df, filter)

            filtered_df.reset_index(drop=True, inplace=True)
            filtered_df.index = filtered_df.index + 1

            data = {'disp_order': filtered_df.columns.values.tolist(),
                    'row': filtered_df.to_dict(orient='index')}
            rtn = {'result': True, 'data': data}
            return make_json_response(**rtn)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@PREVIEW.route('/analysis')
class PreviewAnalysis(Resource):
    parser = PREVIEW.parser()
    parser.add_argument('json_data', type=FileStorage, location='files', required=True,
                        help='Sample Data, Convert Rule Info')
    parser.add_argument('script_file', type=FileStorage, location='files', help='Script File')
    parser.add_argument('use_script', type=str, help='use_script on/off')
    parser.add_argument('func_id', type=int, help='Function ID')

    @PREVIEW.expect(parser)
    @PREVIEW.response(200, 'Success')
    @PREVIEW.response(400, 'Bad Request')
    def post(self):
        """
        Get Analysis Result Preview
        """
        logger.info(str(request))

        args = self.parser.parse_args()

        try:
            json_data = json.load(args['json_data'])
            data = json_data['data']
            analysis = json_data['analysis']
            type = analysis['type']

            script_file = args['script_file']
            use_script = True if args['use_script'] == 'true' else False
            func_id = args['func_id']

            data_df = pd.DataFrame([], columns=data['disp_order'])

            if data['row'] is not None:
                for i in range(1, len(data['row']) + 1):
                    data_df = data_df.append(data['row'][str(i)], ignore_index=True)

            analysis_service = AnalysisService()

            if type == 'setting':
                resp_form = analysis_service.get_analysis_by_setting(data_df, **analysis)
                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)
            elif type == 'script':
                analysis = {
                    **analysis,
                    'use_script': use_script
                }

                if script_file is not None:
                    analysis['script_file'] = script_file
                    resp_form = analysis_service.get_analysis_preview_by_script(data_df, **analysis)
                elif func_id is not None:
                    dao_function = DAOFunction()
                    resp_form = dao_function.get_script('analysis.analysis_script', func_id)
                    if not resp_form.res:
                        return make_json_response(status=400, msg=resp_form.msg)
                    script_data = resp_form.data['script']
                    file_name = resp_form.data['file_name']
                    temp_path = os.path.join(app_config.TEMP_PATH, file_name)
                    with open(temp_path, 'w') as f:
                        f.write(script_data)

                    with open(temp_path, 'rb') as f:
                        script_file = FileStorage(f, filename=file_name)
                        analysis['script_file'] = script_file
                        resp_form = analysis_service.get_analysis_preview_by_script(data_df, **analysis)
                else:
                    return make_json_response(status=400, msg='Script not exist.')

                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)
            elif type == 'none':
                resp_form = analysis_service.get_analysis_preview_by_none(data_df, **analysis)
                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)
            else:
                return make_json_response(status=400, msg=f'Wrong analysis type. {type}')

            df = resp_form.data
            disp_order = df.columns.values.tolist()
            if 'log_time' in disp_order:
                disp_order.remove('log_time')
                disp_order.insert(0, 'log_time')

            if 'No.' in disp_order:
                disp_order.remove('No.')
                disp_order.insert(0, 'No.')

            disp_graph = list()
            for col in df.columns:
                try:
                    df[col].astype({col: np.float})
                    disp_graph.append(col)
                except Exception:
                    pass

            data = dict()
            data['data'] = {'disp_order': disp_order, 'disp_graph': disp_graph, 'row': df.to_dict(orient='index')}

            return make_json_response(**data)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@PREVIEW.route('/analysis/multi')
class PreviewAnalysisMulti(Resource):
    parser = PREVIEW.parser()
    parser.add_argument('json_data', type=FileStorage, location='files', required=True,
                        help='Sample Data, Convert Rule Info')
    parser.add_argument('script_file', type=FileStorage, location='files', help='Script File')
    parser.add_argument('use_script', type=str, help='use_script on/off')
    parser.add_argument('func_id', type=int, help='Function ID')

    @PREVIEW.expect(parser)
    @PREVIEW.response(200, 'Success')
    @PREVIEW.response(400, 'Bad Request')
    def post(self):
        """
        Get Multi Analysis Result Preview
        """
        logger.info(str(request))

        args = self.parser.parse_args()

        try:
            json_data = json.load(args['json_data'])
            func_list = json_data['func_list']
            analysis = json_data['analysis']
            type = analysis['type']

            script_file = args['script_file']
            use_script = True if args['use_script'] == 'true' else False
            func_id = args['func_id']

            objects = dict()
            for func in func_list:
                rid = func['rid']
                tab_name = func['tab_name']

                df = preprocessing.load_data(rid=rid)
                objects[tab_name] = df

            analysis_service = AnalysisService()

            if type == 'setting':
                data_df = pd.concat(objects)
                resp_form = analysis_service.get_analysis_by_setting(data_df, **analysis)
                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)
            elif type == 'script':
                analysis = {
                    **analysis,
                    'use_script': use_script
                }
                data_df = pd.concat(objects)
                if script_file is not None:
                    analysis['script_file'] = script_file
                    resp_form = analysis_service.get_analysis_preview_by_script(data_df, **analysis)
                elif func_id is not None:
                    dao_function = DAOFunction()
                    resp_form = dao_function.get_script('analysis.analysis_script', func_id)
                    if not resp_form.res:
                        return make_json_response(status=400, msg=resp_form.msg)

                    script_data = resp_form.data['script']
                    file_name = resp_form.data['file_name']
                    temp_path = os.path.join(app_config.TEMP_PATH, file_name)
                    with open(temp_path, 'w') as f:
                        f.write(script_data)

                    with open(temp_path, 'rb') as f:
                        script_file = FileStorage(f, filename=file_name)
                        analysis['script_file'] = script_file
                        resp_form = analysis_service.get_analysis_preview_by_script(data_df, **analysis)
                else:
                    return make_json_response(status=400, msg='Script not exist.')

                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)
            elif type == 'none':
                resp_form = analysis_service.get_multi_analysis_by_none(objects, **analysis)
                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)

                df_dict = resp_form.data
                data = list()
                common_axis_x = list()
                for tab_name, df in df_dict.items():
                    table = dict()
                    disp_order = df.columns.values.tolist()
                    if 'log_time' in disp_order:
                        disp_order.remove('log_time')
                        disp_order.insert(0, 'log_time')

                    if 'No.' in disp_order:
                        disp_order.remove('No.')
                        disp_order.insert(0, 'No.')

                    disp_graph = list()
                    for col in df.columns:
                        try:
                            df[col].astype({col: np.float})
                            disp_graph.append(col)
                        except Exception:
                            pass

                    table[tab_name] = {'disp_order': disp_order, 'disp_graph': disp_graph, 'row': df.to_dict(orient='index')}
                    data.append(table)

                    if len(common_axis_x) == 0:
                        common_axis_x = disp_order
                    else:
                        common_axis_x = list(set(common_axis_x) & set(disp_order))

                res = dict()
                res['data'] = data
                res['visualization'] = {'common_axis_x': common_axis_x}
                return make_json_response(**res)
            else:
                return make_json_response(status=400, msg=f'Wrong analysis type. {type}')

            df = resp_form.data
            disp_order = df.columns.values.tolist()
            if 'log_time' in disp_order:
                disp_order.remove('log_time')
                disp_order.insert(0, 'log_time')

            if 'No.' in disp_order:
                disp_order.remove('No.')
                disp_order.insert(0, 'No.')

            disp_graph = list()
            for col in df.columns:
                try:
                    df[col].astype({col: np.float})
                    disp_graph.append(col)
                except Exception:
                    pass

            data = dict()
            data['data'] = {'disp_order': disp_order, 'disp_graph': disp_graph, 'row': df.to_dict(orient='index')}

            return make_json_response(**data)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@PREVIEW.route('/sql')
class PreviewAnalysis(Resource):
    parser = PREVIEW.parser()
    parser.add_argument('db_id', type=int, location='json', required=True, help='Database ID')
    parser.add_argument('sql', type=str, location='json', required=True, help='SQL Query')

    @PREVIEW.expect(parser)
    @PREVIEW.response(200, 'Success')
    @PREVIEW.response(400, 'Bad Request')
    def post(self):
        """
        Get SQL Query Result
        """
        logger.info(str(request))

        args = self.parser.parse_args()

        try:
            db_id = args['db_id']
            sql = args['sql']

            dao_mgmt = DAOMGMTSetting()
            mgmt_df = dao_mgmt.fetch_all(args={'where': f"target = 'remote' and id = {db_id}"})

            if len(mgmt_df) == 0:
                return ResponseForm(res=False, msg='Cannot find any matching db id')

            conf = mgmt_df.iloc[0].to_dict()
            conf['user'] = conf.pop('username')

            dao_remote = DAOBaseClass(**conf)
            resp_form = dao_remote.connection_check()
            if not resp_form.res:
                logger.debug(f'connection check failed : {resp_form.msg}')
                return make_json_response(status=400, msg=resp_form.msg)

            df = dao_remote.read_sql(query=sql)
            if len(df) == 0:
                return make_json_response(status=400, msg='There is no matching log data.')

            disp_order = df.columns.values.tolist()
            if 'log_time' in disp_order:
                disp_order.remove('log_time')
                disp_order.insert(0, 'log_time')

            if 'No.' in disp_order:
                disp_order.remove('No.')
                disp_order.insert(0, 'No.')

            data = dict()
            data['data'] = {'disp_order': disp_order, 'row': df.to_dict(orient='index')}
            return make_json_response(**data)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))
