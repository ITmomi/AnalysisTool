import os
import datetime
from io import StringIO
import pandas as pd
import psycopg2 as pg2
from config.app_config import *


def get_db_config():
    import configparser
    from config.app_config import DB_CONFIG_PATH

    config = configparser.ConfigParser()
    config.read(DB_CONFIG_PATH)
    try:
        return {
            'dbname': config['DBSETTINGS']['DB_NAME'],
            'user': config['DBSETTINGS']['DB_USER'],
            'host': config['DBSETTINGS']['DB_HOST'],
            'password': config['DBSETTINGS']['DB_PASSWORD'],
            'port': config['DBSETTINGS']['DB_PORT']
        }
    except KeyError:
        return None


def get_datetime(time: str):
    fmt = ['%Y-%m-%d %H:%M:%S', '%Y%m%d%H%M%S', '%Y-%m-%d']
    if time is None:
        return None
    for f in fmt:
        try:
            return datetime.datetime.strptime(time, f)
        except ValueError:
            continue
    return None


def get_date_string(time: datetime.date):
    return time.strftime('%Y-%m-%d %H:%M:%S')


def exist_table(table_name, schema_name='public', config=None):
    try:
        if config is None:
            config = get_db_config()
        sql = f"select exists (select from information_schema.tables \
                where table_name='{table_name}' and table_schema='{schema_name}')"
        with pg2.connect(**config) as connect:
            with connect.cursor() as cursor:
                cursor.execute(sql)
                ret = cursor.fetchone()
                return ret[0]

    except Exception as msg:
        print(f'exist_table exception occurs. {msg}')
        return False


def test_db_connection(config):
    try:
        connect = pg2.connect(**config)
        connect.close()
        return True
    except Exception as msg:
        pass
    return False


def exist_data_from_table(table_name, config=None):
    try:
        if config is None:
            config = get_db_config()
        with pg2.connect(**config) as connect:
            with connect.cursor() as cursor:
                cursor.execute(f"select count(*) from {table_name}")
                _ret = cursor.fetchone()
                return True if _ret[0] > 0 else False
    except:
        pass
    return False


def copy_table(src_config, dst_config, src_schema, dst_schema, table):
    src_tbl = f'{src_schema}.{table}'
    dst_tbl = f'{dst_schema}.{table}'
    if exist_table(table, src_schema, src_config) and exist_table(table, dst_schema, dst_config):
        if exist_data_from_table(src_tbl, src_config) and not exist_data_from_table(dst_tbl, dst_config):
            with pg2.connect(**src_config) as src_conn:
                with src_conn.cursor() as src_cur:
                    src_cur.execute(f"select * from {src_tbl} limit 0")
                    columns = [_[0] for _ in src_cur.description]

                    buffer = StringIO()
                    src_cur.copy_to(buffer, src_tbl, sep='\t', null=NA_VALUE, columns=columns)
                    buffer.seek(0)

                    with pg2.connect(**dst_config) as dst_conn:
                        with dst_conn.cursor() as dst_cur:
                            try:
                                dst_cur.copy_from(buffer, dst_tbl, sep="\t", null=NA_VALUE, columns=columns)
                                return True
                            except (Exception, pg2.DatabaseError) as error:
                                raise RuntimeError(f'..error occurs on copy table. {error}')
    return False
