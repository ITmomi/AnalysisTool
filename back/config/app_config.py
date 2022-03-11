##########################################################################
# Application Information
##########################################################################
APP_NAME = 'MPA Analysis Tool'
APP_MAJOR = 1
APP_MINOR = 3
APP_REVISION = 0
APP_VERSION = '%s.%s.%s' % (APP_MAJOR, APP_MINOR, APP_REVISION)

##########################################################################
# Import/Export File Version
##########################################################################
IMPORT_EXPORT_FILE_VER = '1.2.0'


APP_COPYRIGHT = 'Copyright (c) 2021-2022 CANON Inc. All rights reserved.'
APP_MODE = 'Desktop'

API_VERSION = APP_VERSION
API_TITLE = 'MPA Analysis Tool - REST API SERVER'
API_DESCRIPTION = 'MPA Analysis ToolのREST APIに対する詳細説明ページです。'
API_LICENSE = APP_COPYRIGHT

##########################################################################
# Debug Mode
##########################################################################
DEBUG = True

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
RSC_SETTING_CORRECTION_CP_VS_DEFAULT = 'setting/correction_cp_vs_default.json'
RSC_SETTING_CORR_COMP_DEFAULT = 'setting/correction_component_default.json'

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
GRP_THREASHOLD = (50 * 2)

##########################################################################
# Coef.
##########################################################################
# plate倍率/回転成分は 1000 倍で表示する
plate_rot_coef = 1.0e3
plate_mag_coef = 1.0e3

##########################################################################
# Map Graph Default Settings.
##########################################################################
MAP_COLUMN_NUM = 4
MAP_SCALE = 50

##########################################################################
# ADC Measurement
##########################################################################
ADC_MEAS_LOGNAME = 'ADCMEASUREMENT'
ADC_MEAS_TABLE_NAME = 'adc_measurement'
dx_list = ['p1_xl', 'p1_xr', 'p2_xl', 'p2_xr', 'p3_xl', 'p3_xr']
dy_list = ['p1_yl', 'p1_yr', 'p2_yl', 'p2_yr', 'p3_yl', 'p3_yr']
meas_column_list = dx_list + dy_list

cp_comp_values = ['cp1', 'cp2', 'cp3']
vs_comp_values = ['vs1', 'vs2', 'vs3']
cp_vs_list = cp_comp_values + vs_comp_values

pro_file_col_tbl = {
    '22006': 'cp1',
    '22005': 'cp2',
    '22007': 'cp3',
    '2CCF0': 'vs1',
    '22021': 'vs2',
    '2CCF1': 'vs3'
}

# 計測値の変数名
meas_x_rl_ivalue = [['p1_xr', 'p1_xl'],
                    ['p2_xr', 'p2_xl'],
                    ['p3_xr', 'p3_xl']]
meas_y_rl_ivalue = [['p1_yr', 'p1_yl'],
                    ['p2_yr', 'p2_yl'],
                    ['p3_yr', 'p3_yl']]

# Matrix基本列名
base_col = {
    'x': ['X', 'DR_Upper', 'DR_Lower', 'MX', 'MX_Upper', 'MX_Lower'],
    'y': ['Y', 'MY_Upper', 'MY_Lower', 'T', 'Yaw_Upper', 'Yaw_Lower']
}

column_type = {
    'p1_xl': float, 'p1_yl': float, 'p1_xr': float, 'p1_yr': float,
    'p2_xl': float, 'p2_yl': float, 'p2_xr': float, 'p2_yr': float,
    'p3_xl': float, 'p3_yl': float, 'p3_xr': float, 'p3_yr': float,
    'logicalposition_x': float, 'logicalposition_y': float,
    'cp1': float, 'cp2': float, 'cp3': float,
    'vs1': float, 'vs2': float, 'vs3': float,
    'plate': int, 'step': int
}

##########################################################################
# ANOVA Default Settings.
##########################################################################
# デフォルト値
DEFAULT_VAL_ANOVA = {
    # VS幅[mm]
    'vs': 750.0,
    # スリット円弧半径[mm]
    'radius': 455.0
}

##########################################################################
# Overlay Correction
##########################################################################
CORRECTION_LOGNAME = 'correction'
AdcCorrectionMeasOffsetEvent = 'AdcCorrectionMeasOffsetEvent'
AdcCorrectionOffsetEvent = 'AdcCorrectionOffsetEvent'
StageCorrectionMapEvent = 'StageCorrectionMapEvent'
AdcCorrectionMeasEvent = 'AdcCorrectionMeasEvent'