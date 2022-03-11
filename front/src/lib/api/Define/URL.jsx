export const SLICE = '/';
export const MAIN = SLICE + 'main';
export const NEW = MAIN + SLICE + 'new';
export const EDIT = MAIN + SLICE + 'edit';
export const ANALYSIS = SLICE + 'job';
export const PROCESS = SLICE + 'process';
export const SETTINGS = SLICE + 'settings';
export const OVERLAY = SLICE + 'overlay';

export const OVERLAY_ADC_MEASUREMENT = OVERLAY + SLICE + 'adc';
export const OVERLAY_CORRECTION = OVERLAY + SLICE + 'correction';

export const URL_RESOURCE = '/api/resources';
export const URL_RESOURCE_MAIN = URL_RESOURCE + '/main';
export const URL_RESOURCE_ABOUT = URL_RESOURCE + '/about';
export const URL_RESOURCE_FUNC = URL_RESOURCE + '/func';
export const URL_RESOURCE_SETTING = URL_RESOURCE + '/settings';
export const URL_RESOURCE_HISTORY_SETTING = URL_RESOURCE_SETTING + '/history';
export const URL_RESOURCE_RULE = URL_RESOURCE + '/rule';
export const URL_RESOURCE_SCRIPT = URL_RESOURCE + '/scripts';

export const URL_RESOURCE_SETTING_DATE = URL_RESOURCE_SETTING + '/date';

export const URL_RESOURCE_MAIN_CATEGORY = URL_RESOURCE_MAIN + '/category';

export const URL_RESOURCE_REMOTE = URL_RESOURCE + '/remote';
export const URL_RESOURCE_REMOTE_TABLE = URL_RESOURCE_REMOTE + '/tables';
export const URL_RESOURCE_REMOTE_EQUIPMENTS =
  URL_RESOURCE_REMOTE + '/equipments';
export const URL_RESOURCE_REMOTE_VALID_DATE = URL_RESOURCE_REMOTE + '/date';

//NEXT BUTTON CLICK
export const URL_RESOURCE_NEW = URL_RESOURCE + '/new';
export const URL_RESOURCE_NEW_INIT = URL_RESOURCE_NEW + '/step1';
export const URL_RESOURCE_NEW_STEP1 = URL_RESOURCE_NEW + '/step2';
export const URL_RESOURCE_NEW_STEP2 = URL_RESOURCE_NEW + '/step3';
export const URL_RESOURCE_NEW_STEP3 = URL_RESOURCE_NEW + '/step4';
export const URL_RESOURCE_NEW_STEP4 = URL_RESOURCE_NEW + '/step5';
export const URL_RESOURCE_NEW_STEP5 = URL_RESOURCE_NEW + '/step6';

export const URL_RESOURCE_STEP2_MULTI_SETTING =
  URL_RESOURCE_NEW + '/step2' + SETTINGS;

export const URL_RESOURCE_EDIT = URL_RESOURCE + '/edit';
export const URL_RESOURCE_EDIT_INIT = URL_RESOURCE_EDIT + '/step1';
export const URL_RESOURCE_EDIT_STEP1 = URL_RESOURCE_EDIT + '/step2';
export const URL_RESOURCE_EDIT_STEP2 = URL_RESOURCE_EDIT + '/step3';
export const URL_RESOURCE_EDIT_STEP3 = URL_RESOURCE_EDIT + '/step4';
export const URL_RESOURCE_EDIT_STEP4 = URL_RESOURCE_EDIT + '/step5';
export const URL_RESOURCE_EDIT_STEP5 = URL_RESOURCE_EDIT + '/step6';
export const URL_RESOURCE_EDIT_STEP6 = URL_RESOURCE_EDIT + '/step7';

//PREVIEW BUTTON CLICK
export const URL_PREVIEW = '/api/preview';
export const URL_PREVIEW_SAMPLELOG = URL_PREVIEW + '/samplelog';
export const URL_PREVIEW_SAMPLELOG_MULTI = URL_PREVIEW_SAMPLELOG + '/multi';
export const URL_PREVIEW_CONVERT = URL_PREVIEW + '/convert';
export const URL_PREVIEW_FILTER = URL_PREVIEW + '/filter';
export const URL_PREVIEW_ANALYSIS = URL_PREVIEW + '/analysis';
export const URL_PREVIEW_ANALYSIS_MULTI = URL_PREVIEW_ANALYSIS + '/multi';
export const URL_PREVIEW_CONVERTED = URL_PREVIEW + '/converted';
export const URL_PREVIEW_SQL = URL_PREVIEW + '/sql';

export const URL_CONVERTER = '/api/converter';
export const URL_CONVERTER_JOB = URL_CONVERTER + '/job';
export const URL_CONVERTER_FILE = URL_CONVERTER + '/file';

export const URL_ANALYSIS = '/api/analysis';
export const URL_ANALYSIS_LOCAL = URL_ANALYSIS + '/local';
export const URL_ANALYSIS_REMOTE = URL_ANALYSIS + '/remote';
export const URL_ANALYSIS_SQL = URL_ANALYSIS + '/sql';
export const URL_ANALYSIS_HISTORY = URL_ANALYSIS + '/history';

export const URL_ANALYSIS_DEFAULT = URL_ANALYSIS + '/default';
export const URL_ANALYSIS_DEFAULT_MULTI = URL_ANALYSIS_DEFAULT + '/multi';

export const URL_SETTING_MGMT = '/api/setting';
export const URL_SETTING_GET_LOCAL = URL_SETTING_MGMT + '/local';
export const URL_SETTING_GET_REMOTE = URL_SETTING_MGMT + '/remote';
export const URL_SETTING_GET_TABLES = URL_SETTING_MGMT + '/tables';
export const URL_SETTING_CHECK_DB_CONNECTION =
  URL_SETTING_MGMT + '/connection-check';

export const URL_IMPORT = '/api/import';
export const URL_IMPORT_DBTABLE = URL_IMPORT + '/rules';
export const URL_IMPORT_FUNCTIONS = URL_IMPORT + '/function';

export const URL_EXPORT = '/api/export';
export const URL_EXPORT_DBTABLE = URL_EXPORT + '/rules';
export const URL_EXPORT_FUNCTIONS = URL_EXPORT + '/function';
export const URL_EXPORT_OVERLAY = URL_EXPORT + '/overlay';

export const URL_OVERLAY = '/api/overlay';
export const URL_OVERLAY_CONVERT = URL_OVERLAY + '/convert';
export const URL_OVERLAY_CONVERT_STATUS = URL_OVERLAY + '/status';
export const URL_OVERLAY_REMOTE = URL_OVERLAY + '/remote';
export const URL_OVERLAY_REMOTE_EQUIPMENT = URL_OVERLAY_REMOTE + '/equipments';
export const URL_OVERLAY_EQUIPMENT_INFO = `${URL_OVERLAY_REMOTE}/info`;
export const URL_OVERLAY_SETTING_INFO = `${URL_OVERLAY}/setting`;
export const URL_OVERLAY_ANALYSIS_INFO = `${URL_OVERLAY}/info`;
export const URL_OVERLAY_PLATE_INFO = `${URL_OVERLAY_ANALYSIS_INFO}/plate`;
export const URL_OVERLAY_ANALYSIS = `${URL_OVERLAY}/analysis`;
export const URL_OVERLAY_ETC = URL_OVERLAY + '/etc';
export const URL_OVERLAY_CPVS = URL_OVERLAY + '/cpvs';
export const URL_OVERLAY_CPVS_LOAD = URL_OVERLAY_CPVS + '/load';
