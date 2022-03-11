import os
import logging
from flask import request, Response, json
from flask_restx import Resource, Namespace, fields
import pandas as pd
import numpy as np
from copy import deepcopy
import datetime
import traceback

from config import app_config
from service.analysis.service_analysis import AnalysisService
from service.script.service_script import ScriptService
from dao.dao_function import DAOFunction
from common.utils.response import make_json_response, ResponseForm
from common.utils import preprocessing
from controller.converter.converter import create_request_id
from dao.dao_history import DAOHistory
from dao.dao_job import DAOJob
from dao.dao_analysis_items import DAOAnalysisItems

logger = logging.getLogger(app_config.LOG)

ANALYSIS = Namespace(name='ANALYSIS', description='ログ分析用API。')

analysis_body = ANALYSIS.model('analysis_body', {
    'log_name': fields.String(description='ログ名', example='PLATEAUTOFOCUSCOMPENSATION'),
    'source': fields.String(description='[local, DB]', example='local'),
    'target_path': fields.String(description='フォルダ経路',
                                 example='P:/log_sample/server_log_path/BSOT/s2/SBPCN480/PLATEAUTOFOCUSCOMPENSATION'),
    'model': fields.String(description='ログフォーマット区分のためのモデル名', example='E813'),
    'one_period': fields.String(description='指定時間を1個のperiodで区分 [12, 24]', example='24'),
    'adjust_period': fields.String(description='periodを区分するための基準時間', example='0'),
    'first_half_year': fields.String(description='ログにyear情報がない場合、1～6月のデータのyear設定', example='2021'),
    'second_half_year': fields.String(description='ログにyear情報がない場合、7～12月のデータのyear設定. [Same Year, Last Year]',
                                      example='Same Year'),
})

analysis_list_response = ANALYSIS.model('analysis_list_response', {
    'items': fields.List(fields.Raw(example={'target': 'one_period',
                                             'title': 'One Period(hour)',
                                             'type': 'select',
                                             'mode': 'singular',
                                             'options': ['12h', '24h'],
                                             'selected': '24h'}, description='target:파라미터명, title:타이틀, '
                                                                              'type:옵션 아이템타입, mode:옵션 아이템 모드, '
                                                                              'options:선택옵션, selected:선택된 옵션'),
                         description='설정 가능한 아이템 리스트'),
    'data': fields.List(fields.Raw(description='start:시작날짜, end:종료날짜, job_list:장치리스트',
                                   example={'start': '2017-05-11 00:00:00',
                                            'end': '2017-05-11 23:59:59',
                                            'job_list': ['SCAN3X2/SCANDBG']}),
                        description='기간별 데이터를 리스트로 반환'),
})

analysis_summary_response = ANALYSIS.model('analysis_summary_response', {
    'items': fields.List(fields.Raw(example={'target': 'valid_interval_minutes',
                                             'title': 'Valid Interval(Min)',
                                             'type': 'select',
                                             'mode': 'singular',
                                             'options': ['1', '2'],
                                             'selected': None}, description='target:파라미터명, title:타이틀, '
                                                                              'type:옵션 아이템타입, mode:옵션 아이템 모드, '
                                                                              'options:선택옵션, selected:선택된 옵션'),
                        description='설정 가능한 아이템 리스트'),
    'data': fields.Raw(example={'disp_order': [], 'summary': {'index 0~ALL': {'column名': '値'}}},
                       description='disp_order:컬럼표시순서, summary:표시 데이터'),
})

analysis_detail_response = ANALYSIS.model('analysis_detail_response', {
    'data': fields.Raw(example={'disp_order': [], 'detail': {'index 0~': {'column名': '値'}}},
                       description='disp_order:컬럼표시순서, detail:표시 데이터'),
})

analysis_remote_response = ANALYSIS.model('analysis_remote_response', {
    'rid': fields.String(description='Request ID', example='request_YYYYMMDD_hhmmssssssss')
})


@ANALYSIS.route('/default/local/<int:func_id>/<string:rid>')
@ANALYSIS.route('/default/remote/<int:func_id>/<string:rid>')
@ANALYSIS.route('/default/sql/<int:func_id>/<string:rid>')
@ANALYSIS.param('func_id', 'Function ID')
@ANALYSIS.param('rid', 'Request ID')
class GetAnalyisDefault(Resource):
    @ANALYSIS.response(200, 'Success')
    @ANALYSIS.response(400, 'Bad Request')
    def get(self, func_id, rid):
        """
        Get Log Period(Start, End) and Filter Setting Information
        """
        logger.info(str(request))

        try:
            analysis = AnalysisService()
            resp_form = analysis.get_analysis_type(func_id)
            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)

            analysis_type = resp_form.data

            resp_form = analysis.get_options(func_id, rid)
            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)

            period_filter = resp_form.data

            aggregation = dict()
            if analysis_type['analysis_type'] == "setting":
                resp_form = analysis.get_aggregation_default(key_id=func_id, rid=rid)
                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)

                aggregation = resp_form.data
            elif analysis_type['analysis_type'] == "script":
                # We don't use filter setting on Script Analysis.
                period_filter['filter'] = list()

            resp_form = analysis.get_visualization_default(func_id)
            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)

            visualization = resp_form.data

            options = {**analysis_type, **period_filter, **aggregation, **visualization}

            return make_json_response(**options)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@ANALYSIS.route('/default/history/<int:func_id>/<int:history_id>')
