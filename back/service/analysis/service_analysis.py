import os
import datetime
import time
from copy import deepcopy
from multiprocessing import Process, Manager
import pandas as pd
from flask import json
import numpy as np
import logging
import traceback
from pandas.api.types import is_numeric_dtype, is_string_dtype

from service.script.service_script import ScriptService
from service.resources.service_resources import ResourcesService
from dao.dao_analysis_items import DAOAnalysisItems
from dao.dao_base import DAOBaseClass
from dao.dao_function import DAOFunction
from dao.dao_management_setting import DAOMGMTSetting
from config.app_config import *
import convert as lc

from common.utils.response import ResponseForm
from common.utils import calculator, preprocessing

LOG_NAME = 'PLATEAUTOFOCUSCOMPENSATION'

logger = logging.getLogger(LOG)


class AnalysisService:
    def __init__(self):
        pass

    def __del__(self):
        print('__del__', __class__)

    def get_remote_log(self, func_id, **kwargs):
        try:
            db_id = kwargs['db_id']
            source = kwargs['source']

            dao_mgmt = DAOMGMTSetting()
            df = dao_mgmt.fetch_all(args={'where': f"target = 'remote' and id = {db_id}"})

            if len(df) == 0:
                return ResponseForm(res=False, msg='Cannot find any matching db id')

            # connection check
            conf = df.iloc[0].to_dict()
            conf['user'] = conf.pop('username')

            dao_remote = DAOBaseClass(**conf)
            resp_form = dao_remote.connection_check()
            if not resp_form.res:
                logger.debug(f'connection check failed : {resp_form.msg}')
                return resp_form

            # Get Source Information
            dao_func = DAOFunction()
            resp_form = dao_func.get_source_info(func_id)
            if not resp_form.res:
                return ResponseForm(res=False, msg='No Matching Information.')

            source_info = resp_form.data

            if source == 'remote':
                table_name = source_info['table_name']
                equipment_name = kwargs['equipment_name']
                period = kwargs['period']

                if '~' not in period:
                    return ResponseForm(res=False, msg='Please Check period. It must be contained "~"')

                [start, end] = period.split('~')

                filter = {'equipment_name': equipment_name, 'log_time': {'start': start, 'end': end}}
                log_count = dao_remote.load_data(table=table_name, **filter)
                if not log_count:
                    return ResponseForm(res=False, msg='There is no matching log data.')

                df = dao_remote.get_df()
            else:
                sql = source_info['sql']
                df = dao_remote.read_sql(query=sql)
                if len(df) == 0:
                    return ResponseForm(res=False, msg='There is no matching log data.')

            return ResponseForm(res=True, data=df)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_analysis(self, func_id, rid, **args):
        try:
            dao_base = DAOBaseClass(table_name='analysis.function')
            func_dict = dao_base.fetch_one(args={'select': 'analysis_type', 'where': f'id={func_id}'})
            if func_dict is None:
                return ResponseForm(res=False, msg='no matching function id.')
            #
            # log_name = func_dict['log_name']
            analysis_type = func_dict['analysis_type']
            #
            # dao_convert = self.get_convert_dao(log_name)
            # len = dao_convert.load_data(rid=rid, **args['filter'])
            # if len == 0:
            #     return ResponseForm(res=False, msg='Nothing to Analysis.')
            # convert_df = dao_convert.get_df()
            convert_df = preprocessing.load_data(rid=rid, **args['filter'])

            aggregation = {'aggregation': dict()}
            disp_order = list()
            disp_graph = list()

            if convert_df is not None and len(convert_df) > 0:
                if analysis_type == 'none':
                    df_result = convert_df
                elif analysis_type == 'setting':
                    resp_form = self.exec_analysis(src_df=convert_df, func_id=func_id, rid=rid, **args)
                    if not resp_form.res:
                        return resp_form

                    df_result = resp_form.data

                    aggregation_type = args['aggregation']['type']
                    aggregation_val = args['aggregation']['val']

                    resp_form = self.get_aggregation_default(key_id=func_id, rid=rid)
                    if not resp_form.res:
                        return resp_form

                    aggregation = resp_form.data
                    aggregation['aggregation']['selected'] = aggregation_type
                    if aggregation_type in aggregation['aggregation']['subItem']:
                        aggregation['aggregation']['subItem'][aggregation_type]['selected'] = aggregation_val
                elif analysis_type == 'script':
                    dao_func = DAOFunction()
                    resp_form = dao_func.get_script(table='analysis.analysis_script', func_id=func_id)
                    if not resp_form.res:
                        return ResponseForm(res=False, msg='Cannot Find Analysis Script Info')

                    info = {
                        'db_id': resp_form.data['db_id'],
                        'sql': resp_form.data['sql']
                    }
                    resp_form = ScriptService().run_generic_analysis_script(df=convert_df, rid=rid, **info)
                    if not resp_form.res:
                        return resp_form
                    df_result = resp_form.data
                else:
                    return ResponseForm(res=False, msg='Undefined analysis type.')

                if 'No.' not in df_result.columns:
                    df_result.reset_index(inplace=True)
                    df_result['index'] = df_result['index'] + 1
                    disp_str_dict = {'index': 'No.'}
                    df_result.rename(columns=disp_str_dict, inplace=True)

                disp_order = df_result.columns.values.tolist()
                if 'log_time' in disp_order:
                    disp_order.remove('log_time')
                    disp_order.insert(0, 'log_time')

                if 'No.' in disp_order:
                    disp_order.remove('No.')
                    disp_order.insert(0, 'No.')

                for col in df_result.columns:
                    try:
                        df_result[col].astype({col: np.float})
                        disp_graph.append(col)
                    except Exception:
                        pass
            else:
                df_result = None

            resp_form = self.get_options(func_id, rid)
            if not resp_form.res:
                return resp_form

            options = resp_form.data
            if analysis_type == 'script':
                # We don't use filter setting on Script Analysis.
                options['filter'] = list()

            if 'log_time' in args['filter']:
                selected_period = [args['filter']['log_time']['start'], args['filter']['log_time']['end']]
                options['period']['selected'] = selected_period

            for item in options['filter']:
                if item['target'] in args['filter']:
                    item['selected'] = args['filter'][item['target']]
                else:
                    item['selected'] = list()

            ret = dict()
            ret['option'] = {**options, **aggregation}
            ret['data'] = {
                'disp_order': disp_order,
                'disp_graph': disp_graph,
                'row': dict() if df_result is None else df_result.to_dict(orient='index')
            }

            return ResponseForm(res=True, data=ret)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_analysis_by_setting(self, df, rid=None, **kwargs):
        filter_list = kwargs['filter_default']
        aggregation = kwargs['aggregation_default']

        for filter in filter_list:
            key = filter['key']
            val = filter['val']
            if val is not None and len(val) > 0:
                if key in df.columns:
                    if key == 'log_time':
                        start = val['start']
                        end = val['end']
                        try:
                            datetime.datetime.strptime(end, '%Y-%m-%d')
                            end = end + ' 23:59:59'
                        except Exception as e:
                            pass
                        df = df[(start <= df['log_time']) & (df['log_time'] <= end)]
                    else:
                        df_copy = df.astype({key: str})

                        if isinstance(val, list):
                            if len(val) > 0:
                                val = [str(_) for _ in val]
                                df = df[df_copy[key].isin(val)]
                        else:
                            df = df[df_copy[key] == str(val)]
                            # df = df[df[filter['key']].isin(filter['val'])]
        # df.reset_index(drop=True, inplace=True)

        if len(df) == 0:
            df = df.astype(float)
        else:
            df = df.astype({'log_time': 'datetime64'})

        analysis_items = kwargs['items']

        analysis_items_df = pd.DataFrame(analysis_items)
        analysis_items_df['source_col'] = analysis_items_df['source_col'].apply(lambda x: ','.join(x) if isinstance(x, list) else x)

        args = {'filter': filter_list, 'aggregation': aggregation}
        return self.exec_analysis(src_df=df, item_df=analysis_items_df, rid=rid, **args)

    def get_analysis_preview_by_script(self, df, **kwargs):
        if len(df) == 0:
            df = df.astype(float)
        else:
            df = df.astype({'log_time': 'datetime64'})

        use_script = kwargs['use_script']

        if not use_script:
            return self.get_analysis_preview_by_none(df, **{'filter_default': list()})
        else:
            script_service = ScriptService()
            resp_form = script_service.preview_generic_analysis_script(df, **kwargs)
            if resp_form.res:
                df = resp_form.data

                return ResponseForm(res=True, data=df)
            else:
                return resp_form

    def get_analysis_preview_by_none(self, df, **kwargs):
        filter_list = kwargs['filter_default']

        for filter in filter_list:
            if filter['val'] is not None and len(filter['val']) > 0:
                df = df[df[filter['key']].isin(filter['val'])]
        df.reset_index(drop=True, inplace=True)

        return ResponseForm(res=True, data=df)

    def get_multi_analysis_by_none(self, objects, **kwargs):
        filter_list = kwargs['filter_default']

        for filter in filter_list:
            if filter['val'] is not None and len(filter['val']) > 0:
                key = filter['key']
                val = filter['val']
                for tab_name, df in objects.items():
                    if key in df.columns:
                        if key == 'log_time':
                            start = val['start']
                            end = val['end']
                            try:
                                datetime.datetime.strptime(end, '%Y-%m-%d')
                                end = end + ' 23:59:59'
                            except Exception as e:
                                pass
                            df = df[(start <= df['log_time']) & (df['log_time'] <= end)]
                        else:
                            df_copy = df.astype({key: str})

                            if isinstance(val, list):
                                if len(val) > 0:
                                    val = [str(_) for _ in val]
                                    df = df[df_copy[key].isin(val)]
                            else:
                                df = df[df_copy[key] == str(val)]

                        # df = df[df[filter['key']].isin(filter['val'])]
                        df.reset_index(drop=True, inplace=True)
                        objects[tab_name] = df

        return ResponseForm(res=True, data=objects)

    def exec_analysis(self, src_df=None, func_id=None, item_df=None, rid=None, **args):
        if func_id is not None:
            dao_analysis_items = DAOAnalysisItems(func_id=func_id)
        else:
            dao_analysis_items = DAOAnalysisItems(df=item_df)

        analysis_result = None
        total_merge_df = None

        aggregation_type = args['aggregation']['type']
        aggregation_val = args['aggregation']['val']

        if aggregation_type == 'column':
            group = aggregation_val
        elif aggregation_type == 'period':
            group = aggregation_type
            if len(src_df) == 0:
                src_df['period'] = None
            else:
                log_start = str(src_df['log_time'].min())
                src_df = preprocessing.divide_by_stats_period(src_df, log_start, aggregation_val)
        else:
            group = None

        group_analysis_list = dao_analysis_items.get_analysis_list_by_order()

        for item in group_analysis_list:
            group_analysis = item['group_analysis']
            group_analysis_type = item['group_analysis_type']
            try:
                group_df = self.exec_calculate(group_analysis, group_analysis_type, src_df, item['source_col'], group=group, rid=rid)
                if isinstance(group_df, pd.Series):
                    group_df = pd.DataFrame(group_df).T
                elif isinstance(group_df, (np.int64, np.float64)):
                    group_df = pd.DataFrame({item['source_col']: [group_df]})

                disp_str_dict = dict()
                if item['source_col'] in group_df.columns:
                    disp_str_dict[item['source_col']] = item['title']
                else:
                    col_list = item['source_col'].split(sep=',')
                    for item_col in col_list:
                        if '/' in item_col:
                            [tab_name, column] = item_col.split(sep='/')
                        else:
                            column = item_col

                        if column in group_df.columns:
                            disp_str_dict[column] = item['title']

                    disp_str_dict[0] = item['title']

                # cp_group_df = deepcopy(group_df)
                group_df.rename(columns=disp_str_dict, inplace=True)

                if analysis_result is None:
                    analysis_result = group_df
                else:
                    analysis_result = analysis_result.reset_index().merge(group_df.reset_index(),
                                                                          how='left').set_index('index')

                total_analysis = item['total_analysis']
                total_analysis_type = item['total_analysis_type']

                total_df = self.exec_calculate(total_analysis, total_analysis_type, group_df, item['title'], rid=rid)
                if total_df is not None:
                    if isinstance(total_df, pd.Series):
                        total_df = pd.DataFrame(total_df, columns=['ALL']).T
                    elif isinstance(total_df, (np.int64, np.float64)):
                        total_df = pd.DataFrame({item['source_col']: total_df}, index=['ALL'])

                    if len(total_df) > 1:
                        return ResponseForm(res=False, msg=f"Result of Total Analysis has multiple value."
                                                           f" Use analysis type like max/min/ave/sum/3sigma etc.")

                    if total_merge_df is None:
                        total_merge_df = total_df
                    else:
                        total_merge_df = pd.concat([total_merge_df, total_df], axis=1)

                    # if total_merge_df is not None:
                    #     total_merge_df.rename(columns=disp_str_dict, inplace=True)

            except Exception as e:
                logger.error(str(e))
                logger.error(traceback.format_exc())
                return ResponseForm(res=False, msg=str(e))

        if analysis_result is not None:
            if group == 'period':
                analysis_result.rename(columns={'period': 'log_time'}, inplace=True)
            else:
                cell_df = deepcopy(src_df)
                cell_df = calculator.calc_formula('min', cell_df, 'log_time', group)
                if isinstance(cell_df, pd.Series):
                    cell_df = pd.DataFrame(cell_df).T
                elif isinstance(cell_df, pd._libs.tslibs.timestamps.Timestamp):
                    cell_df = pd.DataFrame({'log_time': [cell_df]})
                elif isinstance(cell_df, np.datetime64):
                    cell_df = pd.DataFrame({'log_time': [cell_df]})

                analysis_result = analysis_result.reset_index().merge(cell_df.reset_index(),
                                                                      how='left').set_index('index')

            analysis_result.reset_index(inplace=True)
            analysis_result['index'] = analysis_result['index'] + 1
            disp_str_dict = {'index': 'No.'}

            if total_merge_df is not None:
                total_merge_df.reset_index(inplace=True)
                analysis_result = pd.concat([analysis_result, total_merge_df])
                analysis_result.reset_index(inplace=True, drop=True)

            analysis_result.rename(columns=disp_str_dict, inplace=True)

            return ResponseForm(res=True, data=analysis_result)
        else:
            return ResponseForm(res=False, msg='There is nothing to summary.')

    def exec_calculate(self, formula, type, df, col, group=None, rid=None):
        output_df = pd.DataFrame()
        column_list = list()
        col_list = col.split(sep=',')
        for item in col_list:
            if '/' in item:
                [tab_name, column] = item.split(sep='/')
                if tab_name in df.index and column in df.columns:
                    if group is not None:
                        output_df = pd.concat([output_df, df.loc[tab_name][[column, group]]])
                    else:
                        output_df = pd.concat([output_df, df.loc[tab_name][[column]]])
                    column_list.append(column)
            else:
                if item in df.columns:
                    if group is not None:
                        output_df = pd.concat([output_df, df[[item, group]]])
                    else:
                        output_df = pd.concat([output_df, df[[item]]])
                    column_list.append(item)

        if group is not None:
            output_df[group] = output_df[group].fillna('None')

        column_list = list(set(column_list))

        if type == 'sequential':
            formula_list = formula.split('.')
            final_grp_formula_list = ['min', 'max', 'ave', 'sum', '3sigma']
            if group is not None and formula_list[-1] not in final_grp_formula_list:
                err_str = f"Cannot use '{formula}' with group analysis." \
                          f"Group analysis should finish with one of {final_grp_formula_list}"
                raise Exception(err_str)
            for form in formula_list:
                output_df = calculator.calc_formula(form, output_df, column_list, group)
        elif type == 'script':
            output_df = calculator.calc_formula(formula, output_df, column_list, group, script=True, rid=rid)
        else:
            output_df = calculator.calc_formula(formula, output_df, column_list, group)

        return output_df

    def get_detail(self, func_id, rid, **args):
        try:
            dao_base = DAOBaseClass(table_name='analysis.function')
            func_dict = dao_base.fetch_one(args={'select': 'analysis_type', 'where': f'id={func_id}'})
            if func_dict is None:
                return ResponseForm(res=False, msg='no matching function id.')

            analysis_type = func_dict['analysis_type']

            convert_df = preprocessing.load_data(rid=rid, **args['filter'])
            if convert_df is None or len(convert_df) == 0:
                return ResponseForm(res=False, msg='Log Data Empty.')

            if analysis_type == 'setting':
                if 'type' not in args['aggregation']\
                        or 'val' not in args['aggregation']\
                        or 'selected' not in args['aggregation']:
                    return ResponseForm(res=False, msg='aggregation info empty.')

                dao_analysis_items = DAOAnalysisItems(func_id=func_id)
                columns_str = dao_analysis_items.get_columns_comma_separated()
                if columns_str is not None:
                    columns = dao_analysis_items.get_column_list()

                    aggregation_type = args['aggregation']['type']
                    aggregation_val = args['aggregation']['val']
                    selected = args['aggregation']['selected']

                    if aggregation_type == 'column':
                        column = aggregation_val
                        convert_df = convert_df.astype({column: str})
                        df = convert_df[convert_df[column].isin(selected)]
                    elif aggregation_type == 'period':
                        column = 'period'
                        aggregation_val = aggregation_val
                        log_start = str(convert_df['log_time'].min())
                        convert_df = preprocessing.divide_by_stats_period(convert_df, log_start, aggregation_val)
                        df = convert_df[convert_df[column].isin(selected)]
                    else:
                        df = convert_df
                        column = None

                    if 'process' in df.columns:
                        columns.append('process')

                    if 'device' in df.columns:
                        columns.append('device')

                    if 'log_time' in df.columns:
                        columns.append('log_time')

                    if column is not None and column not in columns:
                        columns.append(column)

                    df = df[columns]

                    df.reset_index(inplace=True, drop=True)
                    df.reset_index(inplace=True)
                    df['index'] = df['index'] + 1
                    disp_order = dao_analysis_items.sort_by_column_order(df.columns, column)
                    disp_graph = []
                    for col in df.columns:
                        try:
                            df[col].astype({col: np.float})
                            disp_graph.append(col)
                        except Exception:
                            pass
                    if 'index' in disp_graph:
                        disp_graph.remove('index')

                    ########### SET Options #############
                    filter_list = []
                    if aggregation_type != 'all':
                        filter_option = dict()
                        filter_option['target'] = column
                        filter_option['title'] = column
                        filter_option['type'] = 'select'
                        filter_option['mode'] = 'plural'
                        filter_option['selected'] = selected
                        filter_option['options'] = selected
                        filter_list.append(filter_option)
                    ######################################

                    df_graph_type = dao_base.fetch_all(table='public.graph_type')
                    df_graph_type.sort_values(by='id', inplace=True)
                    graph_type = [df_graph_type['type'].values[0]]
                    if 'log_time' in disp_order:
                        x_axis = 'log_time'
                    elif 'period' in disp_order:
                        x_axis = 'period'
                    else:
                        x_axis = None

                    items = list()
                    if x_axis is not None:
                        for column in disp_graph:
                            item = dict()
                            item['title'] = column
                            item['type'] = graph_type
                            item['x_axis'] = x_axis
                            item['y_axis'] = [column]
                            item['z_axis'] = None
                            item['x_range_min'] = None
                            item['x_range_max'] = None
                            item['y_range_min'] = None
                            item['y_range_max'] = None
                            item['z_range_min'] = None
                            item['z_range_max'] = None

                            items.append(item)

                    rtn_dict = {
                        'data': {
                            'disp_order': disp_order,
                            'disp_graph': disp_graph,
                            'row': df.to_dict(orient='index')
                        },
                        'option': {
                            'filter': filter_list
                        },
                        'visualization': {
                            'items': items
                        }
                    }

                    return ResponseForm(res=True, data=rtn_dict)
                else:
                    return ResponseForm(res=False, msg='There is no Analysis Items.')
            else:
                disp_order = convert_df.columns.values.tolist()
                if 'log_time' in disp_order:
                    disp_order.remove('log_time')
                    disp_order.insert(0, 'log_time')

                if 'No.' in disp_order:
                    disp_order.remove('No.')
                    disp_order.insert(0, 'No.')

                disp_graph = list()
                for col in convert_df.columns:
                    try:
                        convert_df[col].astype({col: np.float})
                        disp_graph.append(col)
                    except Exception:
                        pass

                df_graph_type = dao_base.fetch_all(table='public.graph_type')
                df_graph_type.sort_values(by='id', inplace=True)
                graph_type = [df_graph_type['type'].values[0]]
                if 'log_time' in disp_order:
                    x_axis = 'log_time'
                elif 'period' in disp_order:
                    x_axis = 'period'
                else:
                    x_axis = None

                items = list()
                if x_axis is not None:
                    for column in disp_graph:
                        item = dict()
                        item['title'] = column
                        item['type'] = graph_type
                        item['x_axis'] = x_axis
                        item['y_axis'] = [column]
                        item['z_axis'] = None
                        item['x_range_min'] = None
                        item['x_range_max'] = None
                        item['y_range_min'] = None
                        item['y_range_max'] = None
                        item['z_range_min'] = None
                        item['z_range_max'] = None

                        items.append(item)

                rtn_dict = {
                    'data': {
                        'disp_order': disp_order,
                        'disp_graph': disp_graph,
                        'row': convert_df.to_dict(orient='index')
                    },
                    'option': {
                        'filter': list()
                    },
                    'visualization': {
                        'items': items
                    }
                }

                return ResponseForm(res=True, data=rtn_dict)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_multi_detail(self, func_id, **kwargs):
        dao_func = DAOFunction()
        resp_form = dao_func.get_source_info(func_id)
        if not resp_form.res:
            return resp_form

        df_info = resp_form.data

        row = dao_func.fetch_one(args={'select': 'analysis_type', 'where': f'id={func_id}'})
        if row is None:
            return ResponseForm(res=False, msg='no matching function id.')

        analysis_type = row['analysis_type']

        objects = dict()
        for i in range(len(df_info)):
            rid = df_info['rid'].values[i]
            tab_name = df_info['tab_name'].values[i]

            df = preprocessing.load_data(rid=rid, **kwargs['filter'])
            objects[tab_name] = df

        filter_list = list()

        if analysis_type == 'setting':
            if 'type' not in kwargs['aggregation'] \
                    or 'val' not in kwargs['aggregation'] \
                    or 'selected' not in kwargs['aggregation']:
                return ResponseForm(res=False, msg='aggregation info empty.')

            aggregation_type = kwargs['aggregation']['type']
            aggregation_val = kwargs['aggregation']['val']
            selected = kwargs['aggregation']['selected']

            for tab_name, df in objects.items():
                if aggregation_type == 'column':
                    column = aggregation_val
                    if column not in df.columns:
                        df[column] = None
                    df = df.astype({column: str})
                    df = df[df[column].isin(selected)]
                    objects[tab_name] = df
                elif aggregation_type == 'period':
                    column = 'period'
                    log_start = str(df['log_time'].min())
                    df = preprocessing.divide_by_stats_period(df, log_start, aggregation_val)
                    df = df[df[column].isin(selected)]
                    objects[tab_name] = df
                else:
                    continue

            ########### SET Options #############
            if aggregation_type != 'all':
                filter_option = dict()
                filter_option['target'] = column
                filter_option['title'] = column
                filter_option['type'] = 'select'
                filter_option['mode'] = 'plural'
                filter_option['selected'] = selected
                filter_option['options'] = selected
                filter_list.append(filter_option)
            ######################################

        data = dict()
        common_axis_x = list()
        for tab_name, df in objects.items():
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

        df_graph_type = dao_func.fetch_all(table='public.graph_type')
        df_graph_type.sort_values(by='id', inplace=True)
        graph_type = [df_graph_type['type'].values[0]]
        items = list()

        if 'log_time' in common_axis_x:
            x_axis = 'log_time'
        elif 'period' in common_axis_x:
            x_axis = 'period'
        else:
            x_axis = None

        if x_axis is not None:
            for key, val in data.items():
                tab_name = key
                disp_graph = val['disp_graph']

                for column in disp_graph:
                    item = dict()
                    item['title'] = f'{tab_name}_{column}'
                    item['type'] = graph_type
                    item['x_axis'] = x_axis
                    item['y_axis'] = [f'{tab_name}/{column}']
                    item['z_axis'] = None
                    item['x_range_min'] = None
                    item['x_range_max'] = None
                    item['y_range_min'] = None
                    item['y_range_max'] = None
                    item['z_range_min'] = None
                    item['z_range_max'] = None

                    items.append(item)

        rtn_dict = {
            'data': data,
            'option': {
                'filter': filter_list
            },
            'visualization': {
                'common_axis_x': common_axis_x,
                'items': items
            }
        }

        return ResponseForm(res=True, data=rtn_dict)

    def get_analysis_type(self, func_id):
        dao_func = DAOBaseClass(table_name='analysis.function')
        row = dao_func.fetch_one(args={'select': 'analysis_type', 'where': f"id='{func_id}'"})
        if row is None:
            return ResponseForm(res=False, msg='No matching func_id')

        return ResponseForm(res=True, data=dict(row))

    def get_options(self, key_id, rid=None, df=None, is_history=False):
        try:
            if df is None:
                log_df = preprocessing.load_data(rid=rid)
            else:
                log_df = df

            if log_df is None or len(log_df) == 0:
                return ResponseForm(res=False, msg='Log Data Empty.')

            period = preprocessing.get_data_period(log_df)
            if period is None:
                return ResponseForm(res=False, msg='No "log_time" column.')

            data = dict()
            data['period'] = {**period, 'selected': [period['start'], period['end']]}

            if is_history:
                dao_filter_default = DAOBaseClass(table_name='history.filter_history')
                df_filter_default = dao_filter_default.fetch_all(args={'where': f"history_id='{key_id}'"})
            else:
                dao_filter_default = DAOBaseClass(table_name='analysis.filter_default')
                df_filter_default = dao_filter_default.fetch_all(args={'where': f"func_id='{key_id}'"})

            filter_list = []
            for key in df_filter_default['key'].unique().tolist():
                if key in log_df.columns:
                    filter = dict()
                    filter['target'] = key
                    filter['title'] = key
                    filter['type'] = 'select'
                    filter['mode'] = 'plural'
                    selected_list = df_filter_default[df_filter_default['key'] == key]['val'].tolist()
                    selected_list = [_ for _ in selected_list if _ is not None]
                    filter['selected'] = selected_list
                    filter['options'] = log_df[key].unique().tolist()

                    filter_list.append(filter)

            data['filter'] = filter_list

            return ResponseForm(res=True, data=data)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_aggregation_default(self, key_id, rid=None, df=None, is_history=False):
        try:
            if is_history:
                dao_aggregation_default = DAOBaseClass(table_name='history.aggregation_history')
                dict_aggregation_default = dao_aggregation_default.fetch_one(args={'where': f"history_id='{key_id}'"})
            else:
                dao_aggregation_default = DAOBaseClass(table_name='analysis.aggregation_default')
                dict_aggregation_default = dao_aggregation_default.fetch_one(args={'where': f"func_id='{key_id}'"})

            resp_form = self.get_aggreg_form()
            if not resp_form.res:
                return ResponseForm(res=False, msg='get json form file fail.')

            aggreg_form = resp_form.data

            dao_aggregation_type = DAOBaseClass(table_name='public.aggregation_type')
            df_aggregation_type = dao_aggregation_type.fetch_all()
            aggregation_type_list = df_aggregation_type['type'].tolist()

            aggreg_form['options'] = aggregation_type_list
            if dict_aggregation_default is None:
                aggreg_form['selected'] = 'all'
            else:
                aggreg_form['selected'] = dict_aggregation_default['type']

            for key, val in aggreg_form['subItem'].items():
                if dict_aggregation_default is not None:
                    if key == dict_aggregation_default['type']:
                        val['selected'] = dict_aggregation_default['val']

                if key == 'column':
                    if df is None:
                        log_df = preprocessing.load_data(rid=rid)
                    else:
                        log_df = df

                    if log_df is None or len(log_df) == 0:
                        return ResponseForm(res=False, msg='Log Data Empty.')

                    col_options = []
                    for column in log_df.columns:
                        """
                        is_numeric_dtype() : True when dtype is int64 or float64 or bool.
                        is_string_dtype() : True when dtype is object or category.
                        """
                        if is_numeric_dtype(log_df[column]) or is_string_dtype(log_df[column]):
                            col_options.append(column)

                    val['options'] = col_options

            data = dict()
            data['aggregation'] = aggreg_form
            return ResponseForm(res=True, data=data)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_visualization_default(self, func_id):
        try:
            resp_form = ResourcesService().get_visualization_info(func_id)
            if not resp_form.res:
                return resp_form

            return ResponseForm(res=True, data={'visualization': resp_form.data})
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_aggreg_form(self):
        try:
            with open(os.path.join(RESOURCE_PATH, RSC_JSON_OPT_AGGREG_FORM), 'r') as f:
                json_data = json.load(f)

            return ResponseForm(res=True, data=json_data)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))
