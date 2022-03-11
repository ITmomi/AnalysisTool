export const QUERY_KEY = {
  MAIN_INIT: 'main_init',
  VERSION_INIT: 'version_init',
  //---------------------------------------------------------
  JOBSETTING_INIT: 'jobSetting/loading',
  JOBSETTING_FILE_UPLOAD: 'jobSetting/file-upload',
  JOBSETTING_LOCAL_JOB: 'jobSetting/local/convert-job',
  JOBSETTING_SQL_JOB: 'jobSetting/sql',
  JOBSETTING_REMOTE_JOB: 'jobSetting/remote',
  JOBSETTING_HISTORY_JOB: 'jobSetting/history',
  JOBSETTING_USER_FAB_EQUIPMENT_LIST: 'jobSetting/remote/equipment_list',
  JOBSETTING_CONVERT_NG: 'jobSetting/convert-job/delete',
  JOBSETTING_CONVERT_JOB_STATUS: 'jobSetting/convert-job/status',
  JOBSETTING_EQUIPMENT_VALID_DATE: 'jobSetting/remote/table/equipment/date',
  JOBSETTING_DELETE_HISTORY: 'jobSetting/history/delete',
  JOBSETTING_MULTIJOB_UPDATE: 'jobSetting/multi/info_update', //mutation

  //---------------------------------------------------------
  MGMT_INIT: 'mgmt_init',
  MGMT_LOCAL_DB: 'mgmt/local',
  MGMT_REMOTE_DB: 'mgmt/remote',
  MGMT_REMOTE_DB_LIST: 'mgmt/remote/list',
  MGMT_REMOTE_DB_DETAIL: 'mgmt/remote/db_id',
  MGMT_REMOTE_DB_STATUS: 'mgmt/remote/db_id/status',
  MGMT_TABLE_DB: 'mgmt/table',
  DB_CONNECTION_CHECK: 'mgmt/connection-check', //mutation
  MGMT_DB_UPDATE: 'mgmt/db_update', //mutation
  MGMT_DB_DELETE: 'mgmt/db_delete', //mutation
  MGMT_DB_ADD: 'mgmt/db_add', //mutation
  MGMT_RULES_IMPORT: 'mgmt/rules/import',

  //---------------------------------------------------------
  STEP1_NEW_INIT: 'jobStep/step1/new_init',
  STEP1_EDIT_INIT: 'jobStep/step1/edit_init',
  STEP1_NEXT: 'jobStep/step1/next',
  STEP2_MULTI_RESOURCE: 'jobStep/step2/resource/multi',
  STEP2_MULTI_PREVIEW: 'jobStep/step2/preview/multi',
  STEP2_MULTI_LOCAL_JOB_STATUS: 'jobStep/step2/preview/local/convertor',
  STEP2_MULTI_PREVIEW2: 'jobStep/step2/preview/multi/request',
  STEP2_RESOURCE_UPDATE: 'jobStep/step2/resource/update',
  STEP2_DB_TABLE_LIST: 'jobStep/step2/db_id/table_list',
  STEP2_USER_FAB_EQUIPMENT_LIST: 'jobStep/step2/db_id/table/equipment_list',
  STEP2_EQUIPMENT_VALID_DATE: 'jobStep/step2/db_id/table/equipment/date',
  STEP5_PREVIEW: 'jobStep/step5/preview',
  STEP5_DATASOURCE_LIST: 'jobStep/step5/db_list',
  STEP5_SQL_QUERY: 'jobStep/step5/sql_query',

  //---------------------------------------------------------
  OVERLAY_REMOTE_DB_LIST: 'overlay/remote/list',
  OVERLAY_REMOTE_USER_FAB_EQUIPMENT: 'overlay/remote/equipment',
  OVERLAY_LOCAL_FILE_UPLOAD: 'overlay/local/file-upload',
  OVERLAY_ETC_SETTING_UPDATE: 'overlay/map/etc',
  OVERLAY_PRESET_ADD: 'overlay/map/preset/add', //mutation
  OVERLAY_PRESET_UPDATE: 'overlay/map/preset/update', //mutation
  OVERLAY_PRESET_DELETE: 'overlay/map/preset/delete', //mutation
  OVERLAY_PRESET_GET: 'overlay/map/preset/get',
};
