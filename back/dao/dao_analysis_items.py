from dao.dao_base import DAOBaseClass


class DAOAnalysisItems(DAOBaseClass):
    TABLE_NAME = 'analysis.analysis_items'

    def __init__(self, func_id=None, df=None):
        super().__init__(table_name=DAOAnalysisItems.TABLE_NAME)
        if func_id is not None:
            self.df = self.fetch_all(args={'where': f"func_id='{func_id}'"})
        elif df is not None:
            self.df = df

    def __del__(self):
        super().__del__()
        print('__del__', __class__)

    def get_columns_comma_separated(self):
        columns = self.df['source_col'].unique().tolist()

        return ', '.join(columns)

    def get_column_list(self, group_analysis=None, total_analysis=None):
        select_df = self.df

        if group_analysis is not None:
            select_df = select_df[select_df['group_analysis'] == group_analysis]

        if total_analysis is not None:
            select_df = select_df[select_df['total_analysis'] == total_analysis]

        # select_df = self.df[(self.df['op_type'] == op_type) & (self.df['cell_formula'] == cell_form)]
        # select_df = self.df[['column_name', operation]].dropna(axis=0)
        # cell_list = select_df[operation].apply(lambda x: x.split('|')[0])

        columns = select_df['source_col'].dropna(axis=0).unique().tolist()

        return columns

    def sort_by_column_order(self, columns, group_name):
        df = self.df.sort_values(by='disp_order', ascending=True)
        column_list = df['source_col'].unique().tolist()

        disp_order = []
        for column in column_list:
            if column in columns:
                disp_order.append(column)

        if 'process' in columns:
            disp_order.insert(0, 'process')

        if 'device' in columns:
            disp_order.insert(0, 'device')

        if 'log_time' in columns:
            disp_order.insert(0, 'log_time')

        if group_name not in disp_order and group_name in columns:
            disp_order.insert(0, group_name)

        if 'index' in columns:
            disp_order.insert(0, 'index')

        return disp_order

    def get_analysis_list_by_order(self):
        self.df.sort_values(by='disp_order', ascending=True, inplace=True)
        return self.df.to_dict(orient='records')
