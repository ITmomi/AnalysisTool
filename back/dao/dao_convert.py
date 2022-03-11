import os
from io import StringIO
import logging
import traceback
import pandas as pd
import pandas.io.sql as sqlio
import psycopg2 as pg2
import psycopg2.extras
import psycopg2.errors
import configparser

from config.app_config import *
from dao.exception import DatabaseQueryException
from dao.utils import get_db_config

logger = logging.getLogger(LOG)


class ConvertDao:

    __instance = None

    @classmethod
    def __get_instance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__get_instance
        return cls.__instance

    def __init__(self):
        print('initialize job dao')
        self.config = get_db_config()

    def insert_df(self, table, df):
        if not str(table).startswith('convert'):
            table = 'convert.%s' % table

        buffer = StringIO()

        if '' in df.columns:
            del df['']

        df['created_time'] = pd.Timestamp.now()

        # df.to_csv('test.csv', index=False, header=True)
        df.to_csv(buffer, index=False, header=False)
        buffer.seek(0)

        with pg2.connect(**self.config) as conn:
            with conn.cursor() as cur:
                try:
                    cur.copy_from(buffer, table, sep=",", columns=df.columns, null=NA_VALUE)
                except (Exception, pg2.DatabaseError) as error:
                    conn.rollback()
                    raise DatabaseQueryException(error)

    def count_row(self, table):
        if not str(table).startswith('convert'):
            table = 'convert.%s' % table
        with pg2.connect(**self.config) as connect:
            with connect.cursor() as cursor:
                cursor.execute(f'select count(*) from {table}')
                return int(cursor.fetchone()[0])
        print('unexpected operation')
        return 0

    def get_columns(self, table):
        if not str(table).startswith('convert'):
            table = 'convert.%s' % table
        schema, table = table.split('.')
        with pg2.connect(**self.config) as connect:
            sql = "select * from information_schema.columns where table_name = '%s' and table_schema = '%s'" \
                  % (table, schema)
            df = sqlio.read_sql_query(sql, connect)
            return df['column_name'].tolist()

    def get_version_info_log_time(self, count=2):
        try:
            with pg2.connect(**self.config) as connect:
                with connect.cursor() as cursor:
                    cursor.execute(f"select log_time from convert.version_info group by log_time \
                                        order by log_time desc limit {count}")
                    _ret = cursor.fetchall()
                    ret = [_[0] for _ in _ret]
                    return ret
        except Exception as msg:
            print(f'failed to get version info log time. {msg}')
            logger.error(traceback.format_exc())
        return None

    def get_version_info(self, date=None, df=False):
        try:
            with pg2.connect(**self.config) as connect:
                where_date = ''
                if date is not None:
                    where_date = f"where log_time = '{date}'"
                sql = f"select * from convert.version_info {where_date}"
                if df:
                    return pd.read_sql(sql, connect)
                else:
                    with connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                        cursor.execute(sql)
                        _ret = cursor.fetchall()
                        ret = [dict(_) for _ in _ret]
                        return ret
        except Exception as msg:
            print(f'failed to get version info. {msg}')
            logger.error(traceback.format_exc())
        return None

    def get_log_info(self, table, equipment=None):
        try:
            with pg2.connect(**self.config) as connect:
                with connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    sql_equipment = ''
                    if equipment is not None:
                        sql_equipment = f"where equipment_name='{equipment}'"
                    cursor.execute(f"select to_char(min(log_time), 'YYYY-MM-DD HH24:MI:SS') as start, \
                                        to_char(max(log_time), 'YYYY-MM-DD HH24:MI:SS') as end, count(*) \
                                        from convert.{table} {sql_equipment}")
                    _ret = cursor.fetchone()
                    if _ret is None:
                        return None
                    return dict(_ret)
        except Exception as msg:
            print(f'failed to get log info. {msg}')
            logger.error(traceback.format_exc())
        return None

    def get_converted_data(self, table, start, end, equipment=None):
        try:
            with pg2.connect(**self.config) as connect:
                with connect.cursor() as cursor:
                    sql_interval = f"where log_time >= '{start}' and log_time <= '{end}'"
                    sql_equipment = ''
                    if equipment is not None:
                        sql_equipment = f"and equipment_name='{equipment}'"
                    buffer = StringIO()
                    sql = f"copy (select * from convert.{table} {sql_interval} {sql_equipment}) \
                            to stdout with csv delimiter '\t' null as '{NA_VALUE}'"
                    cursor.copy_expert(sql, buffer)
                    return buffer.getvalue()
        except Exception as msg:
            print(f'failed to get converted log. {msg}')
            logger.error(traceback.format_exc())
        return None


def create_converter_tables():
    config = get_db_config()
    try:
        with pg2.connect(**config) as connect:
            with connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # Get a table list we must create.
                cursor.execute('select log_name, db_table from cnvbase.log_define_master group by log_name, db_table')
                _ret = cursor.fetchall()
                tables = [dict(_) for _ in _ret]

                create_list = []
                for tbl in tables:
                    _str = f"{tbl['db_table']} ({tbl['log_name']})"
                    cursor.execute(f"select exists (select from information_schema.tables where \
                                        table_schema='convert' and table_name='{tbl['db_table']}')")
                    _ret = cursor.fetchone()
                    _str = f'{_str} ... {_ret}'

                    if not _ret[0]:
                        cursor.execute(f"select output_col_name, data_type from cnvbase.convert_columns_define where \
                                            log_name = '{tbl['log_name']}' group by output_col_name, data_type")

                        _ret = cursor.fetchall()

                        _str = f'{_str} ... {len(_ret)}'

                        if len(_ret) == 0:
                            print(f"no data to create {tbl['db_table']} table")
                        else:
                            columns = [dict(_) for _ in _ret]
                            create_list.append({'define': tbl, 'column': columns})

                    print(_str)

                if len(create_list) == 0:
                    return

                for tbl in create_list:
                    table_name = tbl['define']['db_table']
                    print(f"create a table {table_name}")
                    sql = f"create table convert.{table_name} ( \
                            equipment_name text not null, \
                            log_time timestamp not null, "

                    for col in tbl['column']:
                        out_col = col['output_col_name']
                        # Exception handling code.
                        if out_col == '' or out_col == 'time' or out_col == 'date' or out_col == 'log_time':
                            continue
                        data_type = get_type_from_column_define(col['data_type'])
                        if data_type is None:
                            continue
                        sql = f"{sql} {out_col} {data_type}, "

                    sql = f"{sql} \
                            log_idx integer not null, \
                            created_time timestamp not null, \
                            request_id varchar(50), \
                            constraint {table_name}__pkey primary key (equipment_name, log_time, log_idx));"

                    cursor.execute(sql)
                    print(f"table {table_name} has been created")

    except Exception as msg:
        print(f'failed to create converter tables. {msg}')
        logger.error(traceback.format_exc())


def get_type_from_column_define(data_type):
    if data_type.startswith('timestamp'):
        return 'timestamp not null'
    elif data_type == 'integer' or data_type == 'int' or data_type == 'iteger' or data_type == 'inetege':
        return 'integer'
    elif data_type == 'floart' or data_type == 'float':
        return 'double precision'
    elif data_type == 'devpro':
        return None
    elif data_type == 'character' or data_type == 'chatracter' or data_type == 'text':
        return 'text'
    else:
        return None

