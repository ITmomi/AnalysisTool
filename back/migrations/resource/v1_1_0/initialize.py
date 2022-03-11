import os
import psycopg2 as pg2
import convert as lc
import pandas as pd
from dao import DAOBaseClass, get_dbinfo
import io
import logging
from config import app_config

logger = logging.getLogger(app_config.LOG)

SCHEMA_SETTINGS = 'settings'
SCHEMA_CONVERT = 'convert'
SCHEMA_ANALYSIS = 'analysis'
SCHEMA_PUBLIC = 'public'
SCHEMA_CNVBASE = 'cnvbase'
SCHEMA_CNVSET = 'cnvset'
SCHEMA_HISTORY = 'history'
SCHEMA_DELETE_LIST = [SCHEMA_ANALYSIS, SCHEMA_CNVBASE, SCHEMA_CONVERT]
SCHEMA_CREATE_LIST = [SCHEMA_ANALYSIS, SCHEMA_CNVBASE, SCHEMA_CONVERT, SCHEMA_HISTORY]
APP_VERSION = '1.1.0'


def init_db_v1_1_0():
    dao = DAOBaseClass()
    dao.drop_tables(schema_list=SCHEMA_DELETE_LIST)

    config = get_dbinfo()

    cnvbase_tables = get_table_query_list(schema='cnvbase')
    for table in cnvbase_tables:
        logger.info(f"create table {table['name']}")
        with pg2.connect(**config) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(table['sql'])

    init_schema()
    init_type()
    init_table()
    init_data()

    with pg2.connect(**config) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute('alter table cnvset.working_logs alter column equipment_names drop not null')
            cur.execute(f"insert into settings.information(key, value) values('cnv_schema_ver', '1.1.0')")
            cur.execute(f"update settings.information set value='{APP_VERSION}' where key='version'")


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
                for item in SCHEMA_CREATE_LIST:
                    if (item,) not in rows:
                        cur.execute('create schema %s' % item)
                        logger.info(item + ' schema is created!!')
    except Exception as e:
        logger.info('schema create error!')
        logger.info(e)


def init_type(**kwargs):
    config = get_dbinfo(**kwargs)
    try:
        with pg2.connect(**config) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                sql_path = 'migrations/resource/v1_1_0/sql/type'
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
        logger.info('type create error!')
        logger.info(e)


def init_table(**kwargs):
    config = get_dbinfo(**kwargs)
    sql_path = 'migrations/resource/v1_1_0/sql/table'
    file_list = {file_name: False for file_name in os.listdir(sql_path)}

    idx = 0
    loop_cnt = 0
    complete = False
    while not complete:
        if loop_cnt >= 5:
            logger.info('Retry too many times.')
            return
        try:
            with pg2.connect(**config) as conn:
                conn.autocommit = True
                with conn.cursor() as cur:
                    (file_name, value) = list(file_list.items())[idx]

                    # Table生成
                    if os.path.isdir(os.path.join(sql_path, file_name)) is False and value is False:
                        [schema, table_name, extension] = file_name.split(sep='.')

                        cur.execute("SELECT EXISTS "
                                    "(SELECT FROM information_schema.tables WHERE table_schema='%s' AND table_name='%s')"
                                    % (schema, table_name))

                        rows = cur.fetchone()
                        if rows[0] is False:
                            file_path = os.path.join(sql_path, file_name)
                            cur.execute(open(file_path, 'r').read())
                            logger.info(schema + '.' + table_name + ' table is created!!')

                        file_list[file_name] = True

            if False in file_list.values():
                idx += 1
                if idx == len(list(file_list.items())):
                    idx = 0
                    loop_cnt += 1
                    logger.info('Retry...')
            else:
                complete = True

        except Exception as e:
            logger.info('table create error!')
            logger.info(e)
            idx += 1
            if idx == len(list(file_list.items())):
                idx = 0
                loop_cnt += 1
                logger.info('Retry...')


def init_data(file=None, **kwargs):
    config = get_dbinfo(**kwargs)

    try:
        if file is None:
            path = 'migrations/resource/v1_1_0/data/initial_data.xlsx'
            if not os.path.exists(path):
                logger.info(f'{path} does not exist')
                return

            xl = pd.ExcelFile(path)
        else:
            xl = pd.ExcelFile(file)
    except Exception as e:
        logger.info(str(e))
        return

    sheet_dict = {tb_name: False for tb_name in xl.sheet_names}
    sheet_list = xl.sheet_names

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
                    table_name = sheet_list[idx]
                    [schema, table] = table_name.split(sep='.')
                    sql = 'select count(*) from %s' % table_name
                    cur.execute(sql)
                    count = cur.fetchone()[0]
                    if count == 0:
                        buf = io.StringIO()
                        df = xl.parse(sheet_name=table_name, header=None, na_filter=False)
                        df.to_csv(buf, sep='\t', header=False, index=False)
                        buf.seek(0)
                        cur.copy_from(buf, table_name, sep='\t', null='-99999999999999')
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
            logger.info('failed to initialize cnvbase tables (%s)' % msg)
            idx += 1
            if idx == len(list(sheet_dict.items())):
                idx = 0
                loop_cnt += 1
                logger.info('Retry...')


def get_table_query_list(schema='public'):
    dependency = ['log_define_master', 'convert_rule', 'convert_rule_item', 'convert_filter',
                  'convert_filter_item', 'convert_error', 'information']
    cur = 'migrations/resource/v1_1_0/sql/cnvbase_table'
    files = [os.path.join(cur, _) for _ in os.listdir(cur)]
    lst = dict()
    for file in files:
        if os.path.isfile(file) and file.endswith('.sql'):
            with open(file) as f:
                sql = f.read()
                sql = sql.replace('__schema__', schema)
                lst[os.path.basename(file).replace('.sql', '')] = sql

    ret = []
    for order in dependency:
        if order not in lst:
            raise RuntimeError('failed to create table query')
        ret.append({'name': order, 'sql': lst[order]})
    return ret