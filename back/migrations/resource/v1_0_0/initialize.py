import os
from dao import get_dbinfo
import psycopg2 as pg2
import logging
from config import app_config

logger = logging.getLogger(app_config.LOG)

SCHEMA_SETTINGS = 'settings'
SCHEMA_CONVERT = 'convert'
SCHEMA_ANALYSIS = 'analysis'
SCHEMA_PUBLIC = 'public'
SCHEMA_CNVBASE = 'cnvbase'
SCHEMA_CNVSET = 'cnvset'
SCHEMA_LIST = [SCHEMA_PUBLIC, SCHEMA_CNVBASE, SCHEMA_SETTINGS, SCHEMA_CONVERT, SCHEMA_ANALYSIS, SCHEMA_CNVSET]


def init_db_v1_0_0():
    init_schema()
    init_type()
    init_table()
    init_data()


def init_schema(**kwargs):
    config = get_dbinfo(**kwargs)
    try:
        with pg2.connect(**config) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                # DBの全体Schema目録獲得
                cur.execute('select nspname from pg_catalog.pg_namespace')
                rows = cur.fetchall()

                # Schema生成
                for item in SCHEMA_LIST:
                    if (item,) not in rows:
                        cur.execute('create schema %s' % item)
                        logger.info(item + ' schema is created!!')
    except Exception as e:
        logger.info('table create error!')
        logger.info(str(e))


def init_type(**kwargs):
    config = get_dbinfo(**kwargs)
    try:
        with pg2.connect(**config) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                sql_path = 'migrations/resource/v1_0_0/sql/type'
                for file_name in os.listdir(sql_path):
                    if os.path.isdir(os.path.join(sql_path, file_name)) is False:
                        [schema, type_name, extension] = file_name.split(sep='.')
                        cur.execute("SELECT EXISTS "
                                    "(SELECT FROM pg_type WHERE typname='%s')"
                                    % type_name)

                        rows = cur.fetchone()
                        if rows[0] is False:
                            file_path = os.path.join(sql_path, file_name)
                            cur.execute(open(file_path, 'r').read())
                            logger.info(schema + '.' + type_name + ' type is created!!')
    except Exception as e:
        logger.info('table create error!')
        logger.info(e)


def init_table(**kwargs):
    config = get_dbinfo(**kwargs)
    try:
        with pg2.connect(**config) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                # Table生成
                sql_path = 'migrations/resource/v1_0_0/sql/table'
                for file_name in os.listdir(sql_path):
                    if os.path.isdir(os.path.join(sql_path, file_name)) is False:
                        [schema, table_name, extension] = file_name.split(sep='.')

                        cur.execute("SELECT EXISTS "
                                    "(SELECT FROM information_schema.tables WHERE table_schema='%s' AND table_name='%s')"
                                    % (schema, table_name))

                        rows = cur.fetchone()
                        if rows[0] is False:
                            file_path = os.path.join(sql_path, file_name)
                            cur.execute(open(file_path, 'r').read())
                            logger.info(schema + '.' + table_name + ' table is created!!')

                            if table_name == 'management_setting':
                                # Insert Management Setting Info
                                query = '''
                                                    insert into settings.management_setting(target, host, username, password, dbname, port) 
                                                    values(%s, %s, %s, %s, %s, %s)
                                                '''
                                record = ('local', config['host'], config['user'], config['password'], config['dbname'], config['port'])
                                cur.execute(query, record)

                                query = '''
                                                    insert into settings.management_setting(target, host, username, password, dbname, port) 
                                                    values('remote', null, null, null, null, null)
                                                '''
                                cur.execute(query)

                            elif table_name == 'information':
                                query = 'insert into settings.information(key, value) values(%s, %s)'
                                record = ('version', '1.0.0')
                                cur.execute(query, record)

    except Exception as e:
        logger.info('table create error!')
        logger.info(e)


def init_data(**kwargs):
    config = get_dbinfo(**kwargs)
    data_path = './migrations/resource/v1_0_0/data'
    # tables = ['cnvbase.equipment_types', 'cnvbase.equipments', 'cnvbase.log_define', 'cnvbase.convert_columns_define']

    file_list = {file_name: False for file_name in os.listdir(data_path)}

    idx = 0
    loop_cnt = 0
    complete = False
    while not complete:
        if loop_cnt >= 5:
            logger.info('Retry too many times.')
            return
        try:
            with pg2.connect(**config) as conn:
                with conn.cursor() as cur:
                    (file_name, value) = list(file_list.items())[idx]

                    if os.path.isdir(os.path.join(data_path, file_name)) is False and value is False:
                        [schema, table, extension] = file_name.split(sep='.')
                        sep = ',' if extension == 'csv' else '\t'
                        table_name = '%s.%s' % (schema, table)
                        sql = 'select count(*) from %s' % table_name
                        cur.execute(sql)
                        count = cur.fetchone()[0]
                        if count == 0:
                            file_path = os.path.join(data_path, file_name)
                            with open(file_path, 'r') as f:
                                cur.copy_from(f, table_name, sep=sep, null='-99999999999999')
                                file_list[file_name] = True
                                logger.info(file_name + ' data insert OK.')
                        else:
                            file_list[file_name] = True

            if False in file_list.values():
                idx += 1
                if idx == len(list(file_list.items())):
                    idx = 0
                    loop_cnt += 1
                    logger.info('Retry...')
            else:
                complete = True
        except Exception as msg:
            logger.info('failed to initialize cnvbase tables (%s)' % msg)
            idx += 1
            if idx == len(list(file_list.items())):
                idx = 0
                loop_cnt += 1
                logger.info('Retry...')