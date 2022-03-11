import logging
import traceback

from dao.dao_base import DAOBaseClass
from common.utils.response import ResponseForm
from config.app_config import *

logger = logging.getLogger(LOG)


class DAOFunction(DAOBaseClass):
    TABLE_NAME = 'analysis.function'

    def __init__(self):
        super().__init__(table_name=DAOFunction.TABLE_NAME)

    def __del__(self):
        super().__del__()
        print('__del__', __class__)

    def get_category_info(self, func_id):
        try:
            row = self.fetch_one(args={'select': 'category_id', 'where': f"id={func_id}"})
            if row is None:
                return ResponseForm(res=False, msg='No matching function info')

            category_id = row['category_id']

            row = self.fetch_one(table='analysis.category', args={'where': f"id={category_id}"})
            if row is None:
                return ResponseForm(res=False, msg='No matching category info')

            dict_row = dict(row)
            for key in ['id']:
                if key in dict_row:
                    dict_row.pop(key)

            return ResponseForm(res=True, data=dict_row)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_source_type(self, func_id):
        try:
            row = self.fetch_one(args={'select': 'source_type', 'where': f"id={func_id}"})
            if row is None:
                return ResponseForm(res=False, msg='No matching function info')

            source_type = row['source_type']

            return ResponseForm(res=True, data=source_type)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_log_name(self, func_id):
        try:
            row = self.fetch_one(table='analysis.local_info', args={'select': 'log_name', 'where': f"func_id={func_id}"})
            if row is None:
                return ResponseForm(res=False, msg='No matching function info')

            log_name = row['log_name']

            return ResponseForm(res=True, data=log_name)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_source_info(self, func_id):
        try:
            resp_form = self.get_source_type(func_id)
            if not resp_form.res:
                return resp_form

            source_type = resp_form.data

            if source_type == 'multi':
                row = self.fetch_all(table='analysis.multi_info', args={'where': f"func_id={func_id}"})
                if len(row) == 0:
                    return ResponseForm(res=False, msg='Multi Function has no sub-functions.')

                return ResponseForm(res=True, data=row)
            else:
                if source_type == 'local':
                    table_name = 'analysis.local_info'
                elif source_type == 'remote':
                    table_name = 'analysis.remote_info'
                elif source_type == 'sql':
                    table_name = 'analysis.sql_info'
                else:
                    return ResponseForm(res=False, msg='Source type is wrong.')

                row = self.fetch_one(table=table_name, args={'where': f"func_id={func_id}"})
                if row is None:
                    return ResponseForm(res=False, msg='No matching function info')

                dict_row = dict(row)
                for key in ['id', 'func_id']:
                    if key in dict_row:
                        dict_row.pop(key)

                return ResponseForm(res=True, data=dict_row)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_script_file_name(self, table, func_id):
        try:
            row = self.fetch_one(table=table, args={'select': 'file_name', 'where': f"func_id={func_id}"})
            if row is None:
                return ResponseForm(res=False, msg='No matching function info')

            return ResponseForm(res=True, data=row['file_name'])

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_script(self, table, func_id):
        try:
            row = self.fetch_one(table=table, args={'where': f"func_id={func_id}"})
            if row is None:
                return ResponseForm(res=False, msg='No matching function info')

            dict_row = dict(row)
            for key in ['id', 'func_id']:
                if key in dict_row:
                    dict_row.pop(key)

            return ResponseForm(res=True, data=dict_row)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_function_info(self, func_id):
        try:
            row = self.fetch_one(args={'where': f"id={func_id}"})
            if row is None:
                return ResponseForm(res=False, msg='No matching function info')

            dict_row = dict(row)
            for key in ['id', 'category_id']:
                if key in dict_row:
                    dict_row.pop(key)

            return ResponseForm(res=True, data=dict_row)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_analysis_items_info(self, func_id):
        try:
            df = self.fetch_all(table='analysis.analysis_items', args={'where': f"func_id={func_id}"})
            if len(df) == 0:
                return ResponseForm(res=False, msg='No matching analysis items info')

            for key in ['func_id', 'id']:
                if key in df.columns:
                    df.drop(key, axis=1, inplace=True)

            return ResponseForm(res=True, data=df.to_dict(orient='records'))
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_filter_default_info(self, func_id):
        try:
            df = self.fetch_all(table='analysis.filter_default', args={'where': f"func_id={func_id}"})
            if len(df) == 0:
                return ResponseForm(res=False, msg='No matching filter default info')

            for key in ['func_id', 'id']:
                if key in df.columns:
                    df.drop(key, axis=1, inplace=True)

            filter_default = list()
            for key in df['key'].unique().tolist():
                item = dict()
                item['key'] = key
                item['val'] = df[df['key'] == key]['val'].tolist()
                item['val'] = [_ for _ in item['val'] if _ != '' and _ is not None]
                filter_default.append(item)

            return ResponseForm(res=True, data=filter_default)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_aggregation_default_info(self, func_id):
        try:
            row = self.fetch_one(table='analysis.aggregation_default', args={'where': f"func_id={func_id}"})
            if row is None:
                return ResponseForm(res=False, msg='No matching aggregation default info')

            dict_row = dict(row)
            for key in ['func_id', 'id']:
                if key in dict_row:
                    dict_row.pop(key)

            return ResponseForm(res=True, data=dict_row)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_function_graph_type(self, func_id):
        try:
            df = self.fetch_all(table='graph.function_graph_type', args={'where': f"func_id={func_id}"})
            if len(df) == 0:
                return ResponseForm(res=False, msg='No matching visualization default info')

            for key in ['func_id']:
                if key in df.columns:
                    df.drop(key, axis=1, inplace=True)

            df['id'] = None

            return ResponseForm(res=True, data=df.to_dict(orient='records'))
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_visualization_default_info(self, func_id):
        try:
            df = self.fetch_all(table='analysis.visualization_default', args={'where': f"func_id={func_id}"})
            if len(df) == 0:
                return ResponseForm(res=False, msg='No matching visualization default info')

            for key in ['func_id']:
                if key in df.columns:
                    df.drop(key, axis=1, inplace=True)

            df['id'] = None

            items = list()
            for i in range(len(df)):
                item = dict()
                item['id'] = df['id'].values[i]
                item['title'] = df['title'].values[i]
                item['type'] = [str(_) for _ in df['type'].values[i].split(sep=',')]
                item['x_axis'] = df['x_axis'].values[i]
                item['y_axis'] = [str(_) for _ in df['y_axis'].values[i].split(sep=',')]
                item['z_axis'] = df['z_axis'].values[i]
                item['x_range_min'] = df['x_range_min'].values[i]
                item['x_range_max'] = df['x_range_max'].values[i]
                item['y_range_min'] = df['y_range_min'].values[i]
                item['y_range_max'] = df['y_range_max'].values[i]
                item['z_range_min'] = df['z_range_min'].values[i]
                item['z_range_max'] = df['z_range_max'].values[i]

                items.append(item)

            return ResponseForm(res=True, data=items)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_multi_info(self, func_id, sub_func_id, tab_name):
        try:
            row = self.fetch_one(table='analysis.multi_info', args={'where': f"sub_func_id='{sub_func_id}' "
                                                                             f"and tab_name='{tab_name}' "
                                                                             f"and func_id='{func_id}'"})
            if row is None:
                return ResponseForm(res=False, msg='No matching sub_func_id and tab_name.')

            row_dict = dict(row)

            return ResponseForm(res=True, data=row_dict)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def insert_category_info(self, category):
        try:
            title = category['title']
            row = self.fetch_one(table='analysis.category', args={'where': f"title='{title}'"})
            if row is None:
                return self.insert(table='analysis.category', data=category, rtn_id=True)
            else:
                return ResponseForm(res=True, data=row['id'])
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def insert_func_info(self, func):
        try:
            info = func.pop('info')
            script = func.pop('script')

            resp_form = self.insert(data=func, rtn_id=True)
            if not resp_form.res:
                return resp_form

            func_id = resp_form.data

            source_type = func['source_type']
            if source_type == 'local':
                table = 'analysis.local_info'
            elif source_type == 'remote':
                table = 'analysis.remote_info'
            else:
                table = 'analysis.sql_info'

            resp_form = self.insert(table=table, data={**info, 'func_id': func_id})
            if not resp_form.res:
                return resp_form

            resp_form = self.insert(table='analysis.preprocess_script', data={**script, 'func_id': func_id})
            if not resp_form.res:
                return resp_form

            return ResponseForm(res=True, data=func_id)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def insert_multi_func_info(self, func):
        try:
            info_list = func.pop('info')
            use_org_analysis = func.pop('use_org_analysis')

            if use_org_analysis:
                func['analysis_type'] = 'org'

            resp_form = self.insert(data=func, rtn_id=True)
            if not resp_form.res:
                return resp_form

            func_id = resp_form.data

            for info in info_list:
                sub_func_id = info['func_id']
                resp_form = self.get_source_type(sub_func_id)
                if not resp_form.res:
                    return resp_form

                sub_source_type = resp_form.data
                data = dict()
                data['func_id'] = func_id
                data['sub_func_id'] = sub_func_id
                data['source_type'] = sub_source_type
                data['tab_name'] = info['tab_name']
                data['rid'] = info['rid']

                if sub_source_type == 'local':
                    data['fid'] = ','.join(map(str, info['fid']))
                elif sub_source_type == 'remote':
                    data['db_id'] = info['db_id']
                    data['table_name'] = info['table_name']
                    data['equipment_name'] = info['equipment_name']
                    data['period_start'] = info['period_start']
                    data['period_end'] = info['period_end']
                else:
                    data['db_id'] = info['db_id']
                    data['sql'] = info['sql']

                resp_form = self.insert(table='analysis.multi_info', data=data)
                if not resp_form.res:
                    return resp_form

            return ResponseForm(res=True, data=func_id)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def update_func_info(self, func, func_id):
        try:
            info = func.pop('info')
            script = func.pop('script')

            resp_form = self.update(set={**func}, where={'id': func_id})
            if not resp_form.res:
                return resp_form

            source_type = func['source_type']
            if source_type == 'local':
                table = 'analysis.local_info'
            elif source_type == 'remote':
                table = 'analysis.remote_info'
            else:
                table = 'analysis.sql_info'

            resp_form = self.update(table=table,
                                    set={**info},
                                    where={'func_id': func_id})
            if not resp_form.res:
                return resp_form

            if script['file_name'] is None:
                resp_form = self.update(table='analysis.preprocess_script',
                                        set={**script, 'script': None},
                                        where={'func_id': func_id})
            else:
                resp_form = self.update(table='analysis.preprocess_script',
                                        set={**script},
                                        where={'func_id': func_id})

            return resp_form

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def update_multi_func_info(self, func, func_id):
        try:
            info_list = func.pop('info')
            use_org_analysis = func.pop('use_org_analysis')

            if use_org_analysis:
                func['analysis_type'] = 'org'

            resp_form = self.update(set={**func}, where={'id': func_id})
            if not resp_form.res:
                return resp_form

            add_item_list = list()
            update_item_list = list()
            id_list = list()
            for item in info_list:
                if item['multi_info_id'] is None:
                    add_item_list.append(item)
                else:
                    id_list.append(item['multi_info_id'])
                    update_item_list.append(item)

            for info in update_item_list:
                id = info.pop('multi_info_id')

                sub_func_id = info['func_id']
                resp_form = self.get_source_type(sub_func_id)
                if not resp_form.res:
                    return resp_form

                sub_source_type = resp_form.data
                data = dict()
                data['func_id'] = func_id
                data['sub_func_id'] = sub_func_id
                data['source_type'] = sub_source_type
                data['tab_name'] = info['tab_name']
                data['rid'] = info['rid']

                if sub_source_type == 'local':
                    data['fid'] = ','.join(map(str, info['fid']))
                elif sub_source_type == 'remote':
                    data['db_id'] = info['db_id']
                    data['table_name'] = info['table_name']
                    data['equipment_name'] = info['equipment_name']
                    data['period_start'] = info['period_start']
                    data['period_end'] = info['period_end']
                else:
                    data['db_id'] = info['db_id']
                    data['sql'] = info['sql']

                resp_form = self.update(table='analysis.multi_info',
                                        set=data,
                                        where={'id': id})
                if not resp_form.res:
                    return resp_form

            multi_info_df = self.fetch_all(table='analysis.multi_info',
                                             args={'select': 'id', 'where': f'func_id={func_id}'})
            not_included_df = multi_info_df[~multi_info_df['id'].isin(id_list)]
            for i in range(len(not_included_df)):
                self.delete(table='analysis.multi_info', where_dict={'id': not_included_df['id'].values[i]})

            for info in add_item_list:
                info.pop('multi_info_id')
                sub_func_id = info.pop('func_id')
                resp_form = self.get_source_type(sub_func_id)
                if not resp_form.res:
                    return resp_form
                sub_source_type = resp_form.data

                data = dict()
                data['func_id'] = func_id
                data['sub_func_id'] = sub_func_id
                data['source_type'] = sub_source_type
                data['tab_name'] = info['tab_name']
                data['rid'] = info['rid']

                if sub_source_type == 'local':
                    data['fid'] = ','.join(map(str, info['fid']))
                elif sub_source_type == 'remote':
                    data['db_id'] = info['db_id']
                    data['table_name'] = info['table_name']
                    data['equipment_name'] = info['equipment_name']
                    data['period_start'] = info['period_start']
                    data['period_end'] = info['period_end']
                else:
                    data['db_id'] = info['db_id']
                    data['sql'] = info['sql']

                resp_form = self.insert(table='analysis.multi_info', data=data)
                if not resp_form.res:
                    return resp_form

            return ResponseForm(res=True, data=func_id)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def insert_convert_script(self, script, func_id):
        try:
            return self.insert(table='analysis.convert_script', data={**script, 'func_id': func_id})
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def update_convert_script(self, script, func_id):
        try:
            if script['file_name'] is None:
                resp_form = self.update(table='analysis.convert_script',
                                        set={**script, 'script': None},
                                        where={'func_id': func_id})
            else:
                resp_form = self.update(table='analysis.convert_script',
                                        set={**script},
                                        where={'func_id': func_id})

            return resp_form

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def update_script_file(self, table, func_id, file):
        try:
            file.stream.seek(0)
            data = file.stream.read()
            script = str(data, 'utf-8')
            resp_form = self.update(table=table,
                                    set={'script': script},
                                    where={'func_id': func_id})

            return resp_form

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def insert_analysis_info(self, analysis, func_id):
        try:
            setting = analysis['setting']

            for item in setting['items']:
                if isinstance(item['source_col'], list):
                    item['source_col'] = ','.join(item['source_col'])
                resp_form = self.insert(table='analysis.analysis_items', data={**item, 'func_id': func_id})
                if not resp_form.res:
                    return resp_form

            tmp_filter_list = list()
            for item in setting['filter_default']:
                if item['val'] is None or len(item['val']) == 0:
                    tmp_dict = dict()
                    tmp_dict['key'] = item['key']
                    tmp_dict['val'] = None
                    tmp_filter_list.append(tmp_dict)
                else:
                    for val in item['val']:
                        tmp_dict = dict()
                        tmp_dict['key'] = item['key']
                        tmp_dict['val'] = val
                        tmp_filter_list.append(tmp_dict)

            for item in tmp_filter_list:
                resp_form = self.insert(table='analysis.filter_default', data={**item, 'func_id': func_id})
                if not resp_form.res:
                    return resp_form

            aggregation_default = setting['aggregation_default']
            if len(aggregation_default) and 'type' in aggregation_default and 'val' in aggregation_default:
                resp_form = self.insert(table='analysis.aggregation_default', data={**aggregation_default,
                                                                                    'func_id': func_id})
                if not resp_form.res:
                    return resp_form

            script = analysis['script']
            # if script['db_id'] is not None:
            resp_form = self.insert(table='analysis.analysis_script', data={**script, 'func_id': func_id})
            if not resp_form.res:
                return resp_form

            return ResponseForm(res=True)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def update_analysis_info(self, analysis, func_id):
        try:
            setting = analysis['setting']

            df_ids = self.fetch_all(table='analysis.analysis_items',
                                    args={'select': 'id', 'where': f"func_id='{func_id}'"})
            id_list = df_ids['id'].tolist()

            for item in setting['items']:
                if isinstance(item['source_col'], list):
                    item['source_col'] = ','.join(item['source_col'])
                resp_form = self.insert(table='analysis.analysis_items', data={**item, 'func_id': func_id})
                if not resp_form.res:
                    return resp_form

            if len(id_list) > 1:
                id_list = ["'" + str(v) + "'" for v in id_list]
                _in = ','.join(id_list)
            elif len(id_list):
                _in = f"'{id_list[0]}'"
            else:
                _in = None

            if _in is not None:
                where_phrase = f"id in ({_in})"
                self.delete(table='analysis.analysis_items', where_phrase=where_phrase)

            df_ids = self.fetch_all(table='analysis.filter_default',
                                    args={'select': 'id', 'where': f"func_id='{func_id}'"})
            id_list = df_ids['id'].tolist()

            tmp_filter_list = list()
            for item in setting['filter_default']:
                if item['val'] is None or len(item['val']) == 0:
                    tmp_dict = dict()
                    tmp_dict['key'] = item['key']
                    tmp_dict['val'] = None
                    tmp_filter_list.append(tmp_dict)
                else:
                    for val in item['val']:
                        tmp_dict = dict()
                        tmp_dict['key'] = item['key']
                        tmp_dict['val'] = val
                        tmp_filter_list.append(tmp_dict)

            for item in tmp_filter_list:
                resp_form = self.insert(table='analysis.filter_default', data={**item, 'func_id': func_id})
                if not resp_form.res:
                    return resp_form

            if len(id_list) > 1:
                id_list = ["'" + str(v) + "'" for v in id_list]
                _in = ','.join(id_list)
            elif len(id_list):
                _in = f"'{id_list[0]}'"
            else:
                _in = None

            if _in is not None:
                where_phrase = f"id in ({_in})"
                self.delete(table='analysis.filter_default', where_phrase=where_phrase)

            df_ids = self.fetch_all(table='analysis.aggregation_default',
                                    args={'select': 'id', 'where': f"func_id='{func_id}'"})
            id_list = df_ids['id'].tolist()

            aggregation_default = setting['aggregation_default']
            if len(aggregation_default) and 'type' in aggregation_default and 'val' in aggregation_default:
                resp_form = self.insert(table='analysis.aggregation_default', data={**aggregation_default,
                                                                                    'func_id': func_id})
                if not resp_form.res:
                    return resp_form

            if len(id_list) > 1:
                id_list = ["'" + str(v) + "'" for v in id_list]
                _in = ','.join(id_list)
            elif len(id_list):
                _in = f"'{id_list[0]}'"
            else:
                _in = None

            if _in is not None:
                where_phrase = f"id in ({_in})"
                self.delete(table='analysis.aggregation_default', where_phrase=where_phrase)

            script = analysis['script']
            if script['file_name'] is None:
                resp_form = self.update(table='analysis.analysis_script',
                                        set={**script, 'script': None},
                                        where={'func_id': func_id})
            else:
                resp_form = self.update(table='analysis.analysis_script',
                                        set={**script},
                                        where={'func_id': func_id})
            if not resp_form.res:
                return resp_form

            return ResponseForm(res=True)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def insert_visual_info(self, visualization, func_id):
        try:
            for item in visualization['function_graph_type']:
                if 'id' in item:
                    item.pop('id')
                resp_form = self.insert(table='graph.function_graph_type', data={**item, 'func_id': func_id})
                if not resp_form.res:
                    return resp_form

            for item in visualization['items']:
                if 'id' in item:
                    item.pop('id')
                item['type'] = ','.join(item['type'])
                item['y_axis'] = ','.join(item['y_axis'])
                resp_form = self.insert(table='analysis.visualization_default', data={**item, 'func_id': func_id})
                if not resp_form.res:
                    return resp_form

            return ResponseForm(res=True)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def update_visual_info(self, visualization, func_id):
        try:
            update_item_list = list()
            add_item_list = list()
            id_list = list()
            for item in visualization['function_graph_type']:
                if item['id'] is None:
                    add_item_list.append(item)
                else:
                    id_list.append(item['id'])
                    update_item_list.append(item)

            for item in update_item_list:
                id = item.pop('id')
                resp_form = self.update(table='graph.function_graph_type',
                                        set={**item},
                                        where={'id': id, 'func_id': func_id})
                if not resp_form.res:
                    return resp_form

            f_graph_type_df = self.fetch_all(table='graph.function_graph_type',
                                             args={'select': 'id, name', 'where': f'func_id={func_id}'})
            not_included_df = f_graph_type_df[~f_graph_type_df['id'].isin(id_list)]
            for i in range(len(not_included_df)):
                self.delete(table='graph.function_graph_type', where_dict={'id': not_included_df['id'].values[i]})

            for item in add_item_list:
                item.pop('id')
                resp_form = self.insert(table='graph.function_graph_type', data={**item, 'func_id': func_id})
                if not resp_form.res:
                    return resp_form

            update_item_list = list()
            add_item_list = list()
            id_list = list()
            for item in visualization['items']:
                item['type'] = ','.join(item['type'])
                item['y_axis'] = ','.join(item['y_axis'])
                if item['id'] is None:
                    add_item_list.append(item)
                else:
                    id_list.append(item['id'])
                    update_item_list.append(item)

            for item in update_item_list:
                id = item.pop('id')
                resp_form = self.update(table='analysis.visualization_default',
                                        set={**item},
                                        where={'id': id, 'func_id': func_id})
                if not resp_form.res:
                    return resp_form

            f_vis_default_df = self.fetch_all(table='analysis.visualization_default',
                                              args={'select': 'id, title', 'where': f'func_id={func_id}'})
            not_included_df = f_vis_default_df[~f_vis_default_df['id'].isin(id_list)]
            for i in range(len(not_included_df)):
                self.delete(table='analysis.visualization_default', where_dict={'id': not_included_df['id'].values[i]})

            for item in add_item_list:
                item.pop('id')
                resp_form = self.insert(table='analysis.visualization_default', data={**item, 'func_id': func_id})
                if not resp_form.res:
                    return resp_form

            return ResponseForm(res=True)

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))