@ANALYSIS.param('func_id', 'Function ID')
@ANALYSIS.param('history_id', 'History ID')
class GetHistoryDefault(Resource):
    @ANALYSIS.response(200, 'Success')
    @ANALYSIS.response(400, 'Bad Request')
    def get(self, func_id, history_id):
        """
        Get Log Period(Start, End) and Filter Setting Information
        """
        logger.info(str(request))

        try:
            dao_history = DAOHistory()
            ret_dict = dao_history.fetch_one(args={'select': 'source', 'where': f"id='{history_id}'"})
            if ret_dict is None:
                return make_json_response(status=400, msg='No matching history.')

            log_from = ret_dict['source']

            if log_from == 'multi':
                resp_form = self.get_multi_history(func_id, history_id)
                if resp_form.res:
                    return make_json_response(**resp_form.data)
                else:
                    return make_json_response(res=False, msg=resp_form.msg)
            else:
                resp_form = dao_history.get_rid(history_id)
                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)

                rid = resp_form.data

                analysis = AnalysisService()

                resp_form = analysis.get_analysis_type(func_id)
                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)

                analysis_type = resp_form.data

                resp_form = dao_history.get_period(history_id)
                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)

                period_selected = resp_form.data

                resp_form = dao_history.get_filter_info(history_id)
                if not resp_form.res:
                    filter_selected = None
                else:
                    filter_selected = resp_form.data

                resp_form = dao_history.get_aggregation_info(history_id)
                if not resp_form.res:
                    aggregation = dict()
                else:
                    aggregation = resp_form.data

                resp_form = dao_history.get_visualization_info(func_id, history_id)
                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)

                visualization = resp_form.data

                infos = dict()
                filter_info = dict()
                filter_info['log_time'] = period_selected
                if filter_selected is not None:
                    filter_info = {**filter_info, **filter_selected}

                infos['filter'] = filter_info

                infos['aggregation'] = aggregation

                resp_form = analysis.get_analysis(func_id, rid, **infos)
                if not resp_form.res:
                    return make_json_response(status=400, msg=resp_form.msg)

                options = {**analysis_type,
                           **resp_form.data['option'],
                           'visualization': visualization,
                           'data': resp_form.data['data'],
                           'rid': rid}

                return make_json_response(**options)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def get_multi_history(self, func_id, history_id):
        analysis_service = AnalysisService()
        resp_form = analysis_service.get_analysis_type(func_id)
        if not resp_form.res:
            return make_json_response(status=400, msg=resp_form.msg)

        analysis_type = resp_form.data['analysis_type']

        if analysis_type == 'org':
            resp_form = self.get_multi_org_his_analysis(func_id, history_id)
        elif analysis_type == 'setting':
            resp_form = self.get_multi_setting_his_analysis(func_id, history_id)
        elif analysis_type == 'script':
            resp_form = self.get_multi_script_his_analysis(func_id, history_id)
        elif analysis_type == 'none':
            resp_form = self.get_multi_none_his_analysis(func_id, history_id)
        else:
            return make_json_response(status=400, msg='Undefined analysis type')

        if resp_form.res:
            result = resp_form.data
            result['analysis_type'] = 'multi/' + analysis_type
            return ResponseForm(res=True, data=result)
        else:
            return resp_form


    def get_multi_org_his_analysis(self, func_id, history_id):
        dao_history = DAOHistory()
        dao_func = DAOFunction()
        analysis_service = AnalysisService()
        resp_form = dao_history.get_multi_info(history_id)
        if not resp_form.res:
            return resp_form

        df_info = resp_form.data

        objects = dict()
        for i in range(len(df_info)):
            rid = df_info['rid'].values[i]
            tab_name = df_info['tab_name'].values[i]

            df = preprocessing.load_data(rid=rid)
            objects[tab_name] = df

        common_axis_x = list()
        dict_result = dict()

        resp_form = dao_history.get_period(history_id)
        if not resp_form.res:
            return resp_form

        selected_period = resp_form.data

        for i in range(len(df_info)):
            rid = df_info['rid'].values[i]
            tab_name = df_info['tab_name'].values[i]
            sub_func_id = df_info['sub_func_id'].values[i]

            func_dict = dao_func.fetch_one(args={'select': 'analysis_type', 'where': f'id={sub_func_id}'})
            if func_dict is None:
                return ResponseForm(res=False, msg="Cannot find sub function's analysis type.")

            sub_analysis_type = func_dict['analysis_type']

            if sub_analysis_type == 'script':
                # We don't use filter setting on Script Analysis.
                filter_default = list()
            else:
                resp_form = dao_func.get_filter_default_info(sub_func_id)
                if not resp_form.res:
                    filter_default = []
                else:
                    filter_default = resp_form.data

            resp_form = dao_func.get_aggregation_default_info(sub_func_id)
            if not resp_form.res:
                aggregation_default = dict()
            else:
                aggregation_default = resp_form.data

            filter_dict = dict()
            for item in filter_default:
                filter_dict[item['key']] = item['val']

            filter_dict['log_time'] = selected_period

            infos = dict()
            infos['filter'] = filter_dict
            infos['aggregation'] = aggregation_default

            res_form = analysis_service.get_analysis(sub_func_id, rid, **infos)
            if res_form.res:
                result = res_form.data.pop('data')
                disp_order = result['disp_order']
                if len(common_axis_x) == 0:
                    common_axis_x = disp_order
                else:
                    common_axis_x = list(set(common_axis_x) & set(disp_order))
                    # common_axis_x = [x for x in common_axis_x if x in disp_order]
                dict_result[tab_name] = result
            else:
                dict_result[tab_name] = None

        data_df = pd.concat(objects)
        period = preprocessing.get_data_period(data_df)
        if period is None:
            return ResponseForm(res=False, msg='No "log_time" column.')

        resp_form = dao_history.get_visualization_info(func_id, history_id)
        if not resp_form.res:
            return resp_form

        visualization = resp_form.data
        visualization['common_axis_x'] = common_axis_x

        result = dict()
        result['period'] = {**period, 'selected': [selected_period['start'], selected_period['end']]}
        result['filter'] = list()
        result['aggregation'] = dict()
        result['visualization'] = visualization
        result['data'] = dict_result

        return ResponseForm(res=True, data=result)

    def get_multi_setting_his_analysis(self, func_id, history_id):
        dao_history = DAOHistory()
        resp_form = dao_history.get_multi_info(history_id)
        if not resp_form.res:
            return resp_form

        df_info = resp_form.data

        objects = dict()
        for i in range(len(df_info)):
            rid = df_info['rid'].values[i]
            tab_name = df_info['tab_name'].values[i]

            df = preprocessing.load_data(rid=rid)
            objects[tab_name] = df

        rid = create_request_id()
        logger.debug(f'create request id : {rid}')

        io = DAOJob.instance()
        form = {
            'id': rid,
            'file': '0',
            'log_name': None,
            'job_type': 'local'
        }
        io.insert_job(**form)

        resp_form = dao_history.get_filter_info(history_id)
        if not resp_form.res:
            filter_default = []
        else:
            filter_info = resp_form.data
            filter_default = list()
            for key, val in filter_info.items():
                filter_default.append({'key': key, 'val': val})

        resp_form = dao_history.get_period(history_id)
        if not resp_form.res:
            return resp_form

        period_selected = resp_form.data
        filter_default.append({'key': 'log_time', 'val': period_selected})

        resp_form = dao_history.get_aggregation_info(history_id)
        if not resp_form.res:
            aggregation_default = dict()
        else:
            aggregation_default = resp_form.data

        data_df = pd.concat(objects)

        dao_analysis_items = DAOAnalysisItems(func_id=func_id)
        analysis_list = dao_analysis_items.get_analysis_list_by_order()

        analysis = {
            'items': analysis_list,
            'filter_default': filter_default,
            'aggregation_default': aggregation_default
        }

        analysis_service = AnalysisService()

        resp_form = analysis_service.get_analysis_by_setting(data_df, rid, **analysis)
        if not resp_form.res:
            return resp_form

        df_result = resp_form.data

        resp_form = analysis_service.get_aggregation_default(key_id=history_id, df=data_df, is_history=True)
        if not resp_form.res:
            return resp_form

        aggregation = resp_form.data['aggregation']

        aggregation_type = aggregation_default['type']
        aggregation_val = aggregation_default['val']

        aggregation['selected'] = aggregation_type
        if aggregation_type in aggregation['subItem']:
            aggregation['subItem'][aggregation_type]['selected'] = aggregation_val

        resp_form = analysis_service.get_options(key_id=history_id, df=data_df, is_history=True)
        if not resp_form.res:
            return resp_form

        option = resp_form.data

        filter_dict = dict()
        for item in filter_default:
            filter_dict[item['key']] = item['val']

        if 'log_time' in filter_dict:
            selected_period = [filter_dict['log_time']['start'], filter_dict['log_time']['end']]
            option['period']['selected'] = selected_period

        for item in option['filter']:
            if item['target'] in filter_dict:
                item['selected'] = filter_dict[item['target']]
            else:
                item['selected'] = list()

        resp_form = dao_history.get_visualization_info(func_id, history_id)
        if not resp_form.res:
            return resp_form

        visualization = resp_form.data

        disp_order = df_result.columns.values.tolist()
        if 'log_time' in disp_order:
            disp_order.remove('log_time')
            disp_order.insert(0, 'log_time')

        if 'No.' in disp_order:
            disp_order.remove('No.')
            disp_order.insert(0, 'No.')

        disp_graph = list()
        for col in df_result.columns:
            try:
                df_result[col].astype({col: np.float})
                disp_graph.append(col)
            except Exception:
                pass

        result = dict()
        result['period'] = option['period']
        result['filter'] = option['filter']
        result['aggregation'] = aggregation
        result['visualization'] = visualization
        result['data'] = {'disp_order': disp_order, 'disp_graph': disp_graph, 'row': df_result.to_dict(orient='index')}

        return ResponseForm(res=True, data=result)

    def get_multi_script_his_analysis(self, func_id, history_id):
        dao_history = DAOHistory()
        dao_func = DAOFunction()
        resp_form = dao_history.get_multi_info(history_id)
        if not resp_form.res:
            return resp_form

        df_info = resp_form.data

        objects = dict()
        for i in range(len(df_info)):
            rid = df_info['rid'].values[i]
            tab_name = df_info['tab_name'].values[i]

            df = preprocessing.load_data(rid=rid)
            objects[tab_name] = df

        rid = create_request_id()
        logger.debug(f'create request id : {rid}')

        io = DAOJob.instance()
        form = {
            'id': rid,
            'file': '0',
            'log_name': None,
            'job_type': 'local'
        }
        io.insert_job(**form)

        resp_form = dao_func.get_script(table='analysis.analysis_script', func_id=func_id)
        if resp_form.res:
            data = resp_form.data
            if data['use_script']:
                script_file_path = self.make_script_folder(log_name='', rid=rid)
                with open(os.path.join(script_file_path, 'analysis.py'), 'w', encoding='shift_jis') as f:
                    f.write(data['script'])

        resp_form = dao_func.get_script(table='analysis.analysis_script', func_id=func_id)
        if not resp_form.res:
            return ResponseForm(res=False, msg='Cannot Find Analysis Script Info')

        info = {
            'db_id': resp_form.data['db_id'],
            'sql': resp_form.data['sql']
        }

        data_df = pd.concat(objects)

        resp_form = dao_history.get_period(history_id)
        if not resp_form.res:
            return resp_form

        selected_period = resp_form.data

        filtered_df = deepcopy(data_df)
        if 'log_time' in filtered_df.columns:
            start = selected_period['start']
            end = selected_period['end']
            try:
                datetime.datetime.strptime(end, '%Y-%m-%d')
                end = end + ' 23:59:59'
            except Exception as e:
                pass
            filtered_df = filtered_df[(start <= filtered_df['log_time']) & (filtered_df['log_time'] <= end)]

        resp_form = ScriptService().run_generic_analysis_script(df=filtered_df, rid=rid, **info)
        if not resp_form.res:
            return resp_form

        df_result = resp_form.data

        period = preprocessing.get_data_period(data_df)
        if period is None:
            return ResponseForm(res=False, msg='No "log_time" column.')

        resp_form = dao_history.get_visualization_info(func_id, history_id)
        if not resp_form.res:
            return resp_form

        visualization = resp_form.data

        disp_order = df_result.columns.values.tolist()
        if 'log_time' in disp_order:
            disp_order.remove('log_time')
            disp_order.insert(0, 'log_time')

        if 'No.' in disp_order:
            disp_order.remove('No.')
            disp_order.insert(0, 'No.')

        disp_graph = list()
        for col in df_result.columns:
            try:
                df_result[col].astype({col: np.float})
                disp_graph.append(col)
            except Exception:
                pass

        result = dict()
        result['period'] = {**period, 'selected': [selected_period['start'], selected_period['end']]}
        result['filter'] = list()
        result['aggregation'] = dict()
        result['visualization'] = visualization
        result['data'] = {'disp_order': disp_order, 'disp_graph': disp_graph, 'row': df_result.to_dict(orient='index')}

        return ResponseForm(res=True, data=result)

    def get_multi_none_his_analysis(self, func_id, history_id):
        dao_history = DAOHistory()
        resp_form = dao_history.get_multi_info(history_id)
        if not resp_form.res:
            return resp_form

        df_info = resp_form.data

        objects = dict()
        for i in range(len(df_info)):
            rid = df_info['rid'].values[i]
            tab_name = df_info['tab_name'].values[i]

            df = preprocessing.load_data(rid=rid)
            objects[tab_name] = df

        resp_form = dao_history.get_filter_info(history_id)
        if not resp_form.res:
            filter_default = []
        else:
            filter_info = resp_form.data
            filter_default = list()
            for key, val in filter_info.items():
                filter_default.append({'key': key, 'val': val})

        resp_form = dao_history.get_period(history_id)
        if not resp_form.res:
            return resp_form

        period_selected = resp_form.data

        filter_default.append({'key': 'log_time', 'val': period_selected})

        analysis = {
            'filter_default': filter_default
        }

        analysis_service = AnalysisService()

        resp_form = analysis_service.get_multi_analysis_by_none(objects, **analysis)
        if not resp_form.res:
            return make_json_response(status=400, msg=resp_form.msg)

        dict_result = resp_form.data

        data = dict()
        common_axis_x = list()
        for tab_name, df in dict_result.items():
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

            data[tab_name] = {'disp_order': disp_order, 'disp_graph': disp_graph,
                               'row': df.to_dict(orient='index')}

            if len(common_axis_x) == 0:
                common_axis_x = disp_order
            else:
                common_axis_x = list(set(common_axis_x) & set(disp_order))

        data_df = pd.concat(objects)
        resp_form = analysis_service.get_options(key_id=history_id, df=data_df, is_history=True)
        if not resp_form.res:
            return resp_form

        option = resp_form.data

        filter_dict = dict()
        for item in filter_default:
            filter_dict[item['key']] = item['val']

        if 'log_time' in filter_dict:
            selected_period = [filter_dict['log_time']['start'], filter_dict['log_time']['end']]
            option['period']['selected'] = selected_period

        for item in option['filter']:
            if item['target'] in filter_dict:
                item['selected'] = filter_dict[item['target']]
            else:
                item['selected'] = list()

        resp_form = dao_history.get_visualization_info(func_id, history_id)
        if not resp_form.res:
            return resp_form

        visualization = resp_form.data
        visualization['common_axis_x'] = common_axis_x

        result = dict()
        result['period'] = option['period']
        result['filter'] = option['filter']
        result['aggregation'] = dict()
        result['visualization'] = visualization
        result['data'] = data

        return ResponseForm(res=True, data=result)


