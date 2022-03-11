import os
import psycopg2 as pg2
import configparser
import logging
import pandas as pd
import io
import csv
import traceback

from config.app_config import *
from common.utils.response import ResponseForm
from dao.dao_convert import create_converter_tables
from dao.utils import get_db_config
from dao.dao_base import DAOBaseClass
from config import app_config

logger = logging.getLogger(app_config.LOG)


def get_dbinfo(**kwargs):
    config = get_db_config()

    if 'dbname' in kwargs:
        config['dbname'] = kwargs['dbname']
    if 'user' in kwargs:
        config['user'] = kwargs['user']
    if 'host' in kwargs:
        config['host'] = kwargs['host']
    if 'password' in kwargs:
        config['password'] = kwargs['password']
    if 'port' in kwargs:
        config['port'] = kwargs['port']

    return config


# def init_db():
#     init_database()
#     init_schema()
#     init_type()
#     init_table()
#     init_data()


# def db_validate():
#     dao = DAOBaseClass()
#     drop_list = []
#
#     if check_force_init_condition():
#         drop_list = SCHEMA_CREATE_LIST
#     else:
#         for item in schema_ver_key_list:
#             if check_schem_init_condition(item['version'], item['key']) is True:
#                 drop_list.append(item['schem_name'])
#                 logger.info(f"Drop {item['schem_name']} tables.")
#
#     if len(drop_list) > 0:
#         dao.drop_tables(schema_list=drop_list, omit_tbl_list=[TBL_SETTINGS_INFORMATION])
#         init_db()
#
#
# def check_force_init_condition():
#     force_init_version_list = ['1.0.0', '1.1.0']
#
#     config = get_dbinfo()
#     ret = False
#     try:
#         with pg2.connect(**config) as conn:
#             with conn.cursor() as cur:
#                 cur.execute("select value from settings.information where key='version'")
#                 rows = cur.fetchone()
#                 pre_version = rows[0]
#                 # [major, minor, revision] = rows[0].split(sep='.')
#
#                 # if int(major) == APP_MAJOR:
#                 #     # Version Up or Down check both.
#                 #     if int(minor) != APP_MINOR:
#                 #         ret = True
#                 #     else:
#                 #         ret = False
#                 # else:
#                 #     ret = True
#                 if pre_version != APP_VERSION and pre_version in force_init_version_list:
#                     ret = True
#                 else:
#                     ret = False
#
#                 query = f"update settings.information set value='{APP_VERSION}' where key='version'"
#                 cur.execute(query)
#
#     except Exception as e:
#         logger.error(str(e))
#         logger.error(traceback.format_exc())
#
#     return ret


# def check_schem_init_condition(version=None, key=None):
#     if version is None or key is None:
#         return False
#
#     config = get_dbinfo()
#     ret = False
#     try:
#         with pg2.connect(**config) as conn:
#             with conn.cursor() as cur:
#                 cur.execute(f"select value from settings.information where key='{key}'")
#                 rows = cur.fetchone()
#                 if rows is None:
#                     query = f"insert into settings.information(key, value) values('{key}', '{version}')"
#                     cur.execute(query)
#                     ret = True
#                 else:
#                     schem_version = rows[0]
#
#                     if schem_version != version:
#                         query = f"update settings.information set value='{version}' where key='{key}'"
#                         cur.execute(query)
#                         ret = True
#
#     except Exception as e:
#         logger.error(str(e))
#         logger.error(traceback.format_exc())
#
#     return ret


def init_database():
    config = get_dbinfo()
    db_config = configparser.ConfigParser()
    db_config.read(DB_CONFIG_PATH)

    config['dbname'] = db_config['DBSETTINGS']['MGMT_DB_NAME']
    db_name = db_config['DBSETTINGS']['DB_NAME']

    try:
        with pg2.connect(**config) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                # Database目録獲得
                cur.execute('SELECT datname FROM pg_database')
                rows = cur.fetchall()

                # Database生成
                if (db_name,) not in rows:
                    cur.execute('create database %s' % db_name)
                    logger.info('%s database created!!')

                # cur.close()
            # conn.commit()
            # conn.close()
    except Exception as e:
        logger.error('database create error!')
        logger.error(str(e))
        logger.error(traceback.format_exc())


# def init_schema(**kwargs):
#     config = get_dbinfo(**kwargs)
#     try:
#         with pg2.connect(**config) as conn:
#             conn.autocommit = True
#             with conn.cursor() as cur:
#                 # DBの全体Schema目録獲得
#                 cur.execute('select nspname from pg_catalog.pg_namespace')
#                 rows = cur.fetchall()
#
#                 # Schema生成
#                 for item in SCHEMA_CREATE_LIST:
#                     if (item,) not in rows:
#                         cur.execute('create schema %s' % item)
#                         logger.info(item + ' schema is created!!')
#     except Exception as e:
#         logger.error('schema create error!')
#         logger.error(str(e))
#         logger.error(traceback.format_exc())


