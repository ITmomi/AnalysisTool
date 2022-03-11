##########################################################################
# Application Information
##########################################################################
APP_MAJOR = 0
APP_MINOR = 0
APP_REVISION = 1
APP_VERSION = '%s.%s.%s' % (APP_MAJOR, APP_MINOR, APP_REVISION)
APP_COPYRIGHT = 'Copyright (c) 2021 CANON Inc. All rights reserved.'
APP_MODE = 'Desktop'

API_VERSION = APP_VERSION
API_TITLE = 'MPA Analysis Tool - REST API SERVER'
API_DESCRIPTION = 'MPA Analysis ToolのREST APIに対する詳細説明ページです。'
API_LICENSE = APP_COPYRIGHT

##########################################################################
# Debug Mode
##########################################################################
DEBUG = False

##########################################################################
# Log System Settings
##########################################################################
LOG = 'APP_LOG'
LOG_FILENAME = 'log.log'
LOG_FILEPATH = 'logs'
LOG_ERRNAME = 'err.log'
LOG_MAXBYTE = 10 * 1024 * 1024
LOG_BACKUPCOUNT = 100
LOG_FORMAT = '%(asctime)s: %(levelname)s: %(module)s: %(message)s'
LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'

##########################################################################
# PATH
##########################################################################
RESOURCE_PATH = 'resource'
BACKUP_PATH = '.backup'
TEMP_PATH = '.tmp'
SCRIPT_EXEC_PATH = '__script__'
local_cache_root = '.convert'
CNV_RESULT_PATH = '.cnv_result'
root_path = '.files'

DB_CONFIG_PATH = 'config/db_config.conf'

STATIC_JS_PATH = 'web/static/js'
STATIC_PATH = 'web/static'
STATIC_PONTS_PATH = 'web/static/fonts'

RSC_JSON_MAIN = 'json/page_main.json'
RSC_JSON_ABOUT = 'json/page_about.json'
RSC_JSON_MGMT_LOCAL = 'json/page_mgmt_local.json'
RSC_JSON_SETTING_LOCAL_FORM = 'json/setting_local_form.json'
RSC_JSON_SETTING_LOCAL_HIS_FORM = 'json/setting_local_history_form.json'
RSC_JSON_SETTING_REMOTE_FORM = 'json/setting_remote_form.json'
RSC_JSON_SETTING_REMOTE_HIS_FORM = 'json/setting_remote_history_form.json'
RSC_JSON_SETTING_SQL_FORM = 'json/setting_sql_form.json'
RSC_JSON_SETTING_SQL_HIS_FORM = 'json/setting_sql_history_form.json'
RSC_JSON_SETTING_MULTI_LOCAL_FORM = 'json/setting_multi_local_form.json'
RSC_JSON_SETTING_MULTI_LOCAL_HIS_FORM = 'json/setting_multi_local_his_form.json'
RSC_JSON_SETTING_MULTI_REMOTE_FORM = 'json/setting_multi_remote_form.json'
RSC_JSON_SETTING_MULTI_REMOTE_HIS_FORM = 'json/setting_multi_remote_his_form.json'
RSC_JSON_SETTING_MULTI_SQL_FORM = 'json/setting_multi_sql_form.json'
RSC_JSON_SETTING_MULTI_SQL_HIS_FORM = 'json/setting_multi_sql_his_form.json'
RSC_JSON_OPT_AGGREG_FORM = 'json/option_aggregation_form.json'
RSC_JSON_STEP2_LOCAL_FORM = 'json/step2_local_form.json'
RSC_JSON_STEP2_REMOTE_FORM = 'json/step2_remote_form.json'
RSC_JSON_STEP2_SQL_FORM = 'json/step2_sql_form.json'
RSC_JSON_STEP2_LOCAL_EDIT_FORM = 'json/step2_local_edit_form.json'
RSC_JSON_STEP2_REMOTE_EDIT_FORM = 'json/step2_remote_edit_form.json'
RSC_JSON_STEP2_SQL_EDIT_FORM = 'json/step2_sql_edit_form.json'
RSC_JSON_STEP2_MULTI_LOCAL_FORM = 'json/step2_multi_local_form.json'
RSC_JSON_STEP2_MULTI_REMOTE_FORM = 'json/step2_multi_remote_form.json'
RSC_JSON_STEP2_MULTI_SQL_FORM = 'json/step2_multi_sql_form.json'
RSC_COLUMN_ANALYSIS_DEFAULT = 'script/column_analysis.py'