@ANALYSIS.route('/default/multi/<int:func_id>')
@ANALYSIS.param('func_id', 'Function ID')
class MultiDefault(Resource):
    @ANALYSIS.response(200, 'Success')
    @ANALYSIS.response(400, 'Bad Request')
    def put(self, func_id):
        """
        Update analysis.multi_info table.
        """
        logger.info(str(request))

        try:
            param = json.loads(request.get_data())

            dao_func = DAOFunction()
            multi_info_id = param.pop('multi_info_id')
            if 'fid' in param:
                param['fid'] = ','.join([str(_) for _ in param['fid']])
            resp_form = dao_func.update(table='analysis.multi_info',
                                        set=param,
                                        where={'id': multi_info_id,
                                               'func_id': func_id})
            if not resp_form.res:
                return resp_form

            return Response(status=200)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def get(self, func_id):
        """
        Get Analysis Results of Multi-Function
        """
        logger.info(str(request))

        try:
            analysis_service = AnalysisService()
            resp_form = analysis_service.get_analysis_type(func_id)
            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)

            analysis_type = resp_form.data['analysis_type']

            if analysis_type == 'org':
                resp_form = self.get_default_multi_org_analysis(func_id)
            elif analysis_type == 'setting':
                resp_form = self.get_default_multi_setting_analysis(func_id)
            elif analysis_type == 'script':
                resp_form = self.get_default_multi_script_analysis(func_id)
            elif analysis_type == 'none':
                resp_form = self.get_default_multi_none_analysis(func_id)
            else:
                return make_json_response(status=400, msg='Undefined analysis type')

            if resp_form.res:
                result = resp_form.data
                result['analysis_type'] = 'multi/' + analysis_type
                return make_json_response(**result)
            else:
                return make_json_response(status=400, msg=resp_form.msg)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))

    def get_default_multi_org_analysis(self, func_id):
        dao_func = DAOFunction()
        analysis_service = AnalysisService()
        resp_form = dao_func.get_source_info(func_id)
        if not resp_form.res:
            return resp_form

        df_info = resp_form.data

        objects = dict()
        for i in range(len(df_info)):
            rid = df_info['rid'].values[i]
            tab_name = df_info['tab_name'].values[i]

            df = preprocessing.load_data(rid=rid)
            objects[tab_name] = df

        common_axis_x = list()
        dict_result = dict()

        for i in range(len(df_info)):
            rid = df_info['rid'].values[i]
            tab_name = df_info['tab_name'].values[i]
            sub_func_id = df_info['sub_func_id'].values[i]

            func_dict = dao_func.fetch_one(args={'select': 'analysis_type', 'where': f'id={sub_func_id}'})
            if func_dict is None:
                return ResponseForm(res=False, msg="Cannot find sub function's analysis type.")

            sub_analysis_type = func_dict['analysis_type']

            if sub_analysis_type == 'script':
                # We don't use filter setting on Script Analysis.
                filter_default = list()
            else:
                resp_form = dao_func.get_filter_default_info(sub_func_id)
                if not resp_form.res:
                    filter_default = []
                else:
                    filter_default = resp_form.data

            resp_form = dao_func.get_aggregation_default_info(sub_func_id)
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

            res_form = analysis_service.get_analysis(sub_func_id, rid, **infos)
            if res_form.res:
                result = res_form.data.pop('data')
                disp_order = result['disp_order']
                if len(common_axis_x) == 0:
                    common_axis_x = disp_order
                else:
                    common_axis_x = list(set(common_axis_x) & set(disp_order))
                    # common_axis_x = [x for x in common_axis_x if x in disp_order]
                dict_result[tab_name] = result
            else:
                dict_result[tab_name] = None

        data_df = pd.concat(objects)
        period = preprocessing.get_data_period(data_df)
        if period is None:
            return ResponseForm(res=False, msg='No "log_time" column.')

        resp_form = analysis_service.get_visualization_default(func_id)
        if not resp_form.res:
            return resp_form

        visualization = resp_form.data['visualization']
        visualization['common_axis_x'] = common_axis_x

        result = dict()
        result['period'] = {**period, 'selected': [period['start'], period['end']]}
        result['filter'] = list()
        result['aggregation'] = dict()
        result['visualization'] = visualization
        result['data'] = dict_result

        return ResponseForm(res=True, data=result)

    def get_default_multi_setting_analysis(self, func_id):
        dao_func = DAOFunction()
        resp_form = dao_func.get_source_info(func_id)
        if not resp_form.res:
            return resp_form

        df_info = resp_form.data

        objects = dict()
        for i in range(len(df_info)):
            rid = df_info['rid'].values[i]
            tab_name = df_info['tab_name'].values[i]

            df = preprocessing.load_data(rid=rid)
            objects[tab_name] = df

        rid = create_request_id()
        logger.debug(f'create request id : {rid}')

        io = DAOJob.instance()
        form = {
            'id': rid,
            'file': '0',
            'log_name': None,
            'job_type': 'local'
        }
        io.insert_job(**form)

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

        data_df = pd.concat(objects)

        dao_analysis_items = DAOAnalysisItems(func_id=func_id)
        analysis_list = dao_analysis_items.get_analysis_list_by_order()

        analysis = {
            'items': analysis_list,
            'filter_default': filter_default,
            'aggregation_default': aggregation_default
        }

        analysis_service = AnalysisService()

        resp_form = analysis_service.get_analysis_by_setting(data_df, rid, **analysis)
        if not resp_form.res:
            return resp_form

        df_result = resp_form.data

        resp_form = analysis_service.get_aggregation_default(key_id=func_id, df=data_df)
        if not resp_form.res:
            return resp_form

        aggregation = resp_form.data['aggregation']

        resp_form = analysis_service.get_options(key_id=func_id, df=data_df)
        if not resp_form.res:
            return resp_form

        option = resp_form.data

        resp_form = analysis_service.get_visualization_default(func_id)
        if not resp_form.res:
            return resp_form

        visualization = resp_form.data['visualization']

        disp_order = df_result.columns.values.tolist()
        if 'log_time' in disp_order:
            disp_order.remove('log_time')
            disp_order.insert(0, 'log_time')

        if 'No.' in disp_order:
            disp_order.remove('No.')
            disp_order.insert(0, 'No.')

        disp_graph = list()
        for col in df_result.columns:
            try:
                df_result[col].astype({col: np.float})
                disp_graph.append(col)
            except Exception:
                pass

        result = dict()
        result['period'] = option['period']
        result['filter'] = option['filter']
        result['aggregation'] = aggregation
        result['visualization'] = visualization
        result['data'] = {'disp_order': disp_order, 'disp_graph': disp_graph, 'row': df_result.to_dict(orient='index')}

        return ResponseForm(res=True, data=result)

    def get_default_multi_script_analysis(self, func_id):
        dao_func = DAOFunction()
        resp_form = dao_func.get_source_info(func_id)
        if not resp_form.res:
            return resp_form

        df_info = resp_form.data

        objects = dict()
        for i in range(len(df_info)):
            rid = df_info['rid'].values[i]
            tab_name = df_info['tab_name'].values[i]

            df = preprocessing.load_data(rid=rid)
            objects[tab_name] = df

        rid = create_request_id()
        logger.debug(f'create request id : {rid}')

        io = DAOJob.instance()
        form = {
            'id': rid,
            'file': '0',
            'log_name': None,
            'job_type': 'local'
        }
        io.insert_job(**form)

        resp_form = dao_func.get_script(table='analysis.analysis_script', func_id=func_id)
        if resp_form.res:
            data = resp_form.data
            if data['use_script']:
                script_file_path = self.make_script_folder(log_name='', rid=rid)
                with open(os.path.join(script_file_path, 'analysis.py'), 'w', encoding='shift_jis') as f:
                    f.write(data['script'])

        resp_form = dao_func.get_script(table='analysis.analysis_script', func_id=func_id)
        if not resp_form.res:
            return ResponseForm(res=False, msg='Cannot Find Analysis Script Info')

        info = {
            'db_id': resp_form.data['db_id'],
            'sql': resp_form.data['sql']
        }

        data_df = pd.concat(objects)

        resp_form = ScriptService().run_generic_analysis_script(df=data_df, rid=rid, **info)
        if not resp_form.res:
            return resp_form

        df_result = resp_form.data

        period = preprocessing.get_data_period(data_df)
        if period is None:
            return ResponseForm(res=False, msg='No "log_time" column.')

        analysis_service = AnalysisService()

        resp_form = analysis_service.get_visualization_default(func_id)
        if not resp_form.res:
            return resp_form

        visualization = resp_form.data['visualization']

        disp_order = df_result.columns.values.tolist()
        if 'log_time' in disp_order:
            disp_order.remove('log_time')
            disp_order.insert(0, 'log_time')

        if 'No.' in disp_order:
            disp_order.remove('No.')
            disp_order.insert(0, 'No.')

        disp_graph = list()
        for col in df_result.columns:
            try:
                df_result[col].astype({col: np.float})
                disp_graph.append(col)
            except Exception:
                pass

        result = dict()
        result['period'] = {**period, 'selected': [period['start'], period['end']]}
        result['filter'] = list()
        result['aggregation'] = dict()
        result['visualization'] = visualization
        result['data'] = {'disp_order': disp_order, 'disp_graph': disp_graph, 'row': df_result.to_dict(orient='index')}

        return ResponseForm(res=True, data=result)

    def get_default_multi_none_analysis(self, func_id):
        dao_func = DAOFunction()
        resp_form = dao_func.get_source_info(func_id)
        if not resp_form.res:
            return resp_form

        df_info = resp_form.data

        objects = dict()
        for i in range(len(df_info)):
            rid = df_info['rid'].values[i]
            tab_name = df_info['tab_name'].values[i]

            df = preprocessing.load_data(rid=rid)
            objects[tab_name] = df

        resp_form = dao_func.get_filter_default_info(func_id)
        if not resp_form.res:
            filter_default = []
        else:
            filter_default = resp_form.data

        analysis = {
            'filter_default': filter_default
        }

        analysis_service = AnalysisService()

        resp_form = analysis_service.get_multi_analysis_by_none(objects, **analysis)
        if not resp_form.res:
            return resp_form

        dict_result = resp_form.data

        data = dict()
        common_axis_x = list()
        for tab_name, df in dict_result.items():
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

            data[tab_name] = {'disp_order': disp_order, 'disp_graph': disp_graph,
                               'row': df.to_dict(orient='index')}

            if len(common_axis_x) == 0:
                common_axis_x = disp_order
            else:
                common_axis_x = list(set(common_axis_x) & set(disp_order))

        data_df = pd.concat(objects)
        resp_form = analysis_service.get_options(key_id=func_id, df=data_df)
        if not resp_form.res:
            return resp_form

        option = resp_form.data

        resp_form = analysis_service.get_visualization_default(func_id)
        if not resp_form.res:
            return resp_form

        visualization = resp_form.data['visualization']
        visualization['common_axis_x'] = common_axis_x

        result = dict()
        result['period'] = option['period']
        result['filter'] = option['filter']
        result['aggregation'] = dict()
        result['visualization'] = visualization
        result['data'] = data

        return ResponseForm(res=True, data=result)