# def init_type(**kwargs):
#     config = get_dbinfo(**kwargs)
#     try:
#         with pg2.connect(**config) as conn:
#             conn.autocommit = True
#             with conn.cursor() as cur:
#                 sql_path = 'resource/sql/type'
#                 for file_name in os.listdir(sql_path):
#                     if os.path.isdir(os.path.join(sql_path, file_name)) is False:
#                         [schema, type_name, extension] = file_name.split(sep='.')
#                         cur.execute("SELECT EXISTS "
#                                     "(SELECT FROM pg_type WHERE typname='%s')"
#                                     % type_name)
#
#                         rows = cur.fetchone()
#                         if rows[0] is False:
#                             file_path = os.path.join(sql_path, file_name)
#                             cur.execute(open(file_path, 'r').read())
#                             logger.info(schema + '.' + type_name + ' type is created!!')
#     except Exception as e:
#         logger.error('type create error!')
#         logger.error(str(e))
#         logger.error(traceback.format_exc())


# def init_table(**kwargs):
#     config = get_dbinfo(**kwargs)
#     sql_path = './resource/sql/table'
#     file_list = {file_name: False for file_name in os.listdir(sql_path)}
#
#     idx = 0
#     loop_cnt = 0
#     complete = False
#
#     while not complete:
#         if loop_cnt >= 5:
#             return ResponseForm(res=False, msg='Retry too many times.')
#         try:
#             with pg2.connect(**config) as conn:
#                 conn.autocommit = True
#                 with conn.cursor() as cur:
#                     (file_name, value) = list(file_list.items())[idx]
#
#                     # Table生成
#                     if os.path.isdir(os.path.join(sql_path, file_name)) is False and value is False:
#                         [schema, table_name, extension] = file_name.split(sep='.')
#
#                         cur.execute("SELECT EXISTS "
#                                     "(SELECT FROM information_schema.tables WHERE table_schema='%s' AND table_name='%s')"
#                                     % (schema, table_name))
#
#                         rows = cur.fetchone()
#                         if rows[0] is False:
#                             file_path = os.path.join(sql_path, file_name)
#                             cur.execute(open(file_path, 'r').read())
#                             logger.info(schema + '.' + table_name + ' table is created!!')
#
#                             file_list[file_name] = True
#
#                             if table_name == 'management_setting':
#                                 # Insert Management Setting Info
#                                 query = '''
#                                                     insert into settings.management_setting(target, host, username, password, dbname, port)
#                                                     values(%s, %s, %s, %s, %s, %s)
#                                                 '''
#                                 record = ('local', config['host'], config['user'], config['password'], config['dbname'], config['port'])
#                                 cur.execute(query, record)
#
#                                 # query = '''
#                                 #                     insert into settings.management_setting(target, host, username, password, dbname, port)
#                                 #                     values('remote', null, null, null, null, null)
#                                 #                 '''
#                                 # cur.execute(query)
#
#                             elif table_name == 'information':
#                                 query = 'insert into settings.information(key, value) values(%s, %s)'
#                                 record = ('version', APP_VERSION)
#                                 cur.execute(query, record)
#
#                                 for item in schema_ver_key_list:
#                                     record = (item['key'], item['version'])
#                                     cur.execute(query, record)
#                             elif table_name == 'system_graph_type':
#                                 with open(os.path.join(RESOURCE_PATH, RSC_SYSTEM_GRAPH_SCRIPT), 'r') as f:
#                                     data = f.read()
#
#                                 query = 'insert into graph.system_graph_type(name, script) values(%s, %s)'
#                                 record = ('default', data)
#                                 cur.execute(query, record)
#                             else:
#                                 public_tables = {
#                                     'aggregation_type': app_config.aggregation_type,
#                                     'analysis_type': app_config.analysis_type,
#                                     'calc_type': app_config.calc_type,
#                                     'graph_type': app_config.graph_type,
#                                     'source_type': app_config.source_type
#                                 }
#
#                                 if table_name in public_tables:
#                                     for item in public_tables[table_name]:
#                                         query = f'insert into {schema}.{table_name}(type) values(%s)'
#                                         cur.execute(query, tuple([item]))
#                         else:
#                             file_list[file_name] = True
#
#             if False in file_list.values():
#                 idx += 1
#                 if idx == len(list(file_list.items())):
#                     idx = 0
#                     loop_cnt += 1
#                     logger.info('Retry...')
#             else:
#                 complete = True
#
#         except Exception as e:
#             logger.error('table create error!')
#             logger.error(str(e))
#             logger.error(traceback.format_exc())
#             idx += 1
#             if idx == len(list(file_list.items())):
#                 idx = 0
#                 loop_cnt += 1
#                 logger.info('Retry...')
#
#     return ResponseForm(res=True)


