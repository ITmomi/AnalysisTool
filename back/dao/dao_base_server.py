import os
from io import StringIO
import traceback
import logging

import psycopg2.extras
import psycopg2 as pg2
import pandas as pd
from dao.utils import get_db_config, test_db_connection, exist_table, exist_data_from_table, copy_table
from config import app_config

logger = logging.getLogger(app_config.LOG)


class BaseServerDao:
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
        print('initialize base server dao')
        self.config = get_db_config()
        self.schema = 'cnvbase'

    # Deprecated
    def get_log_format(self, log_name):
        try:
            with pg2.connect(**self.config) as connect:
                with connect.cursor() as cursor:
                    sql = '''select log_format from cnvbase.log_define_master where log_name=%(log_name)s limit 1'''
                    cursor.execute(sql, locals())
                    return cursor.fetchone()
        except Exception as msg:
            print('failed to get log format (%s)' % msg)
            logger.error(traceback.format_exc())

    def get_equipments(self, equipment_type=None, site=None, fab=None, df=False):
        try:
            with pg2.connect(**self.config) as connect:
                sql = None
                if equipment_type is not None:
                    sql = f"select * from cnvbase.equipments where \
                            equipment_type='{equipment_type}' and exec is true"
                elif site is not None and fab is not None:
                    sql = f"select * from cnvbase.equipments where \
                            user_name='{site}' and fab_name='{fab}' and exec is true"
                else:
                    sql = f"select * from cnvbase.equipments where exec is true"
                if df:
                    return pd.read_sql(sql, connect)
                else:
                    with connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                        cursor.execute(sql, locals())
                        _equipments = cursor.fetchall()
                        equipments = []
                        for equipment in _equipments:
                            equipments.append(dict(equipment))
                        return equipments

        except Exception as msg:
            print('failed to get equipment (%s)' % msg)
            logger.error(traceback.format_exc())

    def get_equipment(self, equipment_name):
        try:
            with pg2.connect(**self.config) as connect:
                with connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    sql = '''
                        select * from cnvbase.equipments where equipment_name=%(equipment_name)s
                    '''
                    cursor.execute(sql, locals())
                    eqp = cursor.fetchone()
                    if eqp is None:
                        print('no equipment called %s' % equipment_name)
                        return None
                    return dict(eqp)

        except Exception as msg:
            print('failed to get equipment (%s)' % msg)
            logger.error(traceback.format_exc())

    def get_table_info(self, table_name):
        try:
            with pg2.connect(**self.config) as connect:
                with connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(f"select exists (select from information_schema.tables \
                                    where table_schema='convert' and table_name='{table_name}')")
                    exist = cursor.fetchone()
                    if not exist[0]:
                        return None
                    return 'tbd'
        except Exception as msg:
            print(f'failed to get table info {msg}')
            logger.error(traceback.format_exc())

    def get_log_define(self, log_name):
        try:
            with pg2.connect(**self.config) as connect:
                with connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(f"select * from cnvbase.log_define_master where log_name='{log_name}'")
                    _ret = cursor.fetchone()
                    if _ret is None:
                        return None
                    return dict(_ret)
        except Exception as msg:
            print(f'failed to get log definition. {msg}')
            logger.error(traceback.format_exc())
        return None

    def find_transfer_log_list(self, log_name):
        if not log_name or log_name == '':
            return None

        sql = f"select * from cnvbase.transfer_log_list where logname = '{log_name}' or \
                    destination_path = '{log_name}'"
        try:
            with pg2.connect(**self.config) as connect:
                with connect.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(sql)
                    _ret = cursor.fetchone()
                    if _ret is None:
                        return None
                    return dict(_ret)
        except Exception as msg:
            print(f'failed to find transfer log list. {msg}')
            logger.error(traceback.format_exc())
        return None

    def get_all_data(self, table):
        try:
            sql = f"select * from {table}"
            with pg2.connect(**self.config) as connect:
                return pd.read_sql(sql, connect)
        except Exception as msg:
            print(f'failed to get all data from {table}. {msg}')
            logger.error(traceback.format_exc())
        return None