@ANALYSIS.route('/<int:func_id>/<string:rid>')
@ANALYSIS.param('func_id', 'Fuction ID')
@ANALYSIS.param('rid', 'Request ID')
class GetAnalysis(Resource):
    parser = ANALYSIS.parser()
    parser.add_argument('start', required=True, help='期間の開始時間(YYYY-MM-DD hh:mm:ss)')
    parser.add_argument('end', required=True, help='期間の終了時間(YYYY-MM-DD hh:mm:ss)')

    @ANALYSIS.expect(parser)
    @ANALYSIS.response(200, 'Success')
    @ANALYSIS.response(500, 'Internal Server Error')
    def get(self, func_id, rid):
        """
        期間/グループ別LOGデータの分析結果を返還するAPI。
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            param_dict = request.args.to_dict(flat=False)  # flat: to get list values

            for key in ['start', 'end']:
                if key in param_dict:
                    param_dict.pop(key)

            filter = dict()
            filter['log_time'] = args

            if 'filter_key' in param_dict:
                for key in param_dict['filter_key']:
                    if key in param_dict:
                        param_dict[key] = [val for val in param_dict[key] if val != '' and val != 'null']
                        if len(param_dict[key]) > 0:
                            filter[key] = param_dict[key]

            infos = dict()
            infos['filter'] = filter

            aggregation = dict()
            if 'aggregation_key' in param_dict:
                if 'aggregation_val' in param_dict:
                    aggregation['type'] = param_dict['aggregation_key'][0]
                    aggregation['val'] = param_dict['aggregation_val'][0]
                else:
                    aggregation['type'] = param_dict['aggregation_key'][0]
                    aggregation['val'] = None

            infos['aggregation'] = aggregation

            analysis = AnalysisService()

            res_form = analysis.get_analysis(func_id, rid, **infos)
            if res_form.res:
                return make_json_response(**res_form.data)
            else:
                logger.debug(f'get summary failed : {res_form.msg}')
                return make_json_response(status=500, msg=res_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=500, msg=str(e))


@ANALYSIS.route('/multi/<int:func_id>')
@ANALYSIS.param('func_id', 'Fuction ID')
class GetMultiAnalysis(Resource):
    parser = ANALYSIS.parser()
    parser.add_argument('start', required=True, help='期間の開始時間(YYYY-MM-DD hh:mm:ss)')
    parser.add_argument('end', required=True, help='期間の終了時間(YYYY-MM-DD hh:mm:ss)')

    @ANALYSIS.expect(parser)
    @ANALYSIS.response(200, 'Success')
    @ANALYSIS.response(500, 'Internal Server Error')
    def get(self, func_id):
        """
        Multi log analysis on specific period and options
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            param_dict = request.args.to_dict(flat=False)  # flat: to get list values

            for key in ['start', 'end']:
                if key in param_dict:
                    param_dict.pop(key)

            filter = dict()
            filter['log_time'] = args

            if 'filter_key' in param_dict:
                for key in param_dict['filter_key']:
                    if key in param_dict:
                        param_dict[key] = [val for val in param_dict[key] if val != '' and val != 'null']
                        if len(param_dict[key]) > 0:
                            filter[key] = param_dict[key]

            infos = dict()
            infos['filter'] = filter

            aggregation = dict()
            if 'aggregation_key' in param_dict:
                if 'aggregation_val' in param_dict:
                    aggregation['type'] = param_dict['aggregation_key'][0]
                    aggregation['val'] = param_dict['aggregation_val'][0]
                else:
                    aggregation['type'] = param_dict['aggregation_key'][0]
                    aggregation['val'] = None

            infos['aggregation'] = aggregation

            analysis_service = AnalysisService()
            resp_form = analysis_service.get_analysis_type(func_id)
            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)

            analysis_type = resp_form.data['analysis_type']

            if analysis_type == 'org':
                resp_form = self.get_multi_org_analysis(func_id, **infos)
            elif analysis_type == 'setting':
                resp_form = self.get_multi_setting_analysis(func_id, **infos)
            elif analysis_type == 'script':
                resp_form = self.get_multi_script_analysis(func_id, **infos)
            elif analysis_type == 'none':
                resp_form = self.get_multi_none_analysis(func_id, **infos)
            else:
                return make_json_response(status=400, msg='Undefined analysis type')

            if resp_form.res:
                result = resp_form.data
                result['analysis_type'] = 'multi/' + analysis_type
                return make_json_response(**result)
            else:
                return make_json_response(status=400, msg=resp_form.msg)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=500, msg=str(e))

    def get_multi_org_analysis(self, func_id, **kwargs):
        dao_func = DAOFunction()
        analysis_service = AnalysisService()
        resp_form = dao_func.get_source_info(func_id)
        if not resp_form.res:
            return resp_form

        df_info = resp_form.data

        objects = dict()
        for i in range(len(df_info)):
            rid = df_info['rid'].values[i]
            tab_name = df_info['tab_name'].values[i]

            df = preprocessing.load_data(rid=rid)
            objects[tab_name] = df

        common_axis_x = list()
        dict_result = dict()

        for i in range(len(df_info)):
            rid = df_info['rid'].values[i]
            tab_name = df_info['tab_name'].values[i]
            sub_func_id = df_info['sub_func_id'].values[i]

            func_dict = dao_func.fetch_one(args={'select': 'analysis_type', 'where': f'id={sub_func_id}'})
            if func_dict is None:
                return ResponseForm(res=False, msg="Cannot find sub function's analysis type.")

            sub_analysis_type = func_dict['analysis_type']

            if sub_analysis_type == 'script':
                # We don't use filter setting on Script Analysis.
                filter_default = list()
            else:
                resp_form = dao_func.get_filter_default_info(sub_func_id)
                if not resp_form.res:
                    filter_default = []
                else:
                    filter_default = resp_form.data

            resp_form = dao_func.get_aggregation_default_info(sub_func_id)
            if not resp_form.res:
                aggregation_default = dict()
            else:
                aggregation_default = resp_form.data

            filter_dict = dict()
            for item in filter_default:
                filter_dict[item['key']] = item['val']

            infos = dict()
            if 'filter' in kwargs:
                infos['filter'] = deepcopy(kwargs['filter'])

            for key, val in filter_dict.items():
                infos['filter'][key] = val

            infos['aggregation'] = aggregation_default

            res_form = analysis_service.get_analysis(sub_func_id, rid, **infos)
            if res_form.res:
                result = res_form.data.pop('data')
                disp_order = result['disp_order']
                if len(common_axis_x) == 0:
                    common_axis_x = disp_order
                else:
                    common_axis_x = list(set(common_axis_x) & set(disp_order))
                    # common_axis_x = [x for x in common_axis_x if x in disp_order]
                dict_result[tab_name] = result
            else:
                dict_result[tab_name] = None

        data_df = pd.concat(objects)
        period = preprocessing.get_data_period(data_df)
        if period is None:
            return ResponseForm(res=False, msg='No "log_time" column.')

        option = dict()
        option['period'] = {**period, 'selected': [kwargs['filter']['log_time']['start'], kwargs['filter']['log_time']['end']]}
        option['filter'] = list()
        option['aggregation'] = dict()

        result = dict()
        result['option'] = {**option}
        result['visualization'] = {'common_axis_x': common_axis_x}
        result['data'] = dict_result

        return ResponseForm(res=True, data=result)

    def get_multi_setting_analysis(self, func_id, **kwargs):
        dao_func = DAOFunction()
        resp_form = dao_func.get_source_info(func_id)
        if not resp_form.res:
            return resp_form

        df_info = resp_form.data

        objects = dict()

        for i in range(len(df_info)):
            rid = df_info['rid'].values[i]
            tab_name = df_info['tab_name'].values[i]

            df = preprocessing.load_data(rid=rid)
            objects[tab_name] = df

        rid = create_request_id()
        logger.debug(f'create request id : {rid}')

        io = DAOJob.instance()
        form = {
            'id': rid,
            'file': '0',
            'log_name': None,
            'job_type': 'local'
        }
        io.insert_job(**form)

        data_df = pd.concat(objects)

        dao_analysis_items = DAOAnalysisItems(func_id=func_id)
        analysis_list = dao_analysis_items.get_analysis_list_by_order()

        filter_default = list()
        for key, val in kwargs['filter'].items():
            filter_default.append({'key': key, 'val': val})

        aggregation_default = dict()
        if 'aggregation' in kwargs:
            aggregation_default = kwargs['aggregation']

        analysis = {
            'items': analysis_list,
            'filter_default': filter_default,
            'aggregation_default': aggregation_default
        }

        analysis_service = AnalysisService()

        resp_form = analysis_service.get_analysis_by_setting(data_df, rid, **analysis)
        if not resp_form.res:
            return resp_form

        df_result = resp_form.data

        aggregation_type = kwargs['aggregation']['type']
        aggregation_val = kwargs['aggregation']['val']

        resp_form = analysis_service.get_aggregation_default(key_id=func_id, df=data_df)
        if not resp_form.res:
            return resp_form

        aggregation = resp_form.data['aggregation']

        aggregation['selected'] = aggregation_type
        if aggregation_type in aggregation['subItem']:
            aggregation['subItem'][aggregation_type]['selected'] = aggregation_val

        resp_form = analysis_service.get_options(key_id=func_id, df=data_df)
        if not resp_form.res:
            return resp_form

        option = resp_form.data
        if 'log_time' in kwargs['filter']:
            selected_period = [kwargs['filter']['log_time']['start'], kwargs['filter']['log_time']['end']]
            option['period']['selected'] = selected_period

        for item in option['filter']:
            if item['target'] in kwargs['filter']:
                item['selected'] = kwargs['filter'][item['target']]
            else:
                item['selected'] = list()

        disp_order = df_result.columns.values.tolist()
        if 'log_time' in disp_order:
            disp_order.remove('log_time')
            disp_order.insert(0, 'log_time')

        if 'No.' in disp_order:
            disp_order.remove('No.')
            disp_order.insert(0, 'No.')

        disp_graph = list()
        for col in df_result.columns:
            try:
                df_result[col].astype({col: np.float})
                disp_graph.append(col)
            except Exception:
                pass

        result = dict()
        result['option'] = {**option, 'aggregation': aggregation}
        result['data'] = {'disp_order': disp_order,
                          'disp_graph': disp_graph,
                          'row': dict() if df_result is None else df_result.to_dict(orient='index')}

        return ResponseForm(res=True, data=result)

    def get_multi_script_analysis(self, func_id, **kwargs):
        dao_func = DAOFunction()
        resp_form = dao_func.get_source_info(func_id)
        if not resp_form.res:
            return make_json_response(status=400, msg=resp_form.msg)

        df_info = resp_form.data

        objects = dict()

        for i in range(len(df_info)):
            rid = df_info['rid'].values[i]
            tab_name = df_info['tab_name'].values[i]

            df = preprocessing.load_data(rid=rid)
            objects[tab_name] = df

        rid = create_request_id()
        logger.debug(f'create request id : {rid}')

        io = DAOJob.instance()
        form = {
            'id': rid,
            'file': '0',
            'log_name': None,
            'job_type': 'local'
        }
        io.insert_job(**form)

        resp_form = dao_func.get_script(table='analysis.analysis_script', func_id=func_id)
        if resp_form.res:
            data = resp_form.data
            if data['use_script']:
                script_file_path = self.make_script_folder(log_name='', rid=rid)
                with open(os.path.join(script_file_path, 'analysis.py'), 'w', encoding='shift_jis') as f:
                    f.write(data['script'])

        resp_form = dao_func.get_script(table='analysis.analysis_script', func_id=func_id)
        if not resp_form.res:
            return ResponseForm(res=False, msg='Cannot Find Analysis Script Info')

        info = {
            'db_id': resp_form.data['db_id'],
            'sql': resp_form.data['sql']
        }

        data_df = pd.concat(objects)

        filtered_df = deepcopy(data_df)
        selected_period = None
        if 'log_time' in kwargs['filter']:
            start = kwargs['filter']['log_time']['start']
            end = kwargs['filter']['log_time']['end']
            selected_period = [start, end]
            if 'log_time' in filtered_df.columns:
                try:
                    datetime.datetime.strptime(end, '%Y-%m-%d')
                    end = end + ' 23:59:59'
                except Exception as e:
                    pass
                filtered_df = filtered_df[(start <= filtered_df['log_time']) & (filtered_df['log_time'] <= end)]

        resp_form = ScriptService().run_generic_analysis_script(df=filtered_df, rid=rid, **info)
        if not resp_form.res:
            return resp_form

        df_result = resp_form.data

        period = preprocessing.get_data_period(data_df)
        if period is None:
            return ResponseForm(res=False, msg='No "log_time" column.')

        disp_order = df_result.columns.values.tolist()
        if 'log_time' in disp_order:
            disp_order.remove('log_time')
            disp_order.insert(0, 'log_time')

        if 'No.' in disp_order:
            disp_order.remove('No.')
            disp_order.insert(0, 'No.')

        disp_graph = list()
        for col in df_result.columns:
            try:
                df_result[col].astype({col: np.float})
                disp_graph.append(col)
            except Exception:
                pass

        option = dict()
        option['period'] = {**period, 'selected': selected_period}
        option['filter'] = list()
        option['aggregation'] = dict()

        result = dict()
        result['option'] = {**option}
        result['data'] = {'disp_order': disp_order, 'disp_graph': disp_graph, 'row': df_result.to_dict(orient='index')}

        return ResponseForm(res=True, data=result)

    def get_multi_none_analysis(self, func_id, **kwargs):
        dao_func = DAOFunction()
        resp_form = dao_func.get_source_info(func_id)
        if not resp_form.res:
            return make_json_response(status=400, msg=resp_form.msg)

        df_info = resp_form.data

        objects = dict()
        for i in range(len(df_info)):
            rid = df_info['rid'].values[i]
            tab_name = df_info['tab_name'].values[i]

            df = preprocessing.load_data(rid=rid)
            objects[tab_name] = df

        filter_default = list()
        for key, val in kwargs['filter'].items():
            filter_default.append({'key': key, 'val': val})

        analysis = {
            'filter_default': filter_default
        }

        analysis_service = AnalysisService()

        resp_form = analysis_service.get_multi_analysis_by_none(deepcopy(objects), **analysis)
        if not resp_form.res:
            return make_json_response(status=400, msg=resp_form.msg)

        dict_result = resp_form.data

        data = dict()
        common_axis_x = list()
        for tab_name, df in dict_result.items():
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

            data[tab_name] = {'disp_order': disp_order, 'disp_graph': disp_graph,
                               'row': df.to_dict(orient='index')}

            if len(common_axis_x) == 0:
                common_axis_x = disp_order
            else:
                common_axis_x = list(set(common_axis_x) & set(disp_order))

        data_df = pd.concat(objects)
        resp_form = analysis_service.get_options(key_id=func_id, df=data_df)
        if not resp_form.res:
            return resp_form

        option = resp_form.data

        if 'log_time' in kwargs['filter']:
            selected_period = [kwargs['filter']['log_time']['start'], kwargs['filter']['log_time']['end']]
            option['period']['selected'] = selected_period

        for item in option['filter']:
            if item['target'] in kwargs['filter']:
                item['selected'] = kwargs['filter'][item['target']]
            else:
                item['selected'] = list()

        visualization = dict()
        visualization['common_axis_x'] = common_axis_x

        result = dict()
        result['option'] = {**option, 'aggregation': dict()}
        result['visualization'] = visualization
        result['data'] = data

        return ResponseForm(res=True, data=result)


