from dao.dao_base import DAOBaseClass
from common.utils.response import ResponseForm


class DAOHistory(DAOBaseClass):
    TABLE_NAME = 'history.history'

    def __init__(self):
        super().__init__(table_name=DAOHistory.TABLE_NAME)

    def __del__(self):
        super().__del__()
        print('__del__', __class__)

    def insert_history(self, **args):
        return self.insert(data=args, rtn_id=True)

    def insert_history_from_local(self, **args):
        return self.insert(data=args, table='history.history_from_local')

    def insert_history_from_remote(self, **args):
        return self.insert(data=args, table='history.history_from_remote')

    def insert_history_from_sql(self, **args):
        return self.insert(data=args, table='history.history_from_sql')

    def insert_history_from_multi(self, **args):
        return self.insert(data=args, table='history.history_from_multi')

    def insert_filter_history(self, **args):
        return self.insert(data=args, table='history.filter_history')

    def insert_aggregation_history(self, **args):
        return self.insert(data=args, table='history.aggregation_history')

    def insert_visualization_history(self, **args):
        return self.insert(data=args, table='history.visualization_history')

    def delete_history_id(self, history_id):
        self.delete(table='history.history', where_dict={'id': history_id})

    def get_local_info(self, history_id):
        ret_dict = self.fetch_one(table='history.history_from_local', args={'where': f"history_id='{history_id}'"})
        if ret_dict is None:
            return ResponseForm(res=False, msg='No matching history.')

        return ResponseForm(res=True, data=dict(ret_dict))

    def get_remote_info(self, history_id):
        ret_dict = self.fetch_one(table='history.history_from_remote', args={'where': f"history_id='{history_id}'"})
        if ret_dict is None:
            return ResponseForm(res=False, msg='No matching history.')

        return ResponseForm(res=True, data=dict(ret_dict))

    def get_sql_info(self, history_id):
        ret_dict = self.fetch_one(table='history.history_from_sql', args={'where': f"history_id='{history_id}'"})
        if ret_dict is None:
            return ResponseForm(res=False, msg='No matching history.')

        return ResponseForm(res=True, data=dict(ret_dict))

    def get_multi_info(self, history_id):
        ret_df = self.fetch_all(table='history.history_from_multi', args={'where': f"history_id='{history_id}'"})
        if len(ret_df) == 0:
            return ResponseForm(res=False, msg='No matching history.')

        return ResponseForm(res=True, data=ret_df)

    def get_rid(self, history_id):
        ret_dict = self.fetch_one(args={'select': 'source', 'where': f"id='{history_id}'"})
        if ret_dict is None:
            return ResponseForm(res=False, msg='No matching history.')

        log_from = ret_dict['source']

        ret_dict = None
        if log_from == 'local':
            ret_dict = self.fetch_one(table='history.history_from_local',
                                      args={'select': 'rid', 'where': f"history_id='{history_id}'"})
        elif log_from == 'remote':
            ret_dict = self.fetch_one(table='history.history_from_remote',
                                      args={'select': 'rid', 'where': f"history_id='{history_id}'"})
        elif log_from == 'sql':
            ret_dict = self.fetch_one(table='history.history_from_sql',
                                      args={'select': 'rid', 'where': f"history_id='{history_id}'"})

        if ret_dict is None:
            return ResponseForm(res=False, msg='Cannot find Request Id.')

        return ResponseForm(res=True, data=ret_dict['rid'])

    def get_period(self, history_id):
        ret_dict = self.fetch_one(args={'select': 'period_start, period_end', 'where': f"id='{history_id}'"})
        if ret_dict is None:
            return ResponseForm(res=False, msg='No matching history.')

        return ResponseForm(res=True, data={'start': str(ret_dict['period_start']), 'end': str(ret_dict['period_end'])})

    def get_filter_info(self, history_id):
        filter_df = self.fetch_all(table='history.filter_history', args={'where': f"history_id='{history_id}'"})
        if len(filter_df) == 0:
            return ResponseForm(res=False, msg='No matching filter info')

        data = dict()
        for key in filter_df['key'].unique().tolist():
            val_list = filter_df[filter_df['key'] == key]['val'].tolist()
            val_list = [val for val in val_list if val != '' and val != 'null' and val is not None]
            if len(val_list):
                data[key] = val_list

        if len(data):
            return ResponseForm(res=True, data=data)
        else:
            return ResponseForm(res=False)

    def get_aggregation_info(self, history_id):
        ret_dict = self.fetch_one(table='history.aggregation_history',
                                  args={'select': 'type, val', 'where': f"history_id='{history_id}'"})
        if ret_dict is None:
            return ResponseForm(res=False, msg='No matching Aggregation info')

        return ResponseForm(res=True, data={'type': ret_dict['type'], 'val': ret_dict['val']})

    def get_visualization_info(self, func_id, history_id):
        func_graph_type_list = list()
        items = list()

        df = self.fetch_all(table='graph.function_graph_type', args={'select': 'id, name, script, type',
                                                                     'where': f"func_id={func_id}"})
        for i in range(len(df)):
            graph_type = dict()
            graph_type['name'] = df['name'].values[i]
            graph_type['script'] = df['script'].values[i]
            graph_type['type'] = df['type'].values[i]

            func_graph_type_list.append(graph_type)

        df_visualization = self.fetch_all(table='history.visualization_history',
                                          args={'where': f"history_id='{history_id}'"})

        for i in range(len(df_visualization)):
            item = dict()
            item['title'] = df_visualization['title'].values[i]
            item['type'] = [str(_) for _ in df_visualization['type'].values[i].split(sep=',')]
            item['x_axis'] = df_visualization['x_axis'].values[i]
            item['y_axis'] = [str(_) for _ in df_visualization['y_axis'].values[i].split(sep=',')]
            item['z_axis'] = df_visualization['z_axis'].values[i]
            item['x_range_min'] = df_visualization['x_range_min'].values[i]
            item['x_range_max'] = df_visualization['x_range_max'].values[i]
            item['y_range_min'] = df_visualization['y_range_min'].values[i]
            item['y_range_max'] = df_visualization['y_range_max'].values[i]
            item['z_range_min'] = df_visualization['z_range_min'].values[i]
            item['z_range_max'] = df_visualization['z_range_max'].values[i]

            items.append(item)

        df_graph_type = self.fetch_all(table='public.graph_type')
        graph_list = list()
        for graph_type in df_graph_type['type'].tolist():
            item = dict()
            item['name'] = graph_type
            item['type'] = 'system'
            graph_list.append(item)

        for graph_type in func_graph_type_list:
            if graph_type['type'] == 'user':
                graph_list.append({'name': graph_type['name'], 'type': graph_type['type']})

        data = dict()
        data['function_graph_type'] = func_graph_type_list
        data['graph_list'] = graph_list
        data['items'] = items

        return ResponseForm(res=True, data=data)
