from abc import *
from io import StringIO
import psycopg2 as pg2
from psycopg2 import extras
import pandas as pd
import configparser
from copy import deepcopy
import datetime
import traceback
import logging

from common.utils.response import ResponseForm
from common.utils import preprocessing
from config.app_config import *
from dao.utils import get_db_config

logger = logging.getLogger(LOG)


class DAOBaseClass(metaclass=ABCMeta):
    def __init__(self, **kwargs):
        self.df = None

        if 'table_name' in kwargs:
            self.table_name = kwargs['table_name']
        else:
            self.table_name = None

        self.config = get_db_config()

        if 'dbname' in kwargs:
            self.config['dbname'] = kwargs['dbname']
        if 'user' in kwargs:
            self.config['user'] = kwargs['user']
        if 'host' in kwargs:
            self.config['host'] = kwargs['host']
        if 'password' in kwargs:
            self.config['password'] = kwargs['password']
        if 'port' in kwargs:
            self.config['port'] = kwargs['port']

        self.connect = pg2.connect(**self.config)
        if self.connect is not None:
            self.cursor = self.connect.cursor()
            self.dict_cursor = self.connect.cursor(cursor_factory=pg2.extras.DictCursor)
        else:
            raise Exception(f'DB Connect Fail.')

    def __del__(self):
        del self.table_name
        del self.config
        del self.df
        self.cursor.close()
        self.dict_cursor.close()
        self.connect.close()
        print('__del__', __class__)

    def execute(self, query, args={}):
        # with pg2.connect(**self.config, connect_timeout=2) as conn:
        #     with conn.cursor() as cur:
        #         cur.execute(query, args)
        #         row = cur.fetchall()
        self.cursor.execute(query, args)
        row = self.cursor.fetchall()

        return row

    # def execute_values(self, query, argslist):
    #     with pg2.connect(**self.config) as conn:
    #         with conn.cursor() as cur:
    #             extras.execute_values(cur, query, argslist)

    # def execute_by_dict(self, query):
    #     with pg2.connect(**self.config) as conn:
    #         with conn.cursor(cursor_factory=pg2.extras.DictCursor) as cur:
    #             cur.execute(query)
    #             row = cur.fetchall()
    #
    #     dict_result = []
    #
    #     for row in row:
    #         dict_result.append(dict(row))
    #
    #     return dict_result

    def read_sql(self, query):
        # with pg2.connect(**self.config) as conn:
        #     return pd.read_sql(query, conn)
        return pd.read_sql(query, self.connect)

    def fetch_one(self, table=None, args={}):
        table_name = table
        if table_name is None:
            table_name = self.table_name

        if 'select' in args:
            if 'where' in args:
                query = 'select %s from %s where %s' % (args['select'], table_name, args['where'])
            else:
                query = 'select %s from %s' % (args['select'], table_name)
        else:
            if 'where' in args:
                query = 'select * from %s where %s' % (table_name, args['where'])
            else:
                query = 'select * from %s' % table_name

        # with pg2.connect(**self.config) as conn:
        #     with conn.cursor(cursor_factory=pg2.extras.DictCursor) as cur:
        #         cur.execute(query)
        #         row = cur.fetchone()

        self.dict_cursor.execute(query)
        row = self.dict_cursor.fetchone()

        return row

    def fetch_all(self, table=None, args={}):
        table_name = table
        if table_name is None:
            table_name = self.table_name

        if 'select' in args:
            if 'where' in args:
                query = 'select %s from %s where %s' % (args['select'], table_name, args['where'])
            else:
                query = 'select %s from %s' % (args['select'], table_name)
        else:
            if 'where' in args:
                query = 'select * from %s where %s' % (table_name, args['where'])
            else:
                query = 'select * from %s' % table_name

        # with pg2.connect(**self.config) as conn:
        #     return pd.read_sql(query, conn)
        return pd.read_sql(query, self.connect)

    # def update_all(self, db_table, update_data, where_data):
    #     """
    #     データをUpdateする
    #     :param db_table:
    #     :param update_data:
    #     :param where_data:
    #     :return:
    #     """
    #     # values = []
    #     # key_str = ''
    #     # is_first_elem = True
    #
    #     update_key = update_data[0]
    #     update_value = update_data[1]
    #     where_key = where_data[0]
    #     where_value = where_data[1]
    #
    #     sql_str = "UPDATE {} SET {} = %s WHERE {} = %s;".format(db_table, update_key, where_key)
    #
    #     with pg2.connect(**self.config) as conn:
    #         with conn.cursor()as cur:
    #             cur.execute(sql_str, (update_value, where_value))

    # def insert_from_df(self, table, df):
    #     """
    #     指定されたテーブルにデータフレームをInsertする
    #     :param table_name: テーブル名
    #     :param insert_df: insertするデータフレーム
    #     :return:
    #     """
    #     for _, elem in df.iterrows():
    #         values = []
    #         key_str = ''
    #         is_first_elem = True
    #         elem = elem.dropna()
    #         for key, value in elem.items():
    #             values.append(value)
    #             if not is_first_elem:
    #                 key_str += ','
    #             is_first_elem = False
    #             key_str += key
    #
    #         sql_str = "INSERT INTO " + table + " (" + key_str + ") VALUES %s"
    #         value_tuple = tuple(values)
    #         value_list = list()
    #         value_list.append(value_tuple)
    #         with pg2.connect(**self.config) as conn:
    #             with conn.cursor()as cur:
    #                 try:
    #                     extras.execute_values(cur, sql_str, value_list)
    #                 except Exception as errmsg:
    #                     print(errmsg)

    # def insert_from_stringio(self, df):
    #     # save dataframe to an in memory buffer
    #     buffer = StringIO()
    #
    #     if '' in df.columns:
    #         del df['']
    #
    #     df['created_time'] = pd.Timestamp.now()
    #
    #     df.to_csv(buffer, index=False, header=False)
    #     buffer.seek(0)
    #
    #     with pg2.connect(**self.config) as conn:
    #         with conn.cursor() as cur:
    #             try:
    #                 cur.copy_from(buffer, self.table_name, sep=",", columns=df.columns, null=NA_VALUE)
    #                 conn.commit()
    #             except (Exception, pg2.DatabaseError) as error:
    #                 print("Error: %s" % error)
    #                 conn.rollback()
    #
    #     print("copy_from_stringio() done")

    # def get_columns(self):
    #     with pg2.connect(**self.config) as conn:
    #         with conn.cursor() as cur:
    #             try:
    #                 cur.execute(f"Select * FROM {self.table_name}")
    #                 columns = [desc[0] for desc in cur.description]
    #
    #                 return columns
    #             except Exception as e:
    #                 logger.error(str(e))
    #                 logger.error(traceback.format_exc())
    #                 return []

    def connection_check(self):
        try:
            query = 'select version()'
            # row = self.execute(query)
            with pg2.connect(**self.config, connect_timeout=2) as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    row = cur.fetchall()

            data = row[0][0]
            return ResponseForm(res=True, data=data)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            msg = str(e) if len(str(e)) > 0 else 'Cannot Connect Dababase. Check username or dbname or password.'
            return ResponseForm(res=False, msg=msg, status=400)

    def update(self, table=None, set=None, where=None):
        table_name = table
        if table_name is None:
            table_name = self.table_name

        if set is not None:
            value_list = list()
            query = 'update {0} set '.format(table_name)
            for key, val in set.items():
                # if isinstance(val, (int, float)):
                #     query = query + f"{key}={val}, "
                # elif val is None:
                #     query = query + f"{key}=null, "
                # else:
                #     query = query + f"{key}='{val}', "
                if val is None:
                    query = query + f"{key}=null, "
                else:
                    query = query + f"{key}=%s, "
                    value_list.append(val)

            query = query[:-2]

            if where is not None:
                query = query + ' where '
                for key, val in where.items():
                    query = query + "{0}='{1}' and ".format(key, val)
                query = query[:-5]

            query = query + ' RETURNING *'

            try:
                # with pg2.connect(**self.config) as conn:
                #     with conn.cursor()as cur:
                #         cur.execute(query, tuple(value_list))
                #         ret = cur.fetchall()
                #         if len(ret) == 0:
                #             return ResponseForm(res=False, msg='There is nothing to Update.')

                self.cursor.execute(query, tuple(value_list))
                ret = self.cursor.fetchall()
                if len(ret) == 0:
                    return ResponseForm(res=False, msg='There is nothing to Update.')

                self.connect.commit()
                return ResponseForm(res=True)
            except Exception as e:
                logger.error(str(e))
                logger.error(traceback.format_exc())
                return ResponseForm(res=False, msg=str(e))
        else:
            return ResponseForm(res=False, msg='Nothing to Update.')

    def insert(self, data={}, rtn_id=False, table=None):
        table_name = table
        if table_name is None:
            table_name = self.table_name

        key_str = ','.join(data.keys())
        # value_str = ','.join([f"{_}" if isinstance(_, (int, float)) else f"'{_}'" for _ in data.values()])
        value_str = ','.join(['%s' for _ in data.values()])

        query = f'insert into {table_name}({key_str}) values({value_str})'

        if rtn_id:
            query = query + ' RETURNING id'

        try:
            # with pg2.connect(**self.config) as conn:
            #     with conn.cursor()as cur:
            #         cur.execute(query, tuple(data.values()))
            #         if rtn_id:
            #             _id = cur.fetchone()[0]
            #             return ResponseForm(res=True, data=_id)
            #         else:
            #             return ResponseForm(res=True)

            self.cursor.execute(query, tuple(data.values()))
            if rtn_id:
                _id = self.cursor.fetchone()[0]
                self.connect.commit()
                return ResponseForm(res=True, data=_id)
            else:
                self.connect.commit()
                return ResponseForm(res=True)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    # def del_rcd(self, data={}, table=None):
    #     table_name = table
    #     if table_name is None:
    #         table_name = self.table_name
    #     try:
    #         for key, val in data.items():
    #             query = f'delete from {table_name} where {key}={val}'
    #
    #             with pg2.connect(**self.config) as conn:
    #                 with conn.cursor()as cur:
    #                     cur.execute(query)
    #
    #     except Exception as e:
    #         logger.error(str(e))
    #         logger.error(traceback.format_exc())
    #         return ResponseForm(res=False, msg=str(e))
    #
    #     return ResponseForm(res=True)

    def drop_tables(self, schema_list=[], omit_schema_list=[], omit_tbl_list=[]):
        try:
            with pg2.connect(**self.config) as conn:
                conn.autocommit = True
                with conn.cursor() as cur:
                    # cur.execute('select nspname from pg_catalog.pg_namespace')
                    # rows = cur.fetchall()

                    for schema in schema_list:
                        if schema not in omit_schema_list:
                            sql = "SELECT table_schema,table_name FROM information_schema.tables " \
                                  "WHERE table_schema = '%s' ORDER BY table_schema,table_name" % schema
                            cur.execute(sql)
                            tables = cur.fetchall()
                            for table in tables:
                                tb_name = schema + '.' + table[1]
                                if tb_name not in omit_tbl_list:
                                    sql = 'drop table ' + tb_name + " cascade"
                                    cur.execute(sql)

            return ResponseForm(res=True)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def export_tables_from_schema(self, schema_list, omit_tb_list=[]):
        try:
            # with pg2.connect(**self.config) as conn:
            #     with conn.cursor() as cur:
            #         data = dict()
            #         for schema in schema_list:
            #             sql = "SELECT table_schema,table_name FROM information_schema.tables " \
            #                   "WHERE table_schema = '%s' ORDER BY table_schema,table_name" % schema
            #             cur.execute(sql)
            #             tables = cur.fetchall()
            #             for table in tables:
            #                 tb_name = schema + '.' + table[1]
            #                 if tb_name not in omit_tb_list:
            #                     buffer = self.fetch_all_as_csv(table=tb_name)
            #                     data[tb_name] = buffer

            data = dict()
            for schema in schema_list:
                sql = "SELECT table_schema,table_name FROM information_schema.tables " \
                      "WHERE table_schema = '%s' ORDER BY table_schema,table_name" % schema
                self.cursor.execute(sql)
                tables = self.cursor.fetchall()
                for table in tables:
                    tb_name = schema + '.' + table[1]
                    if tb_name not in omit_tb_list:
                        buffer = self.fetch_all_as_csv(table=tb_name)
                        data[tb_name] = buffer

            return ResponseForm(res=True, data=data)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_table_list_from_schema(self, schema_list, omit_list=[]):
        try:
            table_list = []
            # with pg2.connect(**self.config) as conn:
            #     with conn.cursor() as cur:
            #         for schema in schema_list:
            #             sql = "SELECT table_schema,table_name FROM information_schema.tables " \
            #                   "WHERE table_schema = '%s' ORDER BY table_schema,table_name" % schema
            #             cur.execute(sql)
            #             tables = cur.fetchall()
            #             for table in tables:
            #                 tb_name = schema + '.' + table[1]
            #                 if tb_name not in omit_list:
            #                     table_list.append(tb_name)

            for schema in schema_list:
                sql = "SELECT table_schema,table_name FROM information_schema.tables " \
                      "WHERE table_schema = '%s' ORDER BY table_schema,table_name" % schema
                self.cursor.execute(sql)
                tables = self.cursor.fetchall()
                for table in tables:
                    tb_name = schema + '.' + table[1]
                    if tb_name not in omit_list:
                        table_list.append(tb_name)

            return ResponseForm(res=True, data=table_list)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def fetch_all_as_csv(self, table):
        buffer = StringIO()
        try:
            # with pg2.connect(**self.config) as conn:
            #     with conn.cursor() as cur:
            #         # query = "copy (select * from %s) to stdout with csv" % table
            #         # cur.copy_expert(query, buffer)
            #         cur.copy_to(buffer, table, sep='\t', null=NA_VALUE)
            #         return buffer
            self.cursor.copy_to(buffer, table, sep='\t', null=NA_VALUE)
            self.connect.commit()
            return buffer
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return None

    def delete(self, table=None, where_dict=None, where_phrase=None, rtn_id=False):
        table_name = table
        if table_name is None:
            table_name = self.table_name

        if where_dict is None and where_phrase is None:
            return ResponseForm(res=False, msg='WHERE condition is empty.')

        query = f"delete from {table_name} where "
        if where_dict is not None:
            for key, val in where_dict.items():
                query = query + "{0}='{1}' and ".format(key, val)
            query = query[:-5]

            if where_phrase is not None:
                query = query + ' and '

        if where_phrase is not None:
            query = query + where_phrase

        if rtn_id:
            query = query + ' RETURNING id'

        try:
            # with pg2.connect(**self.config) as conn:
            #     with conn.cursor()as cur:
            #         cur.execute(query)
            #         if rtn_id:
            #             _id = cur.fetchone()
            #             if _id is None:
            #                 return ResponseForm(res=False, msg='Delete Fail. No matching condition.')
            #             else:
            #                 return ResponseForm(res=True, data=_id[0])
            #         else:
            #             return ResponseForm(res=True)

            self.cursor.execute(query)
            if rtn_id:
                _id = self.cursor.fetchone()
                if _id is None:
                    return ResponseForm(res=False, msg='Delete Fail. No matching condition.')
                else:
                    self.connect.commit()
                    return ResponseForm(res=True, data=_id[0])
            else:
                self.connect.commit()
                return ResponseForm(res=True)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    def get_log_period(self, table=None, where=None):
        table_name = table
        if table_name is None:
            table_name = self.table_name

        try:
            query = f"select to_char(min(log_time), 'YYYY-MM-DD HH24:MI:SS') as start, " \
                    f"to_char(max(log_time), 'YYYY-MM-DD HH24:MI:SS') as end from {table_name}"

            if where is not None:
                query = query + ' where '
                for key, val in where.items():
                    query = query + "{0}='{1}' and ".format(key, val)
                query = query[:-5]

            # with pg2.connect(**self.config) as conn:
            #     with conn.cursor(cursor_factory=pg2.extras.DictCursor)as cur:
            #         cur.execute(query)
            #         ret = cur.fetchone()
            #         if ret is None:
            #             return ResponseForm(res=False, msg='There is no data')
            #         else:
            #             return ResponseForm(res=True, data=dict(ret))

            self.dict_cursor.execute(query)
            ret = self.dict_cursor.fetchone()
            if ret is None:
                return ResponseForm(res=False, msg='There is no data')
            else:
                return ResponseForm(res=True, data=dict(ret))
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))

    # def load_data_by_id(self, job_id, columns=None):
    #     if columns is None:
    #         self.df = self.fetch_all(args={'where': "request_id='{0}'".format(job_id)})
    #     else:
    #         self.df = self.fetch_all(args={'select': columns,
    #                                        'where': "request_id='{0}'".format(job_id)})
    #
    #     # 時間順序で整列
    #     if 'log_time' in self.df.columns:
    #         self.df.sort_values(by='log_time', ascending=True, inplace=True)
    #
    #     return len(self.df)

    def get_log_time_min(self):
        return self.df['log_time'].min()

    def get_log_time_max(self):
        return self.df['log_time'].max()

    def load_data(self, table=None, rid=None, select=None, **filters):
        fetch_args = dict()
        where = ''
        if select is not None:
            fetch_args['select'] = select

        if rid is not None:
            where = f"request_id='{rid}'"

        for key, val in filters.items():
            if len(where) > 0:
                where = where + ' and '
            if key == 'log_time':
                end = filters[key]['end']
                try:
                    datetime.datetime.strptime(end, '%Y-%m-%d')
                    end = end + ' 23:59:59'
                except Exception as e:
                    pass
                where = where + f"log_time between '{filters[key]['start']}' and '{end}'"
            else:
                if isinstance(val, list):
                    if len(val) > 1:
                        val = ["'"+str(v)+"'" for v in val]
                        _in = ','.join(val)
                        cond = f"{key} in ({_in})"
                        where = where + cond
                    else:
                        where = where + f"{key}='{val[0]}'"
                else:
                    where = where + f"{key}='{val}'"

        if len(where) > 0:
            fetch_args['where'] = where
        # if args['jobname'] is not None:
        #     device = args['jobname'].split('/')[0]
        #     process = args['jobname'].split('/')[1]
        #     fetch_args['where'] = f"request_id='{job_id}' " \
        #                           f"and process='{process}' and device='{device}' " \
        #                           f"and log_time between '{args['start']}' and '{args['end']}'"
        #     self.df = self.fetch_all(args=fetch_args)
        # else:
        #     fetch_args['where'] = f"request_id='{job_id}' " \
        #                           f"and log_time between '{args['start']}' and '{args['end']}'"
        #     self.df = self.fetch_all(args=fetch_args)

        self.df = self.fetch_all(table=table, args=fetch_args)
        for col in COLUMN_OMIT_LIST:
            if col in self.df.columns:
                self.df.drop(col, axis=1, inplace=True)

        if len(self.df) > 0 and 'log_time' in self.df.columns:
            # 時間順序で整列
            self.df.sort_values(by='log_time', ascending=True, inplace=True)
            self.df.reset_index(inplace=True, drop=True)

        # if len(self.df) > 0:
        #     if args['filter_key'] is not None and args['filter_value'] is not None:
        #         filter_key = args['filter_key']
        #         filter_value = args['filter_value']
        #         if filter_key in self.df.columns:
        #             if isinstance(self.df[filter_key][0], str):
        #                 self.df = self.df[self.df[filter_key] == filter_value].reset_index(drop=True)
        #             else:
        #                 self.df = self.df[self.df[filter_key] == int(filter_value)].reset_index(drop=True)
        #
        #     # 時間順序で整列
        #     self.df.sort_values(by='log_time', ascending=True, inplace=True)
        #     self.df.reset_index(inplace=True, drop=True)
        #
        #     if 'glass_id' in self.df.columns and 'step_no' in self.df.columns:
        #         # ログをクリーンにする(不要行削除)
        #         preprocessing.creanup_log_list_by_job(self.df)
        #
        #     # ログをクリーンにする(不要行削除)
        #     self.df = preprocessing.creanup_log_list_by_term(self.df, args['valid_interval_minutes'])
        #
        #     if args['group_by'] == 'period':
        #         self.df = preprocessing.divide_by_stats_period(self.df, args['start'], args['group_value'])

        return len(self.df)

    def get_df(self):
        return deepcopy(self.df)

    def get_column_info(self, table=None):
        table_name = table
        if table_name is None:
            table_name = self.table_name

        schema_name = table_name.split('.')[0]
        table_name = table_name.split('.')[1]

        query = f"select column_name, data_type, character_maximum_length from information_schema.columns " \
                f"where table_schema='{schema_name}' and table_name='{table_name}'"

        # with pg2.connect(**self.config) as conn:
        #     return pd.read_sql(query, conn)

        return pd.read_sql(query, self.connect)

    def remove_all_records(self, schema_list, omit_tb_list):
        try:
            # with pg2.connect(**self.config) as conn:
            #     with conn.cursor() as cur:
            #         data = dict()
            #         for schema in schema_list:
            #             sql = "SELECT table_schema,table_name FROM information_schema.tables " \
            #                   "WHERE table_schema = '%s' ORDER BY table_schema,table_name" % schema
            #             cur.execute(sql)
            #             tables = cur.fetchall()
            #             for table in tables:
            #                 tb_name = schema + '.' + table[1]
            #                 if tb_name not in omit_tb_list:
            #                     sql = f"truncate table {tb_name} restart identity cascade"
            #                     cur.execute(sql)

            data = dict()
            for schema in schema_list:
                sql = "SELECT table_schema,table_name FROM information_schema.tables " \
                      "WHERE table_schema = '%s' ORDER BY table_schema,table_name" % schema
                self.cursor.execute(sql)
                tables = self.cursor.fetchall()
                for table in tables:
                    tb_name = schema + '.' + table[1]
                    if tb_name not in omit_tb_list:
                        sql = f"truncate table {tb_name} restart identity cascade"
                        self.cursor.execute(sql)
                        self.connect.commit()

            return ResponseForm(res=True, data=data)
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.format_exc())
            return ResponseForm(res=False, msg=str(e))
