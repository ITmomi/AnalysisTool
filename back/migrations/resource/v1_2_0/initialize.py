import os
import psycopg2 as pg2
from dao.dao_base import DAOBaseClass
from dao import get_dbinfo
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
SCHEMA_GRAPH = 'graph'
SCHEMA_DELETE_LIST = [SCHEMA_ANALYSIS, SCHEMA_CNVBASE, SCHEMA_HISTORY, SCHEMA_SETTINGS]
SCHEMA_CREATE_LIST = [SCHEMA_GRAPH]

TBL_SETTINGS_INFORMATION = 'settings.information'

RESOURCE_PATH = 'migrations/resource/v1_2_0'
RSC_SYSTEM_GRAPH_SCRIPT = 'script/system_graph_script.js'

##########################################################################
# Public Schema Table Data
##########################################################################
analysis_type = ['setting', 'script', 'none']
source_type = ['local', 'remote', 'sql']
APP_VERSION = '1.2.0'

##########################################################################
# Schema Version
# - Each version of table structure changed.
##########################################################################
CNV_SCHEMA_VER = '1.1.0'
CNV_SCHEMA_KEY = 'cnv_schema_ver'

ANALYSIS_SCHEMA_VER = '1.2.0'
ANALYSIS_SCHEMA_KEY = 'analysis_schema_ver'

HIS_SCHEMA_VER = '1.2.0'
HIS_SCHEMA_KEY = 'his_schema_ver'

CNVSET_SCHEMA_VER = '1.2.0'
CNVSET_SCHEMA_KEY = 'cnvset_schema_ver'

PUBLIC_SCHEMA_VER = '1.2.0'
PUBLIC_SCHEMA_KEY = 'public_schema_ver'

SETTINGS_SCHEMA_VER = '1.2.0'
SETTINGS_SCHEMA_KEY = 'settings_schema_ver'

GRAPH_SCHEMA_VER = '1.2.0'
GRAPH_SCHEMA_KEY = 'graph_schema_ver'

schema_ver_key_list = [
        {'version': PUBLIC_SCHEMA_VER,      'key': PUBLIC_SCHEMA_KEY,   'schem_name': SCHEMA_PUBLIC},
        {'version': ANALYSIS_SCHEMA_VER,    'key': ANALYSIS_SCHEMA_KEY, 'schem_name': SCHEMA_ANALYSIS},
        {'version': CNVSET_SCHEMA_VER,      'key': CNVSET_SCHEMA_KEY,   'schem_name': SCHEMA_CNVSET},
        {'version': HIS_SCHEMA_VER,         'key': HIS_SCHEMA_KEY,      'schem_name': SCHEMA_HISTORY},
        # {'version': CNV_SCHEMA_VER,         'key': CNV_SCHEMA_KEY,      'schem_name': SCHEMA_CONVERT},
        {'version': SETTINGS_SCHEMA_VER,    'key': SETTINGS_SCHEMA_KEY, 'schem_name': SCHEMA_SETTINGS},
        {'version': GRAPH_SCHEMA_VER,       'key': GRAPH_SCHEMA_KEY,    'schem_name': SCHEMA_GRAPH}
    ]


def init_db_v1_2_0():
    dao = DAOBaseClass()

    dao.remove_all_records(schema_list=SCHEMA_DELETE_LIST,
                           omit_tb_list=[TBL_SETTINGS_INFORMATION])

    init_schema()
    init_table()

    config = get_dbinfo()

    with pg2.connect(**config) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            # public schema
            cur.execute(f"update public.calc_type set type='script' where type='custom'")
            cur.execute('alter table graph_type drop column z_axis')
            cur.execute(f"update public.graph_type set type='bar' where type='Bar'")
            cur.execute(f"update public.graph_type set type='line' where type='Line'")
            cur.execute(f"update public.graph_type set type='box plot' where type='Box Plot'")
            cur.execute(f"update public.graph_type set type='density plot' where type='Density Plot'")
            cur.execute(f"update public.graph_type set type='bubble chart' where type='Bubble Chart'")

            # analysis.function
            sql = """
            alter table analysis.function add source_type text not null;
            alter table analysis.function drop column sub_title;
            alter table analysis.function add analysis_type text not null;
            alter table analysis.function drop column btn_msg;
            alter table analysis.function drop column log_name;
            alter table analysis.function drop column show_org;
            
            alter table analysis.function
                add constraint function_analysis_type_type_fk
                    foreign key (analysis_type) references analysis_type (type)
                    on update cascade on delete cascade;
                    
            alter table analysis.function
                add constraint function_source_type_type_fk
                foreign key (source_type) references source_type (type)
                    on update cascade on delete cascade;
            """
            cur.execute(sql)

            # analysis.visualization_default
            cur.execute('alter table analysis.visualization_default alter column x_axis drop not null')

            # cnvbase.log_define_master
            cur.execute("alter table cnvbase.log_define_master add ignore text default ''::text not null")
            cur.execute("alter table cnvbase.log_define_master add retention integer default 0 not null")

            # history.history
            cur.execute("alter table history.history rename column log_from to source")

            # history.history_from_remote
            cur.execute("alter table history.history_from_remote add db_id integer not null")

            # settings.management_setting
            sql = """
            alter table settings.management_setting drop constraint management_setting_pk;
            alter table settings.management_setting alter column target set not null;
            alter table settings.management_setting alter column host set not null;
            alter table settings.management_setting alter column username set not null;
            alter table settings.management_setting alter column password set not null;
            alter table settings.management_setting alter column dbname set not null;
            alter table settings.management_setting alter column port set not null;
            alter table settings.management_setting	add id serial not null;            
            create unique index management_setting_id_uindex
                on settings.management_setting (id);
            alter table settings.management_setting
                add constraint management_setting_pk primary key (id);            
            """
            cur.execute(sql)

            sql = '''
            insert into settings.management_setting(target, host, username, password, dbname, port)
                values(%s, %s, %s, %s, %s, %s)
            '''
            record = ('local', config['host'], config['user'], config['password'], config['dbname'], config['port'])
            cur.execute(sql, record)

            # settings.information
            for item in schema_ver_key_list:
                query = f"insert into settings.information(key, value) values('{item['key']}', '{item['version']}')"
                cur.execute(query)
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


def init_table(**kwargs):
    config = get_dbinfo(**kwargs)
    sql_path = 'migrations/resource/v1_2_0/sql/table'
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

                            if table_name == 'system_graph_type':
                                with open(os.path.join(RESOURCE_PATH, RSC_SYSTEM_GRAPH_SCRIPT), 'r') as f:
                                    data = f.read()

                                query = 'insert into graph.system_graph_type(name, script) values(%s, %s)'
                                record = ('default', data)
                                cur.execute(query, record)
                            else:
                                public_tables = {
                                    'analysis_type': analysis_type,
                                    'source_type': source_type
                                }

                                if table_name in public_tables:
                                    for item in public_tables[table_name]:
                                        query = f'insert into {schema}.{table_name}(type) values(%s)'
                                        cur.execute(query, tuple([item]))
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

        except Exception as e:
            logger.info('table create error!')
            logger.info(str(e))
            idx += 1
            if idx == len(list(file_list.items())):
                idx = 0
                loop_cnt += 1
                logger.info('Retry...')
