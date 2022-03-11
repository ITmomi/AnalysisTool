import datetime
import os
import re
import time

import numpy as np
import pandas as pd

import convert.const as val
from enum import Enum, auto
from convert.connector import Connector
from convert.default_logger import DefaultLogger
from convert.sql.tables import get_table_query_list
from convert.util import test_db_connect, get_schema_list, create_schema, exist_table, get_data_from_table, \
    drop_schema, do_query, insert_df, get_table_column_list, drop_table, get_date_from_str, delete_line_end, \
    get_foreign_key


class LogConvert:
    class ConvErr(Enum):
        NOT_DEF_COL_RULE = 0
        DEF_DUP_RULE = auto()
        FAIL_FETCH_LOG_TIME = auto()
        CAST_ERR = auto()
        UNEXPECTED_ERR = auto()

    db_versions = ['2021-4', '2022-1']
    db = dict()  # Database information
    schema = 'cnvbase'  # Schema where all setting tables place.
    connect = None  # Connector
    logger = None   # Logger to print out debugging message.
    convert_db = dict()  # Where converted logs are inserted.
    convert_schema = 'convert'  # Schema where all converting result places.
    convert_connect = None  # Connector
    information_table = 'information'
    extra_pkey = None  # Additional primary keys for converting tables.
    time_recorder_dict = dict()  # To check method performance.
    error_dict = dict()  # Error Dictionary

    # Describe basic restriction for rule item.
    item_form = [
        # key, type, nullable, duplicatable, allows
        ['rule_id', int, False, True, None],
        ['type', str, True, True, val.item_type_list],
        ['name', str, False, False, None],
        ['data_type', str, False, True, val.data_type_list],
        ['output_column', str, True, False, None],
        ['row_index', int, True, True, lambda x: True if int(x) >= 0 else False],
        ['col_index', int, True, True, lambda x: True if int(x) >= 0 else False],
        ['coef', float, True, True, None],
        ['def_type', str, True, True, val.def_type_list],
        ['def_val', str, True, True, None],
        ['unit', str, True, True, None],
        ['prefix', str, True, True, None],
        ['regex', str, True, True, lambda x: LogConvert.test_re(x)],
        ['re_group', int, True, True, None],
        ['skip', bool, True, True, None]
    ]

    data_type_caster = {
        val.data_type_int: lambda data: LogConvert.cast_int(data),
        val.data_type_float: lambda data: LogConvert.cast_float(data),
        val.data_type_text: str,
        val.data_type_varchar_10: str,
        val.data_type_varchar_30: str,
        val.data_type_varchar_50: str,
        val.data_type_timestamp: lambda date: LogConvert.cast_timestamp(date),
        val.data_type_time: lambda time: LogConvert.cast_time(time),
        val.data_type_bool: bool
    }

    filter_handler = {
        val.filter_type_base_sampler: lambda cond, df: LogConvert.filter_base_sampler(cond, df),
        val.filter_type_time_sampler: lambda cond, df: LogConvert.filter_time_sampler(cond, df),
        val.filter_type_custom: lambda cond, df: LogConvert.filter_custom(cond, df),
    }

    err_form = (
        {'msg_f': '{} line is {} columns but {}-columns rule is not defined.'},  # NOT_DEF_COL_RULE
        {'msg_f': 'duplicated rule definitions for {} columns.'},  # DEF_DUP_RULE
        {'msg_f': 'failed to fetch log_time for line {}.'},  # FAIL_FETCH_LOG_TIME
        {'msg_f': '{} cannot be cast to {} of {}.'},  # CAST_ERR
        {'msg_f': 'Unexpected error while converting.'}  # UNEXPECTED_ERR
    )

    def __init__(self, logger=None):
        if logger is None:
            self.logger = DefaultLogger()
        else:
            self.logger = logger

    @staticmethod
    def cast_int(data):
        data = re.sub(r"[^0-9.-]", "", str(data))
        if data == '':
            return None
        data = float(data)
        return int(round(data))

    @staticmethod
    def cast_float(data):
        data = re.sub(r"[^0-9.-]", "", str(data))
        if data == '':
            return None
        return float(data)

    @staticmethod
    def cast_timestamp(date_str):
        if type(date_str) == datetime.datetime:
            return date_str
        ts = get_date_from_str(date_str)
        if ts.year == 1900:
            ts = ts.replace(year=datetime.datetime.now().year)
        return ts

    @staticmethod
    def cast_time(time_str):
        ts = get_date_from_str(time_str)
        return ts.strftime('%H:%M:%S')

    @staticmethod
    def filter_base_sampler(condition, df):
        try:
            step = int(condition)
            df = df[::step]
        except ValueError as msg:
            raise RuntimeWarning(f'failed to do filtering with base-sampler. {msg}')
        return df

    """
    Time sampler. 
    `condition` is consist to (column_name, interval[ms]) format. 
    """
    @staticmethod
    def filter_time_sampler(condition, df):
        condition = [_.strip() for _ in condition.split(',')]
        try:
            column_name, interval = condition[0], int(condition[1])*1000000
            if column_name in df.columns:
                df[column_name] = df[column_name].astype('datetime64')
                out = df.iloc[[0]]
                last = df.iloc[0][column_name]
                for _, elem in df.iterrows():
                    if (elem[column_name]-last).delta >= interval:
                        out = out.append(elem, ignore_index=True)
                        last = elem[column_name]
                return out

        except ValueError as msg:
            raise RuntimeWarning(f'failed to do filtering with time-sampler. {msg}')
        return df

    @staticmethod
    def filter_custom(condition, df):
        _args = ','.join(df.columns)
        out = pd.DataFrame(columns=df.columns)
        for _, elem in df.iterrows():
            if eval(f"lambda {_args}: {condition}")(**elem.to_dict()):
                out = out.append(elem, ignore_index=True)
        return out

    @staticmethod
    def test_re(exp):
        try:
            re.compile(exp)
            return True
        except re.error:
            pass
        return False

    """
    Set database connection information.
    """
    def set_db_config(self, host, port, dbname, user, password):
        self.db = {
            'host': host,
            'port': port,
            'dbname': dbname,
            'user': user,
            'password': password
        }
        self.logger.info('set_db_config| %s' % str(self.db))
        if not test_db_connect(self.db):
            self.logger.error('invalid database (host=%s, port=%d)' % (self.db['host'], self.db['port']))

        try:
            self.connect = Connector(self.db)
        except Exception as ex:
            self.logger.error('database connection failed. msg=%s' % str(ex))

    """
    Add extra primary keys. 
    When the module creates converting table, it add the specific pkey as primary key.  
    """
    def set_extra_pkey(self, pkey: list):
        self.extra_pkey = pkey

    """
    Set database configuration to place converted log data.
    """
    def set_convert_db(self, host, port, dbname, schema, user, password):
        self.convert_db = {
            'host': host,
            'port': port,
            'dbname': dbname,
            'user': user,
            'password': password,
        }
        self.logger.info('set_convert_db| %s' % str(self.convert_db))
        self.convert_schema = schema

        if not test_db_connect(self.convert_db):
            self.logger.error('invalid converting database (host=%s, port=%d)' % (self.db['host'], self.db['port']))

        try:
            self.convert_connect = Connector(self.convert_db)
        except Exception as ex:
            self.logger.error('converting database connection failed. msg=%s' % str(ex))

    """
    Set logger library.
    """
    def set_logger(self, logger):
        self.logger = logger

    """
    Initialize database.
    """
    def init_database(self):
        self.logger.info('convert| init database')

        if not test_db_connect(self.db):
            raise RuntimeError('convert| failed to initialize convert-rule database')
        if not test_db_connect(self.convert_db):
            raise RuntimeError('convert| failed to initialize convert-storage database')

        schemas = get_schema_list(self.db)
        if self.schema not in schemas:
            create_schema(self.db, self.schema)

        schemas = get_schema_list(self.convert_db)
        if self.convert_schema not in schemas:
            create_schema(self.convert_db, self.convert_schema)

        left_work = []
        if exist_table(self.db, self.schema, self.information_table):
            version_info = get_data_from_table(self.db, self.schema, self.information_table, where="key = 'version'")
            if len(version_info) > 0:
                version = version_info[0][1]  # Check the value of first record
                if version not in self.db_versions:
                    left_work = [*self.db_versions]
                else:
                    next_idx = self.db_versions.index(version)+1
                    if next_idx >= len(self.db_versions):
                        self.logger.info(f'convert| database is up-to-date. version={version}')
                    else:
                        left_work = self.db_versions[next_idx:]
        else:
            self.logger.info('no information table')
            left_work = [*self.db_versions]

        # If the database hasn't done any initializing sequence, delete all tables and create tables again.
        if len(left_work) == len(self.db_versions):
            drop_schema(self.db, self.schema)
            do_query(self.db, f"create schema {self.schema}")

        # do the left works
        self.logger.info(f'convert| left works = {".".join(left_work)}')
        for left in left_work:
            self.logger.info(f'convert| update database to version {left}')
            tables = get_table_query_list(self.schema, left)
            for table in tables:
                self.logger.info(f"convert| do query for {table['name']}")
                do_query(self.db, table['sql'])

        self.logger.info('convert| all database update has done.')
        self.update_information('version', self.db_versions[-1])

    def update_information(self, key, value):
        if exist_table(self.db, self.schema, self.information_table):
            info = get_data_from_table(self.db, self.schema, self.information_table, where=f"key = '{key}'")
            if len(info) == 0:
                do_query(self.db, f"insert into {self.schema}.{self.information_table} (key, value) values \
                    ('{key}', '{value}')")
            else:
                do_query(self.db, f"update {self.schema}.{self.information_table} set value = '{value}' \
                    where key = '{key}'")
        else:
            raise RuntimeError('no information table for converter')

    """ 
    Request to convert a file. 
    """
    def convert(self, log_name, file, request_id=None, equipment_name=None, insert_db=True):
        self.logger.info('convert| request convert(log_name=%s file=%s eqp_name=%s)'
                         % (log_name, os.path.basename(file), equipment_name))
        # clear error_dict
        self.error_dict.clear()

        if not os.path.exists(file) or not os.path.isfile(file):
            raise RuntimeError(f"convert| cannot read file({file})")

        log_define = self.connect.get_log_by_name(log_name)
        if log_define is None:
            raise RuntimeError(f'convert| undefined log {log_name}')

        self.logger.info(f"convert| delete old converting errors (log_id={log_define['id']})")
        self.connect.delete_error(log_define['id'], days=30)

        if self.is_ignore_file(log_define, file):
            # Return empty dataframe
            self.logger.info('convert| file %s ignored' % file)
            return pd.DataFrame()

        rules = self.connect.get_rule_list(log_id=log_define['id'])
        if len(rules) == 0:
            raise RuntimeError(f'convert| no rules exist')

        # Check an output table.
        self.create_convert_result_table(log_define)

        now = datetime.datetime.now()
        try:
            output_dict = self.do_convert(log_define, file, request_id, equipment_name, now, insert_db)
        finally:
            # Insert error.
            self.insert_error(log_define['id'], file, equipment_name)
        return output_dict

    def create_convert_result_table(self, log_define):
        rules = self.connect.get_rule_list(log_id=log_define['id'])
        if len(rules) == 0:
            raise RuntimeError('no rules exist')

        # List all output columns from all rules.
        output_column_list = list()

        for rule in rules:
            items = self.connect.get_rule_items_by_id(rule['id'], df=True)
            for item_index in items[items['output_column'] != ''].index:
                item = items.loc[item_index]
                output_column = item['output_column'].lower()
                if output_column not in [o['output_column'] for o in output_column_list]:
                    output_column_list.append({
                        'output_column': output_column,
                        'data_type': item['data_type']
                    })

        if len(output_column_list) == 0:
            raise RuntimeError('all output_column is empty')

        # Define system-wise columns.
        sys_columns = [
            {'output_column': 'equipment_name', 'data_type': "text not null default ''::text"},
            {'output_column': 'log_time', 'data_type': "timestamp not null default now()"},
            {'output_column': 'log_idx', 'data_type': "integer not null default 0"},
            {'output_column': 'request_id', 'data_type': "varchar(50)"},
            {'output_column': 'created_time', 'data_type': "timestamp"}
        ]

        if exist_table(self.convert_db, self.convert_schema, log_define['table_name']):
            # Check If the rows of the output table was changed.
            columns = get_table_column_list(self.convert_db, self.convert_schema, log_define['table_name'])

            # For now on, the module doesn't need equipments table anymore,
            # So, drop equipment_name foreign-key if it exists.
            if 'equipment_name' in columns:
                fk = get_foreign_key(self.convert_db, self.convert_schema, log_define['table_name'])
                if fk is not None:
                    do_query(self.convert_db, f"alter table {self.convert_schema}.{log_define['table_name']} \
                        drop constraint {fk}")
                    self.logger.info('drop equipment_name foreign-key from %s' % log_define['table_name'])

            # We should not drop the table from the fields.
            # If there is differences with 'columns', Add a column without the origin changing.

            defined_column_list = [o['output_column'] for o in output_column_list]
            for _sys in sys_columns:
                if _sys['output_column'] not in defined_column_list:
                    output_column_list.append(_sys)

            diff = list()
            for _column in output_column_list:
                if _column['output_column'] not in columns:
                    diff.append(_column)

            if len(diff) == 0:
                return

            # Add columns
            for _column in diff:
                sql = f"alter table {self.convert_schema}.{log_define['table_name']} \
                    add {_column['output_column']} {_column['data_type']}"
                do_query(self.convert_db, sql)
                self.logger.info(f"column {_column['output_column']} created in {log_define['table_name']}")

            return

        # Create a table.
        appended = [o['output_column'] for o in output_column_list]

        column_sql = list()
        for elem in output_column_list:
            column_sql.append(f"{elem['output_column']} {elem['data_type']}")

        for _sys in sys_columns:
            if _sys['output_column'] not in appended:
                column_sql.append(f"{_sys['output_column']} {_sys['data_type']}")
                appended.append(_sys['output_column'])

        column_sql = ', '.join(column_sql)

        pkey_sql = ['equipment_name', 'log_time', 'log_idx']
        if self.extra_pkey is not None:
            for ex in self.extra_pkey:
                if ex in appended:
                    pkey_sql.append(ex)
        pkey_sql = ', '.join(pkey_sql)

        table_name = f"{self.convert_schema}.{log_define['table_name']}"

        sql = f"create table {table_name} ( \
                {column_sql}, \
                constraint {log_define['table_name']}_prog_pkey \
                    primary key ({pkey_sql}))"
        do_query(self.convert_db, sql)
        self.logger.info(f"output table created ({log_define['table_name']})")

    """
    Converting entrypoint.
    """
    def do_convert(self, log_define, file, request_id, equipment_name, now, insert_db):
        if log_define['input_type'] == 'regex':
            return self.do_convert_regex(log_define, file, request_id, equipment_name, now, insert_db)
        else:
            return self.do_convert_csv(log_define, file, request_id, equipment_name, now, insert_db)

    """
    Convert a regex type log.
    """
    def do_convert_regex(self, log_define, file, request_id, equipment_name, now, insert_db):

        self.stamp(f'start converting [regex] {os.path.basename(file)}')

        rules = self.connect.get_rule_list(log_define['id'], df=True)
        items = self.connect.get_rule_items_by_id(rules['id'][0], df=True)
        if items is None or len(items) == 0:
            raise RuntimeError(f"no items in rule {rules['id'][0]}")

        # Create an empty dataframe to store converting result.
        out_df = self.create_empty_output_df(log_define['table_name'])

        lines = open(file, 'r', encoding='utf-8').read().split('\n')
        if len(lines) == 0:
            self.logger.warn('empty log input')
            return

        output = dict()

        skipped_df = items[items['skip']]
        for skipped_idx in skipped_df.index:
            self.logger.info(f"skipped item {skipped_df.loc[skipped_idx]['name']}")
        del skipped_df

        for item_idx in items.index:
            item = items.loc[item_idx]
            if item['skip'] is not None and item['skip']:
                continue

            # In `method` type, a user defines a method that receives all lines as argument.
            # if item['def_type'] == val.def_type_method:
            #     method_text = '__regex_method_type_exec'
            #     arg_text = 'lines, '+','.join(output.keys())
            #     method_lines = item['def_val'].split('\n')
            #     if len(method_lines) > 0:
            #         method_lines = [f'   {_}' for _ in method_lines]
            #         method_lines.insert(0, f'def {method_text}({arg_text}):')
            #         method_code = '\n'.join(method_lines)
            #         exec(method_code)
            #         output[item['name']] = locals()[method_text](lines, **output)
            #     break

            try:
                if item['prefix'] is not None and item['prefix'] != '':
                    # Parse the log with the item's prefix.
                    for i in range(len(lines)):
                        line = lines[i]
                        if item['prefix'] in line:
                            line_data = line.replace(item['prefix'], '', 1)
                            matches = re.search(item['regex'], line_data)
                            if matches is not None:
                                try:
                                    _cast = self.data_type_caster[item['data_type']]
                                    output[item['name']] = _cast(matches.group(0))
                                except Exception as ex:
                                    err_type = self.ConvErr.CAST_ERR.value
                                    err_msg = self.err_form[err_type]['msg_f'] \
                                        .format(matches.group(0), item['data_type'], item['name'])
                                    self.add_error(err_type, i + 1, line, err_msg)
                                    ex.args = ('[convert:cast (%s, %s)]' % (item['name'], item['data_type']),) + ex.args
                                    raise
                                break

                # Set default value if failed to parse value from the log.
                if item['name'] not in output:
                    try:
                        if item['def_type'] == val.def_type_null:
                            o = None
                        elif item['def_type'] == val.def_type_equipment_name:
                            o = equipment_name
                        elif item['def_type'] == val.def_type_text:
                            o = str(item['def_val'])
                        elif item['def_type'] == val.def_type_filename:
                            o = os.path.basename(file)
                        elif item['def_type'] == val.def_type_now:
                            o = datetime.datetime.now()
                        elif item['def_type'] == val.def_type_custom:
                            try:
                                _args = ', '.join(output.keys())
                                o = eval(f"lambda {_args}: {item['def_val']}")(**output)
                            except Exception as msg:
                                self.logger.warn(f"failed to get custom value from {item['def_val']}\n{msg}")
                                o = None
                    except Exception as ex:
                        ex.args = ('[convert:default (%s, %s)]' % (item['name'], item['def_type']),) + ex.args
                        raise

                    try:
                        _cast = self.data_type_caster[item['data_type']]
                        output[item['name']] = _cast(o)
                    except Exception as ex:
                        ex.args = ('[convert:cast_def (%s, %s)]' % (item['name'], item['data_type']),) + ex.args
                        raise

            except Exception as ex:
                ex.args = ('[convert: failed to parse %s]' % item['name'],) + ex.args
                raise

        # Fill the output dataframe
        out_dict = dict()
        for _, item in items[items['output_column'] != ''].iterrows():
            out_dict[item['output_column']] = output[item['name']]

        out_df = out_df.append(out_dict, ignore_index=True)

        # Insert common information.
        if 'equipment_name' in out_df.columns:
            out_df['equipment_name'] = equipment_name
        if 'request_id' in out_df.columns:
            out_df['request_id'] = request_id
        if 'created_time' in out_df.columns:
            out_df['created_time'] = now
        if 'log_idx' in out_df.columns:
            out_df['log_idx'] = 0

        # There's no need to do filters in regex converting.

        # Insert converted result.
        # if insert_db:
        #     self.stamp(f"insert df into {log_define['table_name']}")
        #     ret = insert_df(self.convert_db, self.convert_schema, log_define['table_name'], out_df)

        self.stamp(f'{os.path.basename(file)} converted. rows={len(out_df)}')

        # if ret:
        return out_df
        # return None

    """
    Insert df that has been converted by this module. 
    """
    def insert_convert_df(self, log_name, df):
        self.logger.info('insert_convert_df| log_name=%s data_len=%d' % (log_name, -1 if df is None else len(df)))
        if df is None or len(df) == 0:
            raise RuntimeWarning(f'insert_convert_df| empty data (log_name=%s)' % log_name)

        log_define = self.connect.get_log_by_name(log_name)
        if log_define is None:
            raise RuntimeError(f'insert_convert_df| undefined log {log_name}')

        table_columns = get_table_column_list(self.convert_db, self.convert_schema, log_define['table_name'])
        miss = list(set(df.columns.to_list()) - set(table_columns))
        if len(miss) > 0:
            raise RuntimeError(f'insert_convert_df| undefined table column %s' % ','.join(miss))

        return insert_df(self.convert_db, self.convert_schema, log_define['table_name'], df, logger=self.logger)

    """
    Create empty output dataframe to insert converted result into the specified table.
    """
    def create_empty_output_df(self, table_name):
        out_columns = get_table_column_list(self.convert_db, self.convert_schema, table_name)
        if 'id' in out_columns:
            out_columns.remove('id')
        return pd.DataFrame([], columns=out_columns)

    """
    Convert a csv type log.
    """
    def do_convert_csv(self, log_define, file, request_id, equipment_name, now, insert_db):

        def set_default(out_dict, item_df):
            self.set_default(out_dict, item_df, equipment_name, file, now)

        bounced = None
        complete_sum = 0

        def lstats(total, progress, spent, last=False):
            nonlocal bounced, complete_sum
            complete_sum += spent

            cur = time.time()
            if last:
                self.logger.info(' %d/%d (avg. %.3f ms, total %.3f ms)' % (total, total, complete_sum / total, complete_sum))
            elif bounced is None or (cur-bounced) > 3:
                self.logger.info(' %d/%d (avg. %.3f ms)' % (progress, total, complete_sum/progress))
                bounced = cur

        self.stamp(f'start converting [csv] {os.path.basename(file)}')

        rules = self.connect.get_rule_list(log_define['id'], df=True)

        # 'item_dict' have 'columns' as a key
        item_dict = dict()

        # A name of 'log_time' column's item name for each column rules.
        log_time_name_dict = dict()

        # Even if the file has various columns,
        # info_item rule must be determined just one among the rules.
        info_rule = None

        # Info data dict
        info_data = dict()

        # Get all item list for each rules.
        for _, rule in rules.iterrows():
            items = self.connect.get_rule_items_by_id(rule['id'], df=True)
            item_dict[rule['col']] = items

            # Find out 'log_time' column
            log_time_item = items[items['output_column'] == 'log_time']
            if len(log_time_item) == 0:
                self.logger.warn('### error no log_time info ###')
                raise RuntimeError(f"no log_time info for {rule['col']} columns")
            log_time_name_dict[rule['col']] = log_time_item['name'].tolist()[0]

        # Get an output column list.
        table_out = self.create_empty_output_df(log_define['table_name'])

        with open(file, 'r') as f:

            # Pre-analyze the file.
            # Look into the first 100 lines to determine order of rule suitability.

            try:
                # Count lines
                total_lines = sum(1 for _ in f)
                f.seek(0)
                self.logger.info(f'total_lines={total_lines}')

                self.stamp('analyze header')

                stats = {
                    'columns': dict(),
                    'header': {'exist': False, 'columns': 0}
                }
                line_idx = 0
                for line in f:
                    if line_idx > 100:
                        break
                    line_idx += 1

                    line = delete_line_end(line).strip()
                    if len(line) == 0:
                        continue

                    li = line.split(',')

                    if line.startswith('#') and info_rule is not None:
                        # If there is a header in the log,
                        # Set info_items to header columns rule.
                        stats['header']['exist'] = True
                        stats['header']['columns'] = len(li)

                        self.logger.info(f'find a header. set info_rule as {len(li)} columns')

                        # Retain only header columns rule.
                        info_rule = item_dict[len(li)] if len(li) in item_dict else None

                    if len(li) not in stats['columns']:
                        stats['columns'][len(li)] = 0
                    stats['columns'][len(li)] += 1

                if info_rule is None:
                    stats['columns'] = {k: v for k, v in sorted(stats['columns'].items(), key=lambda _item: _item[1], reverse=True)}
                    for _key in stats['columns'].keys():
                        if _key in item_dict:
                            info_rule = item_dict[_key]
                            break

                skip_line_list = list()

                if info_rule is not None:
                    info_item_df = info_rule[info_rule['type'] == val.item_type_info]
                    info_row_candidates = info_item_df.drop_duplicates(['row_index'])['row_index'].astype(int).tolist()

                    # Fetch information data first.
                    info_last_row = info_item_df['row_index'].astype(int).max()

                    f.seek(0)
                    line_idx = 0
                    for line in f:
                        line_idx += 1
                        if line_idx > info_last_row:
                            break
                        if line_idx in info_row_candidates:
                            line = delete_line_end(line).strip()
                            if len(line) == 0:
                                continue
                            li = [_.strip() for _ in line.split(',')]

                            # Info candidate row should be considered as Info Line
                            # if len(li) in item_dict:
                            #     self.logger.info(f'line {line_idx} consider data (line_columns={len(li)})')
                            #     continue

                            skip_line_list.append(line_idx)
                            for _idx in info_item_df[info_item_df['row_index'] == line_idx].index:
                                _item = info_item_df.loc[_idx]
                                data_type = _item['data_type']
                                _val = self.typed(li[int(_item['col_index'])-1], data_type)
                                if data_type in val.data_type_numeric_list and _item['coef'] > 0 and _val is not None:
                                    _val = _val * _item['coef']
                                info_data[_item['name']] = _val

                    # When info_data doesn't exist.
                    for item_index in info_item_df.index:
                        item = info_item_df.loc[item_index]
                        if item['name'] not in info_data:
                            set_default(info_data, item)

            except Exception as ex:
                ex.args = ('[analyze_info]',) + ex.args
                raise

            # Start converting.
            try:
                self.stamp('converting lines')
                f.seek(0)
                line_idx = 0

                log_idx = 0
                last_log_time = None
                line_entry_time = time.time()
                t_out_list = []
                for line in f:
                    try:
                        line_idx += 1

                        _line_entry_time = line_entry_time
                        line_entry_time = time.time()
                        lstats(total_lines, line_idx, (line_entry_time - _line_entry_time) * 1000)

                        # Delete a line-end character
                        line = delete_line_end(line.strip())

                        if len(line) == 0:
                            continue

                        # Skip header line(Start with '#')
                        if line.startswith('#'):
                            continue

                        # Split the line and strip all.
                        li = line.split(',')
                        li = [_.strip() for _ in li]

                        columns = len(li)

                        if line_idx in skip_line_list:
                            # This line may be an information row.
                            continue

                        # Find a rule which is the same as the number of the line columns.
                        rule = rules[rules['col'] == columns]
                        if rule is None or len(rule) == 0:
                            err_type = self.ConvErr.NOT_DEF_COL_RULE.value
                            err_msg = self.err_form[err_type]['msg_f'].format(line_idx, columns, columns)
                            self.add_error(err_type, line_idx, line, err_msg)
                            continue
                        if len(rule) > 1:
                            err_type = self.ConvErr.DEF_DUP_RULE.value
                            err_msg = self.err_form[err_type]['msg_f'].format(columns)
                            self.add_error(err_type, line_idx, line, err_msg)
                            continue

                        # Find rule items from database.
                        items = item_dict[columns]

                        # Converting
                        out = {**info_data}

                        # Convert row as headers
                        items_col = items.columns
                        col_index_idx = items_col.get_loc('col_index')
                        def_type_idx = items_col.get_loc('def_type')
                        def_val_idx = items_col.get_loc('def_val')
                        data_type_idx = items_col.get_loc('data_type')
                        coef_idx = items_col.get_loc('coef')
                        name_idx = items_col.get_loc('name')
                        output_column_idx = items_col.get_loc('output_column')
                        skip_idx = items_col.get_loc('skip')

                        try:  # A line converting
                            item_header_df = items[items['type'] == val.item_type_header]
                            item_values = item_header_df.values
                            for item_index in range(item_header_df.shape[0]):

                                # Skip the item if skip column is true
                                if item_values[item_index, skip_idx]:
                                    continue

                                _val = li[item_values[item_index, col_index_idx]-1]
                                if _val is None or _val == '':
                                    if item_values[item_index, def_type_idx] == val.def_type_null:
                                        _val = None
                                    elif item_values[item_index, def_type_idx] == val.def_type_text:
                                        _val = str(item_values[item_index, def_val_idx])
                                    elif item_values[item_index, def_type_idx] == val.def_type_equipment_name:
                                        _val = equipment_name
                                    elif item_values[item_index, def_type_idx] == val.def_type_now:
                                        _val = now
                                    elif item_values[item_index, def_type_idx] == val.def_type_filename:
                                        _val = os.path.basename(file)
                                    elif item_values[item_index, def_type_idx] == val.def_type_custom:
                                        try:
                                            _args = ', '.join(out.keys())
                                            _val = eval(f"lambda {_args}: {item_values[item_index, def_val_idx]}")(**out)
                                        except Exception as msg:
                                            self.logger.warn(f"failed to get custom value from {item_values[item_index, def_val_idx]}\n{msg}")
                                            _val = None

                                # Casting
                                if _val is None:
                                    o = None
                                else:
                                    _cast = self.data_type_caster[item_values[item_index, data_type_idx]]
                                    try:
                                        if item_values[item_index, data_type_idx] in val.data_type_numeric_list:
                                            _val = LogConvert.cast_float(_val)
                                            if item_values[item_index, coef_idx] != 0:
                                                _val = _val * item_values[item_index, coef_idx]
                                        o = _cast(_val)
                                    except Exception as e:
                                        o = None

                                out[item_values[item_index, name_idx]] = o

                            # Convert custom columns
                            item_custom_df = items[items['type'] == val.item_type_custom]
                            item_values = item_custom_df.values
                            for item_index in range(item_custom_df.shape[0]):

                                # Skip the item if skip column is true
                                if item_values[item_index, skip_idx]:
                                    continue

                                if item_values[item_index, def_type_idx] == val.def_type_null:
                                    o = None
                                elif item_values[item_index, def_type_idx] == val.def_type_text:
                                    o = str(item_values[item_index, def_val_idx])
                                elif item_values[item_index, def_type_idx] == val.def_type_equipment_name:
                                    o = equipment_name
                                elif item_values[item_index, def_type_idx] == val.def_type_now:
                                    o = now
                                elif item_values[item_index, def_type_idx] == val.def_type_filename:
                                    o = os.path.basename(file)
                                elif item_values[item_index, def_type_idx] == val.def_type_custom:
                                    try:
                                        _args = ', '.join(out.keys())
                                        o = eval(f"lambda {_args}: {item_values[item_index, def_val_idx]}")(**out)
                                    except Exception as msg:
                                        self.logger.warn(f"failed to get custom value from {item_values[item_index, def_val_idx]}\n{msg}")
                                        o = None
                                try:
                                    out[item_values[item_index, name_idx]] = None if o is None else self.data_type_caster[item_values[item_index, data_type_idx]](o)
                                except ValueError:
                                    # On type casting fail, We fill the output to 'None'.
                                    out[item_values[item_index, name_idx]] = None
                        except Exception as ex:
                            err_type = self.ConvErr.UNEXPECTED_ERR.value
                            err_msg = self.err_form[err_type]['msg_f']
                            self.add_error(err_type, line_idx, line, err_msg)
                            self.logger.warn(f"failed to convert a line %s. msg=%s" % (line, str(ex)))
                            continue

                        # Calculate log_idx.
                        log_time_name = log_time_name_dict[columns]
                        if log_time_name not in out:
                            err_type = self.ConvErr.FAIL_FETCH_LOG_TIME.value
                            err_msg = self.err_form[err_type]['msg_f'].format(line_idx)
                            self.add_error(err_type, line_idx, line, err_msg)
                            continue

                        if out[log_time_name] == last_log_time:
                            log_idx += 1
                        else:
                            log_idx = 0
                        last_log_time = out[log_time_name]

                        # Create output dataframe to insert into table.
                        t_out = dict()
                        item_df = items[items['output_column'] != '']
                        item_values = item_df.values
                        for item_index in range(item_df.shape[0]):
                            if not item_values[item_index, skip_idx]:
                                t_out[item_values[item_index, output_column_idx]] = out[item_values[item_index, name_idx]]

                        if 'log_idx' in table_out.columns:
                            t_out['log_idx'] = log_idx
                        t_out_list.append(t_out)

                    except Exception as ex:  # Catch exceptions over line converting
                        err_type = self.ConvErr.UNEXPECTED_ERR.value
                        err_msg = self.err_form[err_type]['msg_f']
                        self.add_error(err_type, line_idx, line, err_msg)
                        ex.args = (f'[line] {line}',) + ex.args
                        raise

                # Every line has been converted
                lstats(total_lines, total_lines, 0, True)

            except Exception as ex:  # Catch exceptions over converting
                ex.args = ('[convert]',) + ex.args
                raise

        # The end of the file open

        table_out = pd.DataFrame(t_out_list, columns=table_out.columns)
        # Insert common information.
        if 'equipment_name' in table_out.columns:
            table_out['equipment_name'] = equipment_name
        if 'request_id' in table_out.columns:
            table_out['request_id'] = request_id
        if 'created_time' in table_out.columns:
            table_out['created_time'] = now

        # Data type handling
        ref = next(iter(item_dict.values()))
        ref = ref[ref['output_column'] != '']
        ref_values = ref.values
        ref_output_column_list = []
        ref_col = ref.columns
        ref_data_type_idx = ref_col.get_loc('data_type')
        ref_output_column_idx = ref_col.get_loc('output_column')
        for ref_index in range(ref.shape[0]):
            if ref_values[ref_index, ref_data_type_idx] in val.data_type_numeric_list:
                ref_output_column_list.append(ref_values[ref_index, ref_output_column_idx])
        table_out[ref_output_column_list] = table_out[ref_output_column_list].replace({'': None})
        table_out = table_out.replace({np.nan: None})

        # Filtering
        self.stamp('filter')
        filter = self.connect.get_filter_list(log_define['id'])
        if filter is not None and len(filter) > 0:
            filters = self.connect.get_filter_item_list(filter[0]['id'])
            if filters is not None and len(filters) > 0:
                for ft in filters:
                    if ft['type'] in self.filter_handler and self.filter_handler[ft['type']] is not None:
                        table_out = self.filter_handler[ft['type']](ft['condition'], table_out)

        # Insert converted data into table.
        self.stamp(f"insert df into {log_define['table_name']}")
        # ret = True
        # if insert_db:
        #     ret = insert_df(self.convert_db, self.convert_schema, log_define['table_name'], table_out)
        self.stamp(f'{os.path.basename(file)} converted. rows={len(table_out)}')

        # Fixme  2021-10-29 Ted
        #  insert_df() returns False when duplicated pk exists.
        #  And then, this method will also return False.
        #  In this case convert_process considers it failed processing even though converting success.

        # if ret:
        return table_out
        # else:
        #     return None

    def add_error(self, err_type, line_num, line, error_msg):
        if err_type not in self.error_dict:
            self.logger.warn("[{}:{}][{}]".format(line_num, line, error_msg))
            self.error_dict[err_type] = {
                'msg': error_msg,
                'row': line_num,
                'content': line
            }

    def insert_error(self, log_id, file, equipment_name):
        for err_type in self.error_dict:
            self.connect.insert_error(log_id,
                                      os.path.basename(file),
                                      self.error_dict[err_type]['row'],
                                      self.error_dict[err_type]['msg'],
                                      equipment_name,
                                      self.error_dict[err_type]['content'])
        self.error_dict.clear()

    """
    Create a convert preview data.
    It returns a dataframe converted log.
    """
    def create_convert_preview(self, lines: list, rule_items: list):
        items = pd.DataFrame.from_dict(rule_items)
        headers = len(items[items['type'] == val.item_type_header])
        if headers == 0:
            return None

        output_column_list = items[items['output_column'] != '']['output_column'].tolist()
        if len(output_column_list) == 0:
            return None

        output = pd.DataFrame(columns=output_column_list)

        for line in lines:
            # Delete a line-end character
            line = delete_line_end(line)

            if len(line.strip()) == 0:
                return None

            # Skip header line(Start with '#')
            if line.strip().startswith('#'):
                continue

            # Split the line and strip all.
            li = line.split(',')
            li = [_.strip() for _ in li]

            columns = len(li)

            if columns < headers:
                continue

            out = dict()

            # Convert row as headers
            for _, item in items[items['type'] == val.item_type_header].iterrows():
                _val = li[int(item['col_index']) - 1]
                if _val is None or _val == '':
                    o = item['def_val']
                else:
                    _cast = self.data_type_caster[item['data_type']]

                    try:
                        if item['data_type'] in [val.data_type_int, val.data_type_float]:
                            _val = LogConvert.cast_float(_val)
                            if _val is None:
                                raise RuntimeWarning('not numeric')
                            if int(item['coef']) > 0:
                                _val = _val * item['coef']
                        o = _cast(_val)
                    except Exception as e:
                        o = None

                out[item['name']] = o

            # Convert custom columns
            for _, item in items[items['type'] == val.item_type_custom].iterrows():
                if item['def_type'] == val.def_type_null:
                    o = None
                elif item['def_type'] == val.def_type_equipment_name:
                    o = 'equipment_name'
                elif item['def_type'] == val.def_type_now:
                    o = datetime.datetime.now()
                elif item['def_type'] == val.def_type_filename:
                    o = 'filename'
                elif item['def_type'] == val.def_type_custom:
                    try:
                        _args = ', '.join(out.keys())
                        o = eval(f"lambda {_args}: {item['def_val']}")(**out)
                    except Exception as msg:
                        self.logger.warn(f"failed to get custom value from {item['def_val']}\n{msg}")
                        o = None
                # self.data_type_caster[item['data_type']] <---- do this?
                out[item['name']] = o

            # Create output dataframe to insert into table.
            t_out = dict()
            for _, item in items[items['output_column'] != ''].iterrows():
                t_out[item['output_column']] = out[item['name']]
            output = output.append(t_out, ignore_index=True)

        return output

    """
    Create a convert preview data for csv type log.
    """
    def create_convert_preview_df(self, input_df, item_df):
        if (input_df is not None and len(input_df) == 0) or len(item_df) == 0:
            raise RuntimeError('create_convert_preview_df parameter empty')

        # Test validity of items
        report_list = list()
        item_df = item_df.reindex()
        for _, item in item_df.iterrows():
            # item = item_df.loc[item_index]
            report = self.test_rule_item(item, item_df.drop(_))
            if len(report) > 0 or input_df is None:
                report_list += report

        if len(report_list) > 0 or input_df is None:
            return report_list

        now = datetime.datetime.now()

        cols = len(item_df[item_df['type'] == val.item_type_header])

        output_column_list = item_df[(item_df['output_column'].notnull()) & (item_df['output_column'] != '') & (item_df['skip']==False)]['output_column']
        output = pd.DataFrame(columns=output_column_list.tolist())

        info = dict()
        info_item_df = item_df[item_df['type'] == val.item_type_info]
        if len(info_item_df) > 0:
            info_line_list = info_item_df['row_index'].astype(int).tolist()
        else:
            info_line_list = []

        # for i in range(len(info_line_list)):
        #     info_line_list[i] = int(info_line_list[i])

        for item_idx, item in item_df[item_df['type'] == val.item_type_info].iterrows():
            line = input_df.iloc[int(item['row_index']) - 1]
            _val = line[int(item['col_index']) - 1]
            if _val is None or _val == '':
                if item['def_type'] == val.def_type_null:
                    _val = None
                elif item['def_type'] == val.def_type_text:
                    _val = None if item['def_val'] is None else str(item['def_val'])
                elif item['def_type'] == val.def_type_equipment_name:
                    _val = 'Equipment Name'
                elif item['def_type'] == val.def_type_now:
                    _val = now
                elif item['def_type'] == val.def_type_filename:
                    _val = 'File Name'
                elif item['def_type'] == val.def_type_custom:
                    if len(info) > 0:
                        _args = ', '.join(info.keys())
                        _val = eval(f"lambda {_args}: {item['def_val']}")(**info)
                    else:
                        _val = ''
                else:
                    _val = None if item['def_val'] is None else str(item['def_val'])
            else:
                # Rules for information don't have a coefficient.
                _cast = self.data_type_caster[item['data_type']]
                _val = None if _val is None else _cast(_val)
            info[item['name']] = _val

        for line_idx in input_df.index:
            line = input_df.loc[line_idx]

            # Delete a line which starts with '#'
            if str(line[0]).startswith('#'):
                continue

            if (line_idx+1) in info_line_list:
                continue

            if len(line) != cols:
                self.logger.warn(f"create_convert_preview_df| row {line_idx} columns not matched")
                continue

            try:  # Line operation
                out = {**info}

                for item_idx in item_df[item_df['type'] == val.item_type_header].index:
                    item = item_df.loc[item_idx]
                    _val = line[int(item['col_index']) - 1]
                    if _val is None or _val == '':
                        if item['def_type'] == val.def_type_null:
                            o = None
                        elif item['def_type'] == val.def_type_text:
                            o = None if item['def_val'] is None else str(item['def_val'])
                        elif item['def_type'] == val.def_type_equipment_name:
                            o = 'Equipment Name'
                        elif item['def_type'] == val.def_type_now:
                            o = now
                        elif item['def_type'] == val.def_type_filename:
                            o = 'File Name'
                        elif item['def_type'] == val.def_type_custom:
                            _args = ', '.join(out.keys())
                            o = eval(f"lambda {_args}: {item['def_val']}")(**out)
                        else:
                            o = None if item['def_val'] is None else str(item['def_val'])
                    else:
                        if item['data_type'] in val.data_type_numeric_list:
                            if item['coef'] > 0:
                                _val = LogConvert.cast_float(_val)
                                if _val is not None:
                                    _val = float(_val) * item['coef']
                        _cast = self.data_type_caster[item['data_type']]
                        o = None if _val is None else _cast(_val)

                    out[item['name']] = o

                for item_idx in item_df[item_df['type'] == val.item_type_custom].index:
                    item = item_df.loc[item_idx]
                    if item['def_type'] == val.def_type_null:
                        o = None
                    elif item['def_type'] == val.def_type_equipment_name:
                        o = 'equipment_name'
                    elif item['def_type'] == val.def_type_now:
                        o = now
                    elif item['def_type'] == val.def_type_text:
                        o = str(item['def_val'])
                    elif item['def_type'] == val.def_type_filename:
                        o = 'filename'
                    elif item['def_type'] == val.def_type_custom:
                        try:
                            _args = ', '.join(out.keys())
                            o = eval(f"lambda {_args}: {item['def_val']}")(**out)
                        except Exception as msg:
                            self.logger.warn(f"create_convert_preview_df| failed to get custom value from {item['def_val']}\n{msg}")
                            o = None
                    # self.data_type_caster[item['data_type']] <---- do this?
                    out[item['name']] = o

            except Exception as ex:  # Line operation
                self.logger.warn(f"create_convert_preview_df| line {line_idx} converting failed. msg={str(ex)}")
                continue

            t_out = dict()
            for _, item in item_df[item_df['output_column'] != ''][item_df['skip']==False].iterrows():
                if item['output_column'] is not None and item['output_column'] != '':
                    t_out[item['output_column']] = out[item['name']]
            output = output.append(t_out, ignore_index=True)

        return output

    """
    Create a convert preview data for regex type log.
    """
    def create_convert_regex_preview_df(self, input_raw, item_df):
        if (input_raw is not None and len(input_raw) == 0) or len(item_df) == 0:
            raise RuntimeError('create_convert_preview_df parameter empty')

        report_list = list()
        for item_idx in item_df.index:
            item = item_df.loc[item_idx]
            report = self.test_rule_item(item, item_df.drop(item_idx))
            if len(report) > 0:
                report_list += report

        if len(report_list) > 0 or input_raw is None:
            return report_list

        out_items_df = item_df[item_df['output_column'] != '']
        if len(out_items_df) == 0:
            return [{'key': 'output_column', 'reason': 'no output column defined'}]
        out_df = pd.DataFrame(columns=out_items_df['output_column'].tolist())

        lines = input_raw.split('\n')

        output = dict()

        for item_idx in item_df.index:
            item = item_df.loc[item_idx]

            # In `method` type, a user defines a method that receives all lines as argument.
            # if item['def_type'] == val.def_type_method:
            #     method_text = '__regex_method_type_exec'
            #     arg_text = 'lines, ' + ','.join(output.keys())
            #     method_lines = item['def_val'].split('\n')
            #     if len(method_lines) > 0:
            #         method_lines = [f'   {_}' for _ in method_lines]
            #         method_lines.insert(0, f'def {method_text}({arg_text}):')
            #         method_code = '\n'.join(method_lines)
            #         exec(method_code)
            #         output[item['name']] = locals()[method_text](lines, **output)
            #     break

            if item['prefix'] is not None:
                # Parse the log with the item's prefix.
                for i in range(len(lines)):
                    line = lines[i]
                    if item['prefix'] in line:
                        line = line.replace(item['prefix'], '', 1)
                        matches = re.search(item['regex'], line)
                        if matches is not None:
                            _cast = self.data_type_caster[item['data_type']]
                            output[item['name']] = _cast(matches.group(0))
                        break

            # Set default value if failed to parse value from the log.
            if item['name'] not in output:
                if item['def_type'] == val.def_type_null:
                    o = None
                elif item['def_type'] == val.def_type_equipment_name:
                    o = 'equipment_name'
                elif item['def_type'] == val.def_type_text:
                    o = str(item['def_val'])
                elif item['def_type'] == val.def_type_filename:
                    o = 'filename'
                elif item['def_type'] == val.def_type_now:
                    o = datetime.datetime.now()
                elif item['def_type'] == val.def_type_custom:
                    try:
                        _args = ', '.join(output.keys())
                        o = eval(f"lambda {_args}: {item['def_val']}")(**output)
                    except Exception as msg:
                        self.logger.warn(f"failed to get custom value from {item['def_val']}\n{msg}")
                        o = None

                # When creating preview data, the following items are hardcoded,
                # and it's possible to make type-casting exception.
                if item['def_type'] in [val.def_type_filename, val.def_type_equipment_name]:
                    output[item['name']] = o
                    continue

                _cast = self.data_type_caster[item['data_type']]
                output[item['name']] = _cast(o)

        # Fill the output dataframe
        out_dict = dict()
        for item_idx in out_items_df.index:
            item = item_df.loc[item_idx]
            out_dict[item['output_column']] = output[item['name']]

        out_df = out_df.append(out_dict, ignore_index=True)
        return out_df

    """
    Create a filter preview data.
    It returns filtered dataframe.
    """
    def create_filter_preview(self, sample_df, filter_items: list):
        if filter_items is not None and len(filter_items) > 0:
            for ft in filter_items:
                if ft['type'] in self.filter_handler and self.filter_handler[ft['type']] is not None:
                    sample_df = self.filter_handler[ft['type']](ft['condition'], sample_df)

        return sample_df

    def analyze_file_columns(self, file, test=1000):
        with open(file, 'r') as c:
            tested = 0
            ret = dict()
            for line in c:
                if tested > test:
                    break
                c = len(line.split(','))
                if c not in ret:
                    ret[c] = 1
                else:
                    ret[c] += 1
            return sorted(ret.items(), key=lambda item: item[1], reverse=True)
        return None

    def create_undefined_report(self, log_name, file):
        pass

    """
    Get a log definition by log-name.
    """
    def get_log_by_name(self, log_name):
        return self.connect.get_log_by_name(log_name)

    """ 
    Get log list from the specified database. 
    """
    def get_log_list(self):
        return self.connect.get_log_list()

    """
    Get rule list.
    This method can return all rule list in database including uncommitted rules.
    """
    def get_rule_list(self, log_id, committed=True):
        return self.connect.get_rule_list(log_id, committed=committed)

    """
    Get rule items for the specified rule_id
    """
    def get_rule_items(self, rule_id, df=False):
        return self.connect.get_rule_items_by_id(rule_id, df)

    """ Create new log into log_define table. """

    def create_log(self, log_name):
        return self.connect.insert_log(log_name)

    """ 
    Update log information 
    """
    def update_log(self, log_id, log_name=None, input_type=None, table=None, fab=None, tag=None, ignore=None,
                   retention=None, rule_list=None):
        log = self.connect.get_log_by_id(log_id)
        if log is not None:
            # Check input_type is valid.
            if input_type is not None and input_type not in val.input_type_list:
                raise RuntimeError(f"update_log input_type error ({input_type})")

            # Check table_name is valid
            logs = self.connect.get_log_list(df=True)
            logs = logs.drop(logs[logs['log_name'] == log_name].index)
            if logs['table_name'].isin([table]).any():
                raise RuntimeError(f"update_log duplicated table_name error ({table})")

            log = self.connect.update_log(log_id,
                                          log_name=log['log_name'] if log_name is None else log_name,
                                          input_type=log['input_type'] if input_type is None else input_type,
                                          table_name=log['table_name'] if table is None else table,
                                          fab=log['fab'] if fab is None else fab,
                                          tag=log['tag'] if tag is None else tag,
                                          ignore=log['ignore'] if ignore is None else ignore,
                                          retention=log['retention'] if retention is None else retention)

            # When the caller has inputted a rule list, the callee deletes rules which are not in the list.
            if rule_list is not None:
                all_rule_list = self.connect.get_rule_list(log_id=log['id'])
                for rule in all_rule_list:
                    if rule['id'] not in rule_list:
                        self.connect.delete_rule(rule['id'])

            return log

        return None

    """
    Delete a log definition.
    """
    def delete_log(self, log_id):
        log = self.connect.get_log_by_id(log_id)
        if log is None:
            raise RuntimeError(f'invalid log_id {log_id}')
        self.connect.delete_log(log_id)

    """
    Get a rule information 
    """
    def get_rule(self, rule_id):
        return self.connect.get_rule_by_id(rule_id, extra=True)

    """ 
    Create new rule into convert_rule table. 
    """
    def create_rule(self, log_id, rule_name, check_exist=True):
        log = self.connect.get_log_by_id(log_id)
        if log is None:
            raise RuntimeError(f'invalid log_id {log_id}')

        if check_exist:
            rules = self.connect.get_rule_list(log_id, df=True)

            # Check the specified rule name already exists.
            if rules['rule_name'].isin([rule_name]).any():
                raise RuntimeError(f'rule {rule_name} already exists')

        return self.connect.insert_rule(log_id, rule_name)

    """
    Update a rule information.
    Do not confuse with modify_rule() the below.
    """
    def update_rule(self, rule_id, rule_name=None):
        rule = self.connect.get_rule_by_id(rule_id)
        if rule is None:
            return None
        rule = self.connect.update_rule(rule_id,
                                        rule_name=rule['rule_name'] if rule_name is None else rule_name,
                                        commit=False)
        return rule

    """
    Modify a rule.
    It makes a copy from the specified rule-id and use it as temporary storage while modifying process.
    """
    def modify_rule(self, rule_id):
        rule = self.connect.get_rule_by_id(rule_id)
        if rule is None:
            return None
        if not rule['commit']:
            raise RuntimeError(f'uncommitted rule access error (id={rule_id})')

        rule = self.connect.insert_rule(rule['log_id'], rule['rule_name'], rule['col'])
        if rule is not None:
            items = self.connect.get_rule_item_list(rule_id, df=True)

            items = items.drop(['id'], axis=1)
            items['rule_id'] = rule['id']

            for _, elem in items.iterrows():
                self.connect.insert_rule_item(**elem.to_dict())

        return rule

    """
    Commit a rule
    """
    def commit_rule(self, rule_id):
        # If someone set a rule name as that already exists, this method overwrite a rule on the origin.
        rule = self.connect.get_rule_by_id(rule_id)
        if rule is None:
            return None

        # Check if an origin exists.
        origin = self.connect.get_rule_list(rule['log_id'], rule['rule_name'])
        if len(origin) > 0:
            # Delete the origin and overwrite it.
            for ori in origin:
                if ori['id'] != rule['id']:
                    self.connect.delete_rule(ori['id'])

        return self.connect.update_rule(rule_id, rule['rule_name'], True)

    """
    Delete a rule by rule-id.
    """
    def delete_rule(self, rule_id):
        self.connect.delete_rule(rule_id)

    """ 
    Create a new rule item for the specified rule-id.
    It returns 'None' with a testing report on error. 
    """
    def create_rule_item(self, form):
        item = self.connect.insert_rule_item(**form)
        return item

    """
    Update a rule item.
    """
    def update_rule_item(self, form):
        if form is None or 'id' not in form or form['id'] is None:
            raise RuntimeError('update_rule_item invalid item_id')
        item = self.connect.get_rule_item(form['id'])
        if item is None:
            raise RuntimeError('update_rule_item invalid item_id '+form['id'])

        items = self.connect.get_rule_items_by_id(item['rule_id'], df=True)
        items = items[items['id'] != form['id']].reindex()

        reports = self.test_rule_item(form, items)
        if len(reports) > 0:
            return None, reports

        return self.connect.update_rule_item(**form)

    """
    Test if the argument is correctly composed.
    """
    def test_rule_item(self, form, items=None):

        def report(key, reason):
            return {'name': form['name'], 'key': key, 'reason': reason}

        if items is None:
            items = self.connect.get_rule_items_by_id(form['rule_id'], df=True)

        reports = list()

        if form['name'] is None:
            reports.append(report('name'), 'item must have a name')

        if form['name'] is not None and form['name'].count(' ') > 0:
            reports.append(report('name', 'space is forbidden'))

        if form['output_column'] != 'log_time' and 'log_time' not in items['output_column'].tolist():
            reports.append(report('output_column', 'output table must have log_time column'))

        for test in self.item_form:
            k = test[0]

            if k not in form or form[k] is None or (str(form[k])).strip() == '':
                # Check nullable
                if not test[2]:
                    reports.append(report(k, 'empty value'))
            else:
                # Check duplicatable
                if not test[3] and items[k].isin([form[k]]).any():
                    reports.append(report(k, 'value already exists'))

                # Check allows
                if test[4] is not None:
                    if type(test[4]) == list:
                        if form[k] not in test[4]:
                            reports.append(report(k, 'out of range'))
                    elif callable(test[4]) and test[4].__name__ == '<lambda>':
                        # Check type matched
                        try:
                            test[1](form[k])
                            if not test[4](form[k]):
                                reports.append(report(k, 'out of range'))
                        except ValueError:
                            reports.append(report(k, 'type unmatched'))

        if form['def_type'] == val.def_type_custom and 'def_val' in form and form['def_val'].strip() != '':
            try:
                _args = ', '.join(items['name'].to_list())
                exec(f"__def_custom = lambda {_args}: {form['def_val']}")
            except Exception as msg:
                reports.append(report('def_type', f'exec_error: {msg}'))

        return reports

    """
    Delete a rule item.
    """
    def delete_rule_item(self, item_id):
        self.connect.delete_rule_item(item_id)

    """
    This method supply a empty dict object to be used in rule_item methods.
    """
    def get_rule_item_form(self):
        form = dict()
        for key in self.item_form:
            form[key[0]] = None
        return form

    """
    Create a filter for log_id.
    (Optional, if clone is True) If there exists a filter, it creates a filter and copies all item from the exist. 
    """
    def create_filter(self, log_id, clone=True):
        filter = self.connect.insert_filter(log_id)

        # Find a committed filter by log-id.
        if clone:
            filter_list = self.connect.get_filter_list(log_id)
            if filter_list is not None and len(filter_list) > 0:
                items = self.connect.get_filter_item_list(filter_list[0]['id'])
                for item in items:
                    item.pop('id')
                    item['filter_id'] = filter['id']
                    self.create_filter_item(**item)

        return filter

    """
    Get filter list by log-id.
    """
    def get_filter_list(self, log_id, commit_only=True):
        return self.connect.get_filter_list(log_id, committed=commit_only)

    """
    Get a filter by filter-id.
    """
    def get_filter(self, filter_id):
        return self.connect.get_filter(filter_id)

    """
    Commit a filter.
    """
    def commit_filter(self, filter_id):
        filters = self.connect.get_filter_list(committed=False, df=True)
        target = filters[filters['id'] == filter_id]
        if target is None or len(target) == 0:
            raise RuntimeError(f'invalid filter-id {filter_id}')
        log_filters = filters[filters['log_id'] == int(target['log_id'])]
        if len(log_filters) > 1:
            ret = dict()
            for _, elem in log_filters.iterrows():
                if elem['id'] != filter_id:
                    if elem['commit']:
                        self.connect.delete_filter(elem['id'])
                else:
                    ret = self.connect.update_filter(elem['id'], True)
            return ret
        else:
            return self.connect.update_filter(filter_id, True)

    """
    Delete a filter.
    """
    def delete_filter(self, filter_id):
        self.connect.delete_filter(filter_id)

    """
    Get filter items by the specified filter-id.
    """
    def get_filter_items(self, filter_id):
        return self.connect.get_filter_item_list(filter_id)

    """
    Create a new filter item for the specified filter-id.
    """
    def create_filter_item(self, filter_id, name, type, condition):
        items = self.connect.get_filter_item_list(filter_id, df=True)
        if len(items[items['name'] == name]) > 0:
            raise RuntimeError(f'failed to create filter item {name}')
        if type not in val.filter_type_list:
            raise RuntimeError(f'invalid filter type {type}')
        return self.connect.insert_filter_item(filter_id, name, type, condition)

    """
    Delete a filter item.
    """
    def delete_filter_item(self, item_id):
        self.connect.delete_filter_item(item_id)

    """
    Determine a representative log name.
    First off, it will find a log name from log_define_master.name and then,
    from log_define_master.tag. 
    """
    def determine_log_name(self, log_name):
        log = self.connect.get_log_by_name(log_name)
        if log is not None:
            return log['log_name']

        log_list = self.connect.get_log_list()
        for log in log_list:
            if log_name in log['tag']:
                return log['log_name']

        return None

    """
    
    """
    def get_table_backup_df(self):
        table_dict = {
            'log_define_master': self.connect.get_log_define_df(),
            'convert_rule': self.connect.get_convert_rule_df(),
            'convert_rule_item': self.connect.get_convert_item_df(),
            'convert_filter_rule': self.connect.get_filter_rule_df(),
            'convert_filter_rule': self.connect.get_filter_item_df(),
            'convert_error': self.connect.get_convert_error_df()
        }
        return table_dict

    def restore_table(self, table_dict):
        if 'log_define_master' in table_dict:
            self.connect.restore_log_define(table_dict['log_define_master'])

            if 'convert_rule' in table_dict:
                self.connect.restore_convert_rule(table_dict['convert_rule'])
                if 'convert_rule_item' in table_dict:
                    self.connect.restore_convert_item(table_dict['convert_rule_item'])

            if 'convert_filter' in table_dict:
                self.connect.restore_filter(table_dict['convert_filter'])
                if 'convert_filter_item' in table_dict:
                    self.connect.restore_filter_item(table_dict['convert_filter_item'])

            if 'convert_error' in table_dict:
                self.connect.restore_convert_error(table_dict['convert_error'])
        return True

    def typed(self, data, typ):
        handler = self.data_type_caster[typ]
        if typ in val.data_type_numeric_list:
            if data is None:
                return None
            return handler(data)
        else:
            ret = handler(data)
            if ret is None:
                return ''
            return handler(data)

    def set_default(self, out_dict, item_df, equipment_name, file, now):
        if item_df['name'] not in out_dict:
            if item_df['def_type'] == val.def_type_null:
                o = None
            elif item_df['def_type'] == val.def_type_text:
                o = str(item_df['def_val'])
            elif item_df['def_type'] == val.def_type_equipment_name:
                o = equipment_name
            elif item_df['def_type'] == val.def_type_now:
                o = now
            elif item_df['def_type'] == val.def_type_filename:
                o = os.path.basename(file)
            elif item_df['def_type'] == val.def_type_custom:
                try:
                    _args = ', '.join(out_dict.keys())
                    o = eval(f"lambda {_args}: {item_df['def_val']}")(**out_dict)
                except Exception as msg:
                    self.logger.warn(f"failed to get custom value from {item_df['def_val']}\n{msg}")
                    o = None
            out_dict[item_df['name']] = o

        try:
            out_dict[item_df['name']] = self.typed(out_dict[item_df['name']], item_df['data_type'])
        except ValueError:
            # On type casting fail, We fill the output to 'None'.
            out_dict[item_df['name']] = None

    """
    Create an error report for the specified log.  
    @Deprecated
    """
    def summary_convert_error(self, log_id):
        error = self.connect.get_error(log_id)
        msg_list = list()
        for err in error:
            if err['msg'] not in msg_list:
                msg_list.append(err['msg'])
        return msg_list

    """
    Get an error list by log-id
    """
    def get_error_list(self, log_id):
        errors = self.connect.get_error(log_id)
        for err in errors:
            if 'created' in err:
                err['created'] = err['created'].strftime('%Y-%m-%d %H:%M:%S')
        return errors

    """
    Clear convert error in database by log-id
    """
    def clear_error(self, log_id):
        self.connect.clear_error(log_id)

    """
    It tests if the filename includes the ignore_pattern of defined log.
    """
    def is_ignore_file(self, log_define, filename):
        if 'ignore' not in log_define or log_define['ignore'] == '':
            return False
        ignores = [p.strip() for p in log_define['ignore'].split(',') if p != '']
        for p in ignores:
            if filename.endswith(p):
                return True
        return False

    """
    Purge the old converted data.
    """
    def purge_convert_data(self, equipment_list):
        log_list = self.connect.get_log_list()

        for log in log_list:
            self.logger.info('purge| %s (table=%s retention=%d)'
                             % (log['log_name'], log['table_name'], log['retention']))
            if log['retention'] < 1:
                continue

            if not exist_table(self.convert_db, self.convert_schema, log['table_name']):
                self.logger.warn("purge| %s table doesn't exist'" % log['table_name'])
                continue

            date_from = datetime.date.today() - datetime.timedelta(log['retention'])

            column_list = get_table_column_list(self.convert_db, self.convert_schema, log['table_name'])
            if 'log_time' not in column_list or 'equipment_name' not in column_list:
                self.logger.warn("purge| %s doesn't have log_time, equipment_name column. skip purging"
                                 % log['table_name'])
                continue

            where = "and equipment_name in (%s)" % ','.join([f'\'{e}\'' for e in equipment_list])

            sql = f"delete from {log['table_name']} where log_time < '{date_from}' {where}"
            do_query(self.convert_db, sql)
            self.logger.info('purge| query=%s' % sql)

    def stamp(self, msg):
        t = datetime.datetime.now()
        self.logger.info(f"## {t.strftime('%Y-%m-%d %H:%M:%S')} : {msg}")

    def recoder_decorator(self, func):
        def wrapper(*args, **kwargs):
            self.time_recorder_dict[func.__name__] = list()
            ret = func(*args, **kwargs)
            self.time_recorder_dict[func.__name__] = None
        return wrapper
