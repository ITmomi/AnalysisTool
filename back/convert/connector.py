import datetime

import numpy as np
import psycopg2 as pg2
import psycopg2.extras
import pandas as pd
import convert.const as val


from convert.exception.log_convert_exception import ParameterError, DatabaseConnectError
from convert.pg_datasource import Connect
from convert.util import insert_df


class Connector:

    schema = 'cnvbase'
    rule_table = f'{schema}.convert_rule'
    rule_item_table = f'{schema}.convert_rule_item'
    log_define_table = f'{schema}.log_define_master'
    filter_table = f'{schema}.convert_filter'
    filter_item_table = f'{schema}.convert_filter_item'
    error_log_table = f'{schema}.convert_error'

    def __init__(self, config):
        self.config = config

    def get_log_list(self, log_name=None, df=False):
        with Connect(self.config, column=True) as conn:
            extra = "" if log_name is None else f"where master.log_name = '{log_name}'"
            sql = f"select *, \
                (select count(id) from {self.rule_table} rule where rule.log_id = master.id and rule.commit = true) as rule, \
                (select count(id) from {self.error_log_table} und where und.log_id = master.id) as error \
                from {self.log_define_table} master {extra} order by master.log_name"
            if df:
                ret = pd.read_sql(sql, conn.connect)
                if ret is None:
                    return pd.DataFrame()
                return ret
            else:
                conn.cursor.execute(sql)
                ret = conn.cursor.fetchall()
                if ret is not None:
                    return [dict(_) for _ in ret]
                return list()
        raise DatabaseConnectError('get_log_list failed')

    def get_log_by_id(self, log_id):
        return self._get_log_by(f"id = {log_id}")

    def get_log_by_name(self, log_name):
        return self._get_log_by(f"log_name = '{log_name}'")

    def _get_log_by(self, sql):
        with Connect(self.config, column=True) as c:
            c.cursor.execute(f"select * from {self.log_define_table} where {sql}")
            ret = c.cursor.fetchone()
            if ret is None:
                return None
            return dict(ret)
        raise DatabaseConnectError(f'get_log_by_id({log_id}) failed')

    """
    Insert new log name into table.
    """
    def insert_log(self, log_name):
        if self.exist_log_name(log_name):
            raise ParameterError(f"log already exist({log_name})")
        with Connect(self.config, column=True) as conn:
            i = self.get_next_id_of(self.log_define_table, conn.cursor)
            conn.cursor.execute(f"insert into {self.log_define_table} (id, log_name) values ({i}, '{log_name}') returning *")
            ret = conn.cursor.fetchone()
            return dict(ret)
        return None

    """
    Update a log record.
    """
    def update_log(self, log_id, log_name, input_type, table_name, fab, tag, ignore, retention):
        with Connect(self.config, column=True) as c:
            c.cursor.execute(f"update {self.log_define_table} set \
                log_name = '{log_name}', input_type = '{input_type}', table_name = '{table_name}', fab = '{fab}', \
                tag = '{tag}', ignore = '{ignore}', retention = {retention} where id = {log_id} returning *")
            ret = c.cursor.fetchone()
            return dict(ret)
        raise DatabaseConnectError(f'update_log failed')

    """
    Delete a log definition.
    """
    def delete_log(self, log_id):
        with Connect(self.config, column=True) as c:
            c.cursor.execute(f"delete from {self.log_define_table} where id = {log_id}")
            return
        raise DatabaseConnectError(f'delete_log failed')

    """
    Return a list of rule name and its column count.
    """
    def get_rule_list(self, log_id=None, rule_name=None, committed=True, df=False):
        with Connect(self.config, column=True) as conn:
            extra0 = "commit = true" if committed else "1 = 1"
            extra1 = "" if log_id is None else f"and log_id = '{log_id}'"
            extra2 = "" if rule_name is None else f"and rule_name = '{rule_name}'"
            sql = f"select r.*, \
                (select count(id) from {self.rule_item_table} where rule_id = r.id and type = 'header') as col, \
                def.table_name as table_name, \
                def.input_type as input_type \
                from {self.rule_table} r left join {self.log_define_table} def on def.id = r.log_id \
                where {extra0} {extra1} {extra2}"
            if df:
                ret = pd.read_sql(sql, conn.connect)
                if ret is None:
                    return pd.DataFrame()
                return ret
            else:
                conn.cursor.execute(sql)
                ret = conn.cursor.fetchall()
                if ret is not None and len(ret) > 0:
                    return [dict(_) for _ in ret]
                return list()
        raise DatabaseConnectError(f'get_rule_list failed')

    """
    Get a rule entity by rule_id.
    """
    def get_rule_by_id(self, rule_id, extra=False):
        with Connect(self.config, column=True) as c:
            if extra:
                sql = f"select \
                        rule.id as id, \
                        rule.log_id as log_id, \
                        rule.rule_name as rule_name, \
                        rule.created as created, \
                        rule.modified as modified, \
                        rule.commit as commit, \
                        def.input_type as input_type, \
                        def.log_name as log_name, \
                        def.table_name as table_name, \
                        (select count(id) from {self.rule_item_table} where rule_id = rule.id and type = 'header') as col \
                        from cnvbase.convert_rule rule \
                        left join {self.log_define_table} def on def.id = rule.log_id where rule.id = {rule_id}"
            else:
                sql = f"select * from {self.schema}.convert_rule where id = {rule_id}"
            c.cursor.execute(sql)
            ret = c.cursor.fetchone()
            if ret is not None:
                return dict(ret)
            return None
        raise DatabaseConnectError("get_rule_by_id db connection failed")

    """
    Insert a rule.
    """
    def insert_rule(self, log_id, rule_name):
        with Connect(self.config, column=True) as c:
            i = self.get_next_id_of(self.rule_table, c.cursor)
            c.cursor.execute(f"insert into {self.schema}.convert_rule (id, log_id, rule_name) \
                values ({i}, {log_id}, '{rule_name}') returning *")
            ret = c.cursor.fetchone()
            if ret is not None:
                return dict(ret)
            return None
        raise DatabaseConnectError("insert_rule db connection failed")

    """
    Update a rule
    """
    def update_rule(self, rule_id, rule_name, commit):
        with Connect(self.config, column=True) as c:
            c.cursor.execute(f"update {self.schema}.convert_rule set \
                rule_name = '{rule_name}', commit = {commit} where id = {rule_id} returning *")
            ret = c.cursor.fetchone()
            if ret is not None:
                return dict(ret)
            return None
        raise DatabaseConnectError("update_rule db connection failed")

    """
    Delete a rule by rule-id.
    """
    def delete_rule(self, rule_id):
        with Connect(self.config) as c:
            c.cursor.execute(f"delete from {self.rule_table} where id = {rule_id}")
            return
        raise DatabaseConnectError("delete_rule db connection failed")

    """
    Get rule items for the specified rule_id
    """
    def get_rule_items_by_id(self, rule_id, df=False):
        with Connect(self.config, column=True) as c:
            sql = f"select * from {self.rule_item_table} where rule_id = {rule_id}"
            if df:
                ret = pd.read_sql(sql, c.connect)
                if ret is None:
                    return pd.DataFrame()
                # convert lower
                ret['output_column'] = ret['output_column'].str.lower()
                # Column type casting.
                ret['row_index'] = ret['row_index'].fillna(0).astype(int)
                ret['col_index'] = ret['col_index'].fillna(0).astype(int)
                ret['coef'] = ret['coef'].fillna(0).astype(int)
                return ret
            else:
                c.cursor.execute(sql)
                ret = c.cursor.fetchall()
                if ret is None:
                    return list()
                return [dict(_) for _ in ret]
        raise DatabaseConnectError(f'get_rule_items_by_id failed')

    """
    Get a rule item by item-id.
    """
    def get_rule_item(self, item_id):
        with Connect(self.config, column=True) as c:
            sql = f"select * from {self.rule_item_table} where id = {item_id}"
            c.cursor.execute(sql)
            ret = c.cursor.fetchone()
            if ret is not None:
                return dict(ret)
            return None
        raise DatabaseConnectError(f'get_rule_item failed')

    """
    Get rule item list.
    """
    def get_rule_item_list(self, rule_id, column=True, df=False):
        sql = f"select * from {self.rule_item_table} where rule_id = {rule_id}"
        with Connect(self.config, column=column) as conn:
            if df:
                ret = pd.read_sql(sql, conn.connect)
                if ret is not None:
                    return ret
                return pd.DataFrame()
            else:
                conn.cursor.execute(sql)
                ret = conn.cursor.fetchall()
                if ret is None:
                    return list()
                return [dict(_) for _ in ret]

    """
    Insert a rule item.
    """
    def insert_rule_item(self, rule_id, **args):
        fields = ['rule_id']
        values = [rule_id]
        for key in args:
            if args[key] is None:
                continue
            fields.append(key)
            # if type(args[key]) == str:
            #     values.append(f"'{args[key]}'")
            # else:
            #     values.append(f'{args[key]}')
            values.append(args[key])
        with Connect(self.config, column=True) as c:
            i = self.get_next_id_of(self.rule_item_table, c.cursor)
            values_str = ','.join(['%s' for _ in values])
            sql = f"insert into {self.rule_item_table} (id, {','.join(fields)}) values ({i}, {values_str}) returning *"
            c.cursor.execute(sql, tuple(values))
            ret = c.cursor.fetchone()
            if ret is not None:
                return dict(ret)
        return None

    """
    Update a rule item.
    """
    def update_rule_item(self, id, rule_id, type, row_index, col_index, name, output_column, data_type, coef, def_val,
                         def_type, unit, prefix, regex, re_group, skip):
        with Connect(self.config, column=True) as c:
            sql = f"update {self.rule_item_table} set \
                rule_id = {rule_id}, \
                type = '{type}', \
                row_index = {row_index}, \
                col_index = {col_index}, \
                name = '{name}', \
                output_column = '{output_column}', \
                data_type = '{data_type}', \
                coef = {coef}, \
                def_val = '{def_val}', \
                def_type = '{def_type}', \
                unit = '{unit}',\
                prefix = '{prefix}', \
                regex = '{regex}', \
                re_group = {re_group}, \
                skip = {skip} where id = {id} returning *"
            c.cursor.execute(sql)
            ret = c.cursor.fetchone()
            if ret is None:
                return None
            return dict(ret)
        raise DatabaseConnectError('update_rule_item failed')

    """
    Delete a rule item.
    """
    def delete_rule_item(self, item_id):
        with Connect(self.config) as c:
            c.cursor.execute(f"delete from {self.rule_item_table} where id = {item_id}")
            return
        raise DatabaseConnectError("delete_rule_item db connection failed")

    def find_rule_id(self, log_name, rule_name):
        with Connect(self.config) as conn:
            conn.cursor.execute(f"select id from cnvbase.convert_rule \
                where log_name = '{log_name}' and rule_name = '{rule_name}'")
            ret = conn.cursor.fetchone()
            if ret is not None:
                return ret[0]
        return None

    """
    Get a filter by filter-id.
    """
    def get_filter(self, filter_id):
        with Connect(self.config, column=True) as c:
            c.cursor.execute(f"select * from {self.filter_table} where id = {filter_id}")
            ret = c.cursor.fetchone()
            if ret is None:
                return None
            return dict(ret)
        raise DatabaseConnectError("get_filter db connection failed")

    """
    Get filter list by log_id
    """
    def get_filter_list(self, log_id=None, committed=True, df=False):
        with Connect(self.config, column=True) as c:
            extra1 = f"and log_id = {log_id}" if log_id is not None else ""
            extra2 = "and commit = true" if committed else ""
            sql = f"select * from {self.filter_table} where 1 = 1 {extra1} {extra2}"
            if df:
                ret = pd.read_sql(sql, c.connect)
                if ret is None:
                    return pd.DataFrame()
                return ret
            c.cursor.execute(sql)
            ret = c.cursor.fetchall()
            if ret is None:
                return list()
            return [dict(_) for _ in ret]
        raise DatabaseConnectError("get_filter_list db connection failed")

    """
    Insert a filter.
    """
    def insert_filter(self, log_id):
        with Connect(self.config, column=True) as c:
            i = self.get_next_id_of(self.filter_table, c.cursor)
            c.cursor.execute(f"insert into {self.filter_table} (id, log_id) \
                values ({i}, {log_id}) returning *")
            ret = c.cursor.fetchone()
            if ret is None:
                return None
            return dict(ret)

    """
    Update a filter
    """
    def update_filter(self, filter_id, commit):
        with Connect(self.config, column=True) as c:
            c.cursor.execute(f"update {self.filter_table} set commit = {commit} where id = {filter_id} returning *")
            ret = c.cursor.fetchone()
            if ret is None:
                return None
            return dict(ret)
        raise DatabaseConnectError("update_filter db connection failed")

    """
    Delete a filter
    """
    def delete_filter(self, filter_id):
        with Connect(self.config) as c:
            c.cursor.execute(f"delete from {self.filter_table} where id = {filter_id}")
            return
        raise DatabaseConnectError("delete_filter db connection failed")

    """
    Insert a filter item. 
    """
    def insert_filter_item(self, filter_id, name, type, condition):
        with Connect(self.config, column=True) as c:
            i = self.get_next_id_of(self.filter_item_table, c.cursor)
            c.cursor.execute(f"insert into {self.filter_item_table} (id, name, filter_id, type, condition ) values \
                ({i}, '{name}', {filter_id}, '{type}', %s) returning *", tuple([condition]))
            ret = c.cursor.fetchone()
            if ret is None:
                return None
            return dict(ret)
        raise DatabaseConnectError("insert_filter_item db connection failed")

    """
    Get filter items by filter-id
    """
    def get_filter_item_list(self, filter_id, df=False):
        with Connect(self.config, column=True) as c:
            sql = f"select * from {self.filter_item_table} where filter_id = {filter_id}"
            if df:
                ret = pd.read_sql(sql, c.connect)
                if ret is None:
                    return pd.DataFrame()
                return ret
            else:
                c.cursor.execute(sql)
                ret = c.cursor.fetchall()
                if ret is None:
                    return list()
                return [dict(_) for _ in ret]
        raise DatabaseConnectError("get_filter_item_list db connection failed")

    """
    Delete a filter item by item-id.
    """
    def delete_filter_item(self, item_id):
        with Connect(self.config) as c:
            c.cursor.execute(f"delete from {self.filter_item_table} where id = {item_id}")
            return
        raise DatabaseConnectError("delete_filter_item db connection failed")

    """
    Test if the specified table exists
    """
    def exist_log_name(self, log_name):

        with Connect(self.config) as conn:
            conn.cursor.execute(f"select count(id) from {self.log_define_table} where log_name = '{log_name}'")
            ret = conn.cursor.fetchone()
            if ret is not None and ret[0] > 0:
                return True
        return False

    """
    Insert a converting error.
    """
    def insert_error(self, log_id, file, row, msg, equipment, content):
        with Connect(self.config, column=True) as c:
            i = self.get_next_id_of(self.error_log_table, c.cursor)
            c.cursor.execute(f"insert into {self.error_log_table} (id, log_id, file, row, msg, equipment, content) \
                values ({i}, {log_id}, '{file}', {row}, '{msg}', '{equipment}', '{content}') returning *")
            ret = c.cursor.fetchone()
            if ret is not None:
                return dict(ret)
            return None
        raise DatabaseConnectError("insert_error db connection failed")

    """
    Get convert error list by log-id.
    """
    def get_error(self, log_id):
        with Connect(self.config, column=True) as c:
            c.cursor.execute(f"select * from {self.error_log_table} where log_id = {log_id}")
            ret = c.cursor.fetchall()
            if ret is not None:
                return [dict(r) for r in ret]
            return None
        raise DatabaseConnectError("get_error db connection failed")

    """
    Clear convert log for the specified log-id
    """
    def clear_error(self, log_id):
        with Connect(self.config, column=True) as c:
            c.cursor.execute(f"delete from {self.error_log_table} where log_id = {log_id}")
            return
        raise DatabaseConnectError("clear_error db connection failed")

    """
    Delete errors that are older than the specific days.
    """
    def delete_error(self, log_id, days=30):
        with Connect(self.config) as c:
            date_to = datetime.datetime.now() - datetime.timedelta(days=days)
            c.cursor.execute(f"delete from {self.error_log_table} where log_id = {log_id} and created < '{date_to}'")
            return
        raise DatabaseConnectError("delete_error db connection failed")

    """
    """
    def get_log_define_df(self):
        with Connect(self.config) as c:
            ret = pd.read_sql(f"select * from {self.log_define_table}", c.connect)
            return ret
        raise DatabaseConnectError("get_log_define_df failed")

    def get_convert_rule_df(self):
        with Connect(self.config) as c:
            ret = pd.read_sql(f"select * from {self.rule_table}", c.connect)
            return ret
        raise DatabaseConnectError("get_convert_rule_df failed")

    def get_convert_item_df(self):
        with Connect(self.config) as c:
            ret = pd.read_sql(f"select * from {self.rule_item_table}", c.connect)
            return ret
        raise DatabaseConnectError("get_convert_item_df failed")

    def get_filter_rule_df(self):
        with Connect(self.config) as c:
            ret = pd.read_sql(f"select * from {self.filter_table}", c.connect)
            return ret
        raise DatabaseConnectError("get_filter_rule_df failed")

    def get_filter_item_df(self):
        with Connect(self.config) as c:
            ret = pd.read_sql(f"select * from {self.filter_item_table}", c.connect)
            return ret
        raise DatabaseConnectError("get_filter_item_df failed")

    def get_convert_error_df(self):
        with Connect(self.config) as c:
            ret = pd.read_sql(f"select * from {self.error_log_table}", c.connect)
            return ret
        raise DatabaseConnectError("get_convert_error_df failed")

    def restore_log_define(self, df):
        df['input_type'] = df['input_type'].replace({np.nan: ''}).astype(str)
        df['table_name'] = df['table_name'].replace({np.nan: ''}).astype(str)
        df['fab'] = df['fab'].replace({np.nan: ''}).astype(str)
        df['tag'] = df['tag'].replace({np.nan: ''}).astype(str)
        df['ignore'] = df['ignore'].replace({np.nan: ''}).astype(str)

        with Connect(self.config) as c:
            c.cursor.execute(f"delete from {self.log_define_table}")
            c.cursor.execute(f"truncate table {self.log_define_table} restart identity cascade")

        insert_df(self.config, self.schema, 'log_define_master', df)

    def restore_convert_rule(self, df):
        df['log_id'] = df['log_id'].astype('int64')
        df['rule_name'] = df['rule_name'].dropna().astype(str)

        with Connect(self.config) as c:
            c.cursor.execute(f"delete from {self.rule_table}")
            c.cursor.execute(f"truncate table {self.rule_table} restart identity cascade")

        insert_df(self.config, self.schema, 'convert_rule', df)

    def restore_convert_item(self, df):
        df['rule_id'] = df['rule_id'].astype('int64')
        df = df.replace({np.nan: ''})
        df['row_index'] = df['row_index'].replace({'': 0}).astype('int64')
        df['col_index'] = df['col_index'].replace({'': 0}).astype('int64')
        df['coef'] = df['coef'].replace({'': 0}).astype('int64')
        df['def_val'] = df['def_val'].apply(lambda x: x if x is None else x.replace("'", "''"))

        with Connect(self.config) as c:
            c.cursor.execute(f"delete from {self.rule_item_table}")
            c.cursor.execute(f"truncate table {self.rule_item_table} restart identity cascade")

        insert_df(self.config, self.schema, 'convert_rule_item', df)

    def restore_filter(self, df):
        df['log_id'] = df['log_id'].astype('int64')
        with Connect(self.config) as c:
            c.cursor.execute(f"delete from {self.filter_table}")
            c.cursor.execute(f"truncate table {self.filter_table} restart identity cascade")

        insert_df(self.config, self.schema, 'convert_filter', df)

    def restore_filter_item(self, df):
        df['filter_id'] = df['filter_id'].astype('int64')
        df = df.replace({np.nan: ''})
        df['condition'] = df['condition'].apply(lambda x: x if x is None else x.replace("'", "''"))

        with Connect(self.config) as c:
            c.cursor.execute(f"delete from {self.filter_item_table}")
            c.cursor.execute(f"truncate table {self.filter_item_table} restart identity cascade")

        insert_df(self.config, self.schema, 'convert_filter_item', df)

    def restore_convert_error(self, df):
        df['log_id'] = df['log_id'].astype('int64')
        df = df.replace({np.nan: ''})
        df['row'] = df['row'].replace({'': 0}).astype('int64')

        with Connect(self.config) as c:
            c.cursor.execute(f"delete from {self.error_log_table}")
            c.cursor.execute(f"truncate table {self.error_log_table} restart identity cascade")

        insert_df(self.config, self.schema, 'convert_error', df)

    def get_next_id_of(self, table, cursor):
        cursor.execute(f"select max(id)+1 as next from {table}")
        ret = cursor.fetchone()
        if ret is None:
            return 0
        ret = dict(ret)
        if 'next' not in ret or ret['next'] is None:
            return 0
        return ret['next']