def init_converter_data():

    # Migration from legacy cras_db
    legacy_db = os.environ.get('LEGACY_DB')
    if legacy_db is None:
        return

    legacy_config = parse_env_db_config(legacy_db)
    if legacy_config is None:
        return

    legacy_config = {**legacy_config, 'dbname': 'cras_db'}
    if test_db_connection(legacy_config):
        print(f"** legacy system available {legacy_config['host']}:{legacy_config['port']}")
        table_list = ['equipment_types', 'equipments']

        for tbl in table_list:
            _str = f'checking {tbl} '
            try:
                if copy_table(legacy_config, get_db_config(), 'public', 'cnvbase', tbl):
                    _str = f'{_str} .. copied'
                else:
                    _str = f'{_str} .. okay'
            except RuntimeError as msg:
                _str = f'{_str} .. failed. {msg}'
            print(_str)
            # if exist_table(tbl, 'cnvbase') and not exist_data_from_table(f'cnvbase.{tbl}'):
            #     # Do copy
            #     print(f' copy {tbl} data from cras_db')
            #     if not exist_table(tbl, config=legacy_config) or not exist_data_from_table(tbl, legacy_config):
            #         print(f'..no data exist in cras_db')
            #         continue
            #     with pg2.connect(**legacy_config) as conn_from:
            #         with conn_from.cursor() as cur_from:
            #             cur_from.execute(f"select * from {tbl} limit 0")
            #             columns = [desc[0] for desc in cur_from.description]
            #
            #             buffer = StringIO()
            #             cur_from.copy_to(buffer, tbl, sep='\t', null='-99999999999999', columns=columns)
            #             buffer.seek(0)
            #
            #             with pg2.connect(**get_db_config()) as conn_to:
            #                 with conn_to.cursor() as cur:
            #                     try:
            #                         cur.copy_from(buffer, f'cnvbase.{tbl}', sep="\t", null='-99999999999999', columns=columns)
            #                     except (Exception, pg2.DatabaseError) as error:
            #                         print(f'..error occurs on copy table. {error}')
            #                         conn_to.rollback()
            #
            #     print('..success')

    # Migration from setting_db
    set_db = os.environ.get('SET_DB')
    if set_db is None:
        return

    set_config = parse_env_db_config(set_db)
    if set_config is None:
        return

    set_config = {**set_config, 'dbname': 'settings'}
    if test_db_connection(set_config):
        print(f"** setting_db system available {set_config['host']}:{set_config['port']}")
        table_list = ['error_category',
                      'convert_columns_define',
                      'transfer_log_list',
                      'running_log_define',
                      'status_monitor_items',
                      'log_define']

        for tbl in table_list:
            _str = f'checking {tbl} '
            try:
                if copy_table(set_config, get_db_config(), 'public', 'cnvbase', tbl):
                    _str = f'{_str} .. copied'
                else:
                    _str = f'{_str} .. okay'
            except RuntimeError as msg:
                _str = f'{_str} .. failed. {msg}'
            print(_str)
            # print(f'checking {tbl}...')
            # if exist_table(tbl, 'cnvbase') and not exist_data_from_table(f'cnvbase.{tbl}'):
            #     # Do copy
            #     print(f' copy {tbl} data from settings')
            #     if not exist_table(tbl, config=set_config) or not exist_data_from_table(tbl, set_config):
            #         print(f'..no data exist in settings')
            #         continue
            #     with pg2.connect(**set_config) as conn_from:
            #         with conn_from.cursor() as cur_from:
            #             cur_from.execute(f"select * from {tbl} limit 0")
            #             columns = [desc[0] for desc in cur_from.description]
            #
            #             buffer = StringIO()
            #             cur_from.copy_to(buffer, tbl, sep='\t', null='-99999999999999', columns=columns)
            #             buffer.seek(0)
            #
            #             with pg2.connect(**get_db_config()) as conn_to:
            #                 with conn_to.cursor() as cur:
            #                     try:
            #                         cur.copy_from(buffer, f'cnvbase.{tbl}', sep="\t", null='-99999999999999', columns=columns)
            #                     except (Exception, pg2.DatabaseError) as error:
            #                         print(f'..error occurs on copy table. {error}')
            #                         conn_to.rollback()
            #
            #     print('..success')


def parse_env_db_config(env):
    if env is None:
        return None

    env_list = env.split(',')
    if len(env_list) < 4 or len(env_list[0]) == '':
        return None

    return {
        'host': env_list[0],
        'port': env_list[1],
        'user': env_list[2],
        'password': env_list[3]
    }


if __name__ == '__main__':
    init_converter_data()