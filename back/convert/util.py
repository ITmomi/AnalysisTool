import datetime

import psycopg2
import psycopg2 as pg2
import pandas as pd
from sqlalchemy import create_engine

from convert.default_logger import DefaultLogger
from convert.pg_datasource import Connect


def get_date_from_str(date_str: str):
    fmt = [
        '%Y-%m-%d %H:%M:%S',
        '%Y/%m/%d %H:%M:%S',
        '%Y-%m-%d',
        '%m/%d %H:%M:%S',
        '%Y/%m/%d',
        '%H:%M:%S',
        '%Y%m%d%H%M%S',
        '%Y/%m/%d %H%M%S%f'
    ]
    if date_str is None:
        raise RuntimeError('get_date_from_str: date_str is null')
    for f in fmt:
        try:
            return datetime.datetime.strptime(date_str, f)
        except ValueError:
            continue
    return None


def test_db_config(config):
    if 'host' in config and 'port' in config and 'dbname' in config and 'user' in config and 'password' in config:
        return True
    return False


def test_db_connect(config):
    if test_db_config(config):
        try:
            c = pg2.connect(**config, connect_timeout=1)
            c.close()
            return True
        except Exception:
            pass
    return False


def get_schema_list(config, column=False):
    with Connect(config, column=column) as c:
        c.cursor.execute('select nspname from pg_catalog.pg_namespace')
        ret = c.cursor.fetchall()
        if ret is None:
            return list()
        if column:
            return [dict(_) for _ in ret] if column else ret
        else:
            return [_[0] for _ in ret]


def create_schema(config, schema):
    with Connect(config) as c:
        c.cursor.execute(f'create schema {schema}')


def exist_table(config, schema, table):
    with Connect(config) as c:
        c.cursor.execute(f"select exists (select from information_schema.tables where table_name='{table}' and table_schema = '{schema}')")
        ret = c.cursor.fetchone()
        return ret[0]
    return False


def get_table_column_list(config, schema, table):
    with Connect(config) as c:
        c.cursor.execute(f"select column_name from information_schema.columns \
            where table_schema = '{schema}' and table_name = '{table}'")
        ret = c.cursor.fetchall()
        return [_[0] for _ in ret]


def drop_schema(config, schema):
    with Connect(config) as c:
        c.cursor.execute(f"drop schema {schema} cascade")
        return
    raise RuntimeError(f'failed to drop schema {schema}')


def drop_table(config, schema, table):
    with Connect(config) as c:
        c.cursor.execute(f"drop table {schema}.{table} cascade")
        return
    raise RuntimeError(f'failed to drop table {schema}.{table}')


def do_query(config, sql):
    with Connect(config) as c:
        c.cursor.execute(sql)
        return
    raise RuntimeError(f'failed to query ({sql})')


def get_foreign_key(config, schema, table):
    sql = f"select constraint_name from information_schema.table_constraints \
        where constraint_type = 'FOREIGN KEY' and table_name = '{table}' and table_schema = '{schema}'"
    with Connect(config) as c:
        c.cursor.execute(sql)
        ret = c.cursor.fetchone()
        if ret is not None:
            ret = ret[0]
        return ret
    raise RuntimeError(f'failed to get_foreign_key ({sql})')


def insert_df(config, schema, table, df, logger=DefaultLogger()):
    try:
        with Connect(config) as c:
            data_values = df.values
            df_columns = df.columns
            for idx in range(df.shape[0]):
                field_list = list()
                value_list = list()
                for key_idx in range(df.shape[1]):
                    if data_values[idx, key_idx] is None:
                        continue
                    field_list.append(df_columns[key_idx])
                    if pd.api.types.is_numeric_dtype(type(data_values[idx, key_idx])):
                        value = f"{data_values[idx, key_idx]}"
                    else:
                        value = f"'{data_values[idx, key_idx]}'"
                    value_list.append(value)

                if len(field_list) > 0:
                    try:
                        c.cursor.execute(f"insert into {schema}.{table} ({','.join(field_list)}) \
                            values ({','.join(value_list)})")
                    except psycopg2.Error as ex:
                        if ex.pgcode == '23505':  # Unique-Violation error
                            logger.warn('insert_df| unique-violation: %s' % (str(ex).replace('\n', '\t')))
                            c.connect.rollback()
                            continue
                        elif ex.pgcode == '23502':  # NotNull-Violation error
                            logger.warn('insert_df| notnull-violation: %s' % (str(ex).replace('\n', '\t')))
                            c.connect.rollback()
                            continue
                        raise
        return True
    except Exception as ex:
        logger.error('insert_df| exception occurs (schema=%s, table=%s) msg=%s' % (schema, table, str(ex)))
        return False
    """
    engine = create_engine(f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['dbname']}")
    try:
        df.to_sql(table, engine, schema=schema, if_exists='append', index=False, )
        return True
    except Exception as msg:
        print(msg)
        return False
    """


def get_data_from_table(config, schema, table, where=None, column=False, df=False):
    with Connect(config, column=column) as c:
        extra = "" if where is None else f"where {where}"
        sql = f"select * from {schema}.{table} {extra}"
        if df:
            ret = pd.read_sql(c.connect, sql)
            if ret is None:
                return pd.DataFrame()
            return ret
        else:
            c.cursor.execute(sql)
            ret = c.cursor.fetchall()
            if ret is None:
                return list()
            if column:
                return [dict(_) for _ in ret]
            else:
                return ret
    raise RuntimeError(f"get_data_from_table failed to create connection. (table={schema}.{table} where={where})")


def delete_line_end(line):
    while True:
        if len(line) > 1 and (line[-1] == '\r' or line[-1] == '\n'):
            line = line[0:-1]
            continue
        break
    return line