@ANALYSIS.route('/data/<int:func_id>/<string:rid>')
@ANALYSIS.param('func_id', 'Function ID')
@ANALYSIS.param('rid', 'Request ID')
class AnalysisDetail(Resource):
    parser = ANALYSIS.parser()
    parser.add_argument('start', required=True, help='期間の開始時間(YYYY-MM-DD hh:mm:ss)')
    parser.add_argument('end', required=True, help='期間の終了時間(YYYY-MM-DD hh:mm:ss)')

    @ANALYSIS.expect(parser)
    @ANALYSIS.response(200, 'Success')
    @ANALYSIS.response(500, 'Internal Server Error')
    def get(self, func_id, rid):
        """
        期間/グループ別全体LOGデータを返還するAPI。
        """
        logger.info(str(request))

        try:

            args = self.parser.parse_args()
            param_dict = request.args.to_dict(flat=False)  # flat: to get list values

            for key in ['start', 'end']:
                if key in param_dict:
                    param_dict.pop(key)

            filter = dict()
            filter['log_time'] = {'start': args['start'], 'end': args['end']}

            if 'filter_key' in param_dict:
                for key in param_dict['filter_key']:
                    if key in param_dict:
                        param_dict[key] = [val for val in param_dict[key] if val != '' and val != 'null']
                        if len(param_dict[key]) > 0:
                            filter[key] = param_dict[key]

            infos = dict()
            infos['filter'] = filter

            aggregation = dict()
            if 'aggregation_key' in param_dict and 'aggregation_val' in param_dict and 'selected' in param_dict:
                aggregation['type'] = param_dict['aggregation_key'][0]
                aggregation['val'] = param_dict['aggregation_val'][0]
                aggregation['selected'] = param_dict['selected']

            infos['aggregation'] = aggregation

            analysis = AnalysisService()

            res_form = analysis.get_detail(func_id, rid, **infos)
            if res_form.res:
                return make_json_response(**res_form.data)
            else:
                logger.debug(f'get detail failed : {res_form.msg}')
                return make_json_response(status=500, msg=res_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=500, msg=str(e))