RSC_SETTING_FAB_DEFAULT = 'setting/fab_default.json'
RSC_SETTING_ADC_MEAS_CP_VS_DEFAULT = 'setting/adc_meas_cp_vs_default.json'



VALIDATION_JSON_PATH = 'test/validation_json'

##########################################################################
# DATA CLEAN INTERVAL
##########################################################################
CLEANER_INTERVAL = 60 * 60  # 60min
EXPIRING_DATE_HOUR = 24     # 24Hours

##########################################################################
# DATABASE SCHEMA
##########################################################################
SCHEMA_SETTINGS = 'settings'
SCHEMA_CONVERT = 'convert'
SCHEMA_ANALYSIS = 'analysis'
SCHEMA_PUBLIC = 'public'
SCHEMA_CNVBASE = 'cnvbase'
SCHEMA_CNVSET = 'cnvset'
SCHEMA_HISTORY = 'history'
SCHEMA_GRAPH = 'graph'
SCHEMA_CREATE_LIST = [SCHEMA_PUBLIC, SCHEMA_SETTINGS, SCHEMA_ANALYSIS, SCHEMA_CNVSET, SCHEMA_HISTORY, SCHEMA_GRAPH]
SCHEMA_EXPORT_LIST = [SCHEMA_CNVBASE]
SCHEMA_EXPORT_LIST_FOR_MAKE_INIT_DATA = [SCHEMA_CNVBASE, SCHEMA_PUBLIC, SCHEMA_ANALYSIS, SCHEMA_GRAPH]

##########################################################################
# DATABASE TABLE
##########################################################################
TBL_SETTINGS_INFORMATION = 'settings.information'
TBL_CNVBASE_INFORMATION = 'cnvbase.information'
TBL_SYSTEM_GRAPH_TYPE = 'graph.system_graph_type'
EXPORT_OMIT_TBL_LIST = [TBL_CNVBASE_INFORMATION, TBL_SYSTEM_GRAPH_TYPE]
COLUMN_OMIT_LIST = ['id', 'created_time', 'request_id', 'equipment_name', 'log_idx']

##########################################################################
# Remote Server URL
##########################################################################
API_GET_NAMES = '/logmonitor/api/v1/site/name'
API_GET_EQUIPMENTS = '/logmonitor/api/v1/analysis/equipments'
API_GET_DATE = '/logmonitor/api/v1/analysis/date'
API_GET_LOG_LIST = '/logmonitor/api/v1/analysis/loglist'
API_GET_LOG = '/logmonitor/api/v1/analysis/log'
API_GET_CONNECTION = '/logmonitor/api/v1/analysis/connection'


##########################################################################
# MISC.
##########################################################################
CONVERTING_PROCESSES = 4

SAMPLE_LINES = 30

NEW_LOG = 0
ADD_RULE = 1
EDIT_RULE = 2

NA_VALUE = '-99999999999999'

##########################################################################
# UNIT
##########################################################################
OFFSET_UNIT = 1000
GRP_THREASHOLD = (50 * 2 * 1000000)

##########################################################################
# Coef.
##########################################################################
MM_TO_NM = 1.0e6
NM_TO_MM = 1.0e-6

##########################################################################
# Map Graph Default Settings.
##########################################################################
MAP_COLUMN_NUM = 4
MAP_SCALE = 50