def init_data(file=None, **kwargs):
    config = get_dbinfo(**kwargs)

    try:
        if file is None:
            path = './resource/data/initial_data.xlsx'
            if not os.path.exists(path):
                return ResponseForm(res=False, msg=f'{path} does not exist')

            xl = pd.ExcelFile(path)
        else:
            xl = pd.ExcelFile(file)
    except Exception as e:
        logger.error(str(e))
        logger.error(traceback.format_exc())
        return ResponseForm(res=False, msg=str(e))

    sheet_dict = {tb_name: False for tb_name in xl.sheet_names}
    sheet_list = xl.sheet_names

    idx = 0
    loop_cnt = 0
    complete = False

    while not complete:
        if loop_cnt >= 5:
            return ResponseForm(res=False, msg='Retry too many times.')
        try:
            with pg2.connect(**config) as conn:
                with conn.cursor() as cur:
                    table_name = sheet_list[idx]
                    [schema, table] = table_name.split(sep='.')
                    sql = 'select count(*) from %s' % table_name
                    cur.execute(sql)
                    count = cur.fetchone()[0]
                    if count == 0:
                        buf = io.StringIO()
                        df = xl.parse(sheet_name=table_name, header=None, na_filter=False)
                        df.to_csv(buf, sep='\t', header=False, index=False, quoting=csv.QUOTE_NONE)
                        buf.seek(0)
                        cur.copy_from(buf, table_name, sep='\t', null=NA_VALUE)
                        sheet_dict[table_name] = True
                        logger.info(table_name + ' data insert OK.')

                        sql = f"SELECT * FROM information_schema.columns WHERE table_name = '{table}' AND column_name = 'id'"
                        cur.execute(sql)
                        row = cur.fetchall()
                        if len(row) > 0:
                            sql = f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), MAX(id)) FROM {table_name}"
                            cur.execute(sql)
                    else:
                        sheet_dict[table_name] = True

            if False in sheet_dict.values():
                idx += 1
                if idx == len(list(sheet_dict.items())):
                    idx = 0
                    loop_cnt += 1
                    logger.info('Retry...')
            else:
                complete = True
        except Exception as msg:
            logger.error('failed to initialize cnvbase tables (%s)' % msg)
            logger.error(traceback.format_exc())
            idx += 1
            if idx == len(list(sheet_dict.items())):
                idx = 0
                loop_cnt += 1
                logger.info('Retry...')

    return ResponseForm(res=True)


# def init_data(**kwargs):
#     config = get_dbinfo(**kwargs)
#     data_path = './resource/data'
#     # tables = ['cnvbase.equipment_types', 'cnvbase.equipments', 'cnvbase.log_define_master', 'cnvbase.convert_columns_define']
#
#     file_list = {file_name: False for file_name in os.listdir(data_path)}
#
#     idx = 0
#     loop_cnt = 0
#     complete = False
#     with pg2.connect(**config) as conn:
#         with conn.cursor() as cur:
#             while not complete:
#                 if loop_cnt >= 5:
#                     return ResponseForm(res=False, msg='Retry too many times.')
#                 try:
#                     (file_name, value) = list(file_list.items())[idx]
#
#                     if os.path.isdir(os.path.join(data_path, file_name)) is False and value is False:
#                         [schema, table, extension] = file_name.split(sep='.')
#                         sep = ',' if extension == 'csv' else '\t'
#                         table_name = '%s.%s' % (schema, table)
#                         sql = 'select count(*) from %s' % table_name
#                         cur.execute(sql)
#                         count = cur.fetchone()[0]
#                         if count == 0:
#                             file_path = os.path.join(data_path, file_name)
#                             with open(file_path, 'r') as f:
#                                 cur.execute('SET search_path TO cnvbase, analysis, history, public')
#                                 cur.copy_from(f, table, sep=sep, null='-99999999999999')
#                                 file_list[file_name] = True
#                                 logger.info(file_name + ' data insert OK.')
#
#                             sql = f"SELECT * FROM information_schema.columns WHERE table_name = '{table}' AND column_name = 'id'"
#                             cur.execute(sql)
#                             row = cur.fetchall()
#                             if len(row) > 0:
#                                 sql = f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), MAX(id)) FROM {table_name}"
#                                 cur.execute(sql)
#                         else:
#                             file_list[file_name] = True
#
#                     if False in file_list.values():
#                         idx += 1
#                         if idx == len(list(file_list.items())):
#                             idx = 0
#                             loop_cnt += 1
#                             logger.info('Retry...')
#                     else:
#                         complete = True
#                 except Exception as msg:
#                     logger.error('failed to initialize cnvbase tables (%s)' % msg)
#                     idx += 1
#                     if idx == len(list(file_list.items())):
#                         idx = 0
#                         loop_cnt += 1
#                         logger.info('Retry...')
#
#     return ResponseForm(res=True)