@ANALYSIS.route('/data/multi/<int:func_id>')
@ANALYSIS.param('func_id', 'Function ID')
class AnalysisMultiDetail(Resource):
    parser = ANALYSIS.parser()
    parser.add_argument('start', required=True, help='期間の開始時間(YYYY-MM-DD hh:mm:ss)')
    parser.add_argument('end', required=True, help='期間の終了時間(YYYY-MM-DD hh:mm:ss)')

    @ANALYSIS.expect(parser)
    @ANALYSIS.response(200, 'Success')
    @ANALYSIS.response(500, 'Internal Server Error')
    def get(self, func_id):
        """
        期間/グループ別全体LOGデータを返還するAPI。
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()
            param_dict = request.args.to_dict(flat=False)  # flat: to get list values

            for key in ['start', 'end']:
                if key in param_dict:
                    param_dict.pop(key)

            filter = dict()
            filter['log_time'] = {'start': args['start'], 'end': args['end']}

            if 'filter_key' in param_dict:
                for key in param_dict['filter_key']:
                    if key in param_dict:
                        param_dict[key] = [val for val in param_dict[key] if val != '' and val != 'null']
                        if len(param_dict[key]) > 0:
                            filter[key] = param_dict[key]

            infos = dict()
            infos['filter'] = filter

            aggregation = dict()
            if 'aggregation_key' in param_dict and 'aggregation_val' in param_dict and 'selected' in param_dict:
                aggregation['type'] = param_dict['aggregation_key'][0]
                aggregation['val'] = param_dict['aggregation_val'][0]
                aggregation['selected'] = param_dict['selected']

            infos['aggregation'] = aggregation

            analysis = AnalysisService()

            res_form = analysis.get_multi_detail(func_id, **infos)
            if res_form.res:
                return make_json_response(**res_form.data)
            else:
                logger.debug(f'get detail failed : {res_form.msg}')
                return make_json_response(status=500, msg=res_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=500, msg=str(e))


@ANALYSIS.route('/remote/<int:func_id>')
@ANALYSIS.param('func_id', 'Function ID')
class AnalysisRemote(Resource):
    parser = ANALYSIS.parser()
    parser.add_argument('db_id', required=True, location='json', help='Database ID')
    parser.add_argument('equipment_name', required=True, location='json', help='Equipment Name')
    parser.add_argument('period', required=True, location='json', help='LOG取得期間(YYYY-MM-DD~YYYY-MM-DD)')

    @ANALYSIS.expect(parser)
    @ANALYSIS.response(200, 'Success')
    @ANALYSIS.response(400, 'Bad Request')
    @ANALYSIS.response(500, 'Internal Server Error')
    def post(self, func_id):
        """
        遠隔LOGを取得して内部Fileに格納する。
        """
        logger.info(str(request))
        try:
            args = self.parser.parse_args()

            logger.debug(f'args : {args}')

            res_form = AnalysisService().get_remote_log(func_id, **{**args, 'source': 'remote'})
            if res_form.res:
                df_out = res_form.data

                rid = create_request_id()
                logger.debug(f'create request id : {rid}')

                io = DAOJob.instance()
                form = {
                    'id': rid,
                    'file': '0',
                    'log_name': None,
                    'job_type': 'local'
                }
                io.insert_job(**form)

                folder = os.path.join(os.path.join(app_config.CNV_RESULT_PATH, rid), 'remote')
                if not os.path.exists(folder):
                    os.makedirs(folder)

                path = os.path.join(folder, 'log.csv')
                df_out.to_csv(path, header=True, index=False)

                script_service = ScriptService()
                script_service.make_script_file({'remote': func_id}, rid)

                use_pre_script = script_service.get_use_pre_script(func_id)
                if use_pre_script:
                    resp_form = ScriptService().run_preprocess_script(file_path=path, rid=rid)
                    if not resp_form.res:
                        return make_json_response(status=400, msg=resp_form.msg)

                return make_json_response(rid=rid)
            else:
                logger.debug(f'get remote log failed : {res_form.msg}')
                return make_json_response(status=500, msg=res_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@ANALYSIS.route('/sql/<int:func_id>')
@ANALYSIS.param('func_id', 'Function ID')
class AnalysisRemote(Resource):
    parser = ANALYSIS.parser()
    parser.add_argument('db_id', required=True, location='json', help='Database ID')

    @ANALYSIS.expect(parser)
    @ANALYSIS.response(200, 'Success')
    @ANALYSIS.response(400, 'Bad Request')
    @ANALYSIS.response(500, 'Internal Server Error')
    def post(self, func_id):
        """
        遠隔LOGを取得して内部Fileに格納する。
        """
        logger.info(str(request))

        try:
            args = self.parser.parse_args()

            logger.debug(f'args : {args}')

            res_form = AnalysisService().get_remote_log(func_id, **{**args, 'source': 'sql'})
            if res_form.res:
                df_out = res_form.data

                rid = create_request_id()
                logger.debug(f'create request id : {rid}')

                io = DAOJob.instance()
                form = {
                    'id': rid,
                    'file': '0',
                    'log_name': None,
                    'job_type': 'local'
                }
                io.insert_job(**form)

                folder = os.path.join(os.path.join(app_config.CNV_RESULT_PATH, rid), 'sql')
                if not os.path.exists(folder):
                    os.makedirs(folder)

                path = os.path.join(folder, 'log.csv')
                df_out.to_csv(path, header=True, index=False)

                script_service = ScriptService()
                script_service.make_script_file({'sql': func_id}, rid)

                use_pre_script = script_service.get_use_pre_script(func_id)
                if use_pre_script:
                    resp_form = ScriptService().run_preprocess_script(file_path=path, rid=rid)
                    if not resp_form.res:
                        return make_json_response(status=400, msg=resp_form.msg)

                return make_json_response(rid=rid)
            else:
                logger.debug(f'get remote log failed : {res_form.msg}')
                return make_json_response(status=500, msg=res_form.msg)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@ANALYSIS.route('/history/<int:func_id>/<int:history_id>')
@ANALYSIS.param('func_id', 'Function ID')
@ANALYSIS.param('history_id', 'History ID')
class AnalysisHistory(Resource):
    @ANALYSIS.response(200, 'Success')
    @ANALYSIS.response(400, 'Bad Request')
    def get(self, func_id, history_id):
        """
        Return Request ID
        """
        logger.info(str(request))

        try:
            dao_history = DAOHistory()
            resp_form = dao_history.get_rid(history_id)
            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)

            rid = resp_form.data

            return make_json_response(rid=rid)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))


@ANALYSIS.route('/history/new')
class SaveHistory(Resource):
    parser = ANALYSIS.parser()
    parser.add_argument('func_id', type=int, location='json', required=True, help='Function ID')
    parser.add_argument('source', type=str, location='json', required=True, help='local/remote/sql')
    parser.add_argument('info', type=dict, location='json', help='local/remote/sql additional info.')
    parser.add_argument('infos', type=list, location='json', help='local/remote/sql additional info.')
    parser.add_argument('title', type=str, location='json', required=True, help='Title Info')
    parser.add_argument('period', type=dict, location='json', required=True, help='Period(Start~End)')
    parser.add_argument('filter', type=dict, location='json', required=True, help='Filter Info')
    parser.add_argument('aggregation', type=dict, location='json', required=True, help='Aggregation Info')
    parser.add_argument('visualization', type=dict, location='json', required=True, help='Visualization Info')

    @ANALYSIS.expect(parser)
    @ANALYSIS.response(200, 'Success')
    @ANALYSIS.response(400, 'Bad Request')
    def post(self):
        """
        Save History Info.
        """
        logger.info(str(request))

        history_id = None

        try:
            args = self.parser.parse_args()

            dao_history = DAOHistory()
            dao_function = DAOFunction()

            source = args['source']
            func_id = args['func_id']
            if source == 'history':
                resp_form = dao_function.get_source_type(func_id)
                if not resp_form.res:
                    return make_json_response(status=400, msg='No matching function id.')
                source = resp_form.data

            infos = dict()
            infos['func_id'] = func_id
            infos['period_start'] = args['period']['start']
            infos['period_end'] = args['period']['end']
            infos['source'] = source
            infos['title'] = args['title']

            resp_form = dao_history.insert_history(**infos)
            if not resp_form.res:
                return make_json_response(status=400, msg=resp_form.msg)

            history_id = resp_form.data

            infos = dict()
            infos['history_id'] = history_id

            subinfo = dict()
            if source == 'local':
                subinfo['rid'] = args['info']['rid']
                resp_form = dao_history.insert_history_from_local(**{**infos, **subinfo})
            elif source == 'remote':
                subinfo['equipment_name'] = args['info']['equipment_name']
                # subinfo['user_fab'] = args['remote']['user_fab']
                subinfo['rid'] = args['info']['rid']
                subinfo['db_id'] = args['info']['db_id']
                resp_form = dao_history.insert_history_from_remote(**{**infos, **subinfo})
            elif source == 'sql':
                subinfo['db_id'] = args['info']['db_id']
                subinfo['rid'] = args['info']['rid']
                subinfo['sql'] = args['info']['sql']
                resp_form = dao_history.insert_history_from_sql(**{**infos, **subinfo})
            elif source == 'multi':
                for arg in args['infos']:
                    if 'multi_info_id' in arg:
                        arg.pop('multi_info_id')

                    resp_form = dao_history.insert_history_from_multi(**{**infos, **arg})
                    if not resp_form.res:
                        dao_history.delete_history_id(history_id)
                        return make_json_response(status=400, msg=resp_form.msg)

            if not resp_form.res:
                dao_history.delete_history_id(history_id)
                return make_json_response(status=400, msg=resp_form.msg)

            if 'filter' in args:
                filter = args['filter']
                for key, val in filter.items():
                    if len(val) > 0:
                        for i in range(len(val)):
                            subinfo = dict()
                            subinfo['key'] = key
                            subinfo['val'] = val[i]
                            resp_form = dao_history.insert_filter_history(**{**infos, **subinfo})
                            if not resp_form.res:
                                dao_history.delete_history_id(history_id)
                                return make_json_response(status=400, msg=resp_form.msg)
                    else:
                        subinfo = dict()
                        subinfo['key'] = key
                        # subinfo['val'] = None
                        resp_form = dao_history.insert_filter_history(**{**infos, **subinfo})
                        if not resp_form.res:
                            dao_history.delete_history_id(history_id)
                            return make_json_response(status=400, msg=resp_form.msg)

            if 'aggregation' in args:
                aggregation = args['aggregation']
                for key, val in aggregation.items():
                    subinfo = dict()
                    subinfo['type'] = key
                    subinfo['val'] = val
                    resp_form = dao_history.insert_aggregation_history(**{**infos, **subinfo})
                    if not resp_form.res:
                        dao_history.delete_history_id(history_id)
                        return make_json_response(status=400, msg=resp_form.msg)

            if 'visualization' in args:
                visualization = args['visualization']
                for item in visualization['items']:
                    if 'id' in item:
                        item.pop('id')
                    item['type'] = ','.join(item['type'])
                    item['y_axis'] = ','.join(item['y_axis'])
                    resp_form = dao_history.insert_visualization_history(**{**infos, **item})
                    # resp_form = self.insert(table='analysis.visualization_default', data={**item, 'func_id': func_id})
                    if not resp_form.res:
                        dao_history.delete_history_id(history_id)
                        return make_json_response(status=400, msg=resp_form.msg)

            return Response(status=200)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            if history_id is not None:
                DAOHistory().delete_history_id(history_id)
            return make_json_response(status=400, msg=str(e))


@ANALYSIS.route('/history/<int:history_id>')
@ANALYSIS.param('history_id', 'History ID')
class DeleteHistory(Resource):
    @ANALYSIS.response(200, 'Success')
    @ANALYSIS.response(400, 'Bad Request')
    def delete(self, history_id):
        logger.info(str(request))

        try:
            dao_history = DAOHistory()
            dao_history.delete_history_id(history_id)
            return Response(status=200)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return make_json_response(status=400, msg=str(e))
