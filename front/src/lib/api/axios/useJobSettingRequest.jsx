import {
  deleteRequest,
  getRequest,
  getRequestParam,
  postRequestFormData,
  postRequestJsonData,
  putRequest,
} from './requests';
import {
  URL_ANALYSIS_DEFAULT_MULTI,
  URL_ANALYSIS_HISTORY,
  URL_ANALYSIS_REMOTE,
  URL_ANALYSIS_SQL,
  URL_CONVERTER_FILE,
  URL_CONVERTER_JOB,
  URL_RESOURCE_HISTORY_SETTING,
  URL_RESOURCE_SETTING,
} from '../Define/URL';
import { MSG_LOCAL, MSG_REMOTE, MSG_SQL } from '../Define/Message';
import { getFormdataFiles } from '../../util/Util';

export const getResource_JobSetting = async ({ func_id }) => {
  const { info } = await getRequest(`${URL_RESOURCE_SETTING}/${func_id}`);
  return {
    info: info,
  };
};

export const getResource_HistorySetting = async ({ history_id }) => {
  const { info } = await getRequest(
    `${URL_RESOURCE_HISTORY_SETTING}/${history_id}`,
  );
  return {
    id: history_id,
    info: info,
  };
};

export const uploadFiles_JobSetting = async (formData, job) => {
  const FormObj = new FormData();
  FormObj.append('files', getFormdataFiles(formData));
  FormObj.append('log_name', job?.info?.log_name ?? job?.log_name);
  const { status, info } = await postRequestFormData(
    URL_CONVERTER_FILE,
    FormObj,
  );
  return {
    upload_id: status === 200 ? info.fid : '0',
    jobInfo: job,
  };
};
export const getRequestIdFromJobSetting = async ({ source, object, files }) => {
  let json = undefined;
  let url;
  if (source === MSG_REMOTE) {
    json = JSON.stringify({
      db_id: object?.db_id ?? '',
      equipment_name: object?.equipment_name ?? '',
      period: `${object?.selected.start ?? ''}~${object?.selected.end ?? ''}`,
    });
    url = `${URL_ANALYSIS_REMOTE}/${object?.sub_func_id ?? object.func_id}`;
  } else if (source === MSG_SQL) {
    json = JSON.stringify({
      db_id: object?.db_id ?? '',
    });
    url = `${URL_ANALYSIS_SQL}/${object?.sub_func_id ?? object.func_id}`;
  } else if (source === MSG_LOCAL) {
    json = JSON.stringify({
      log_name: object?.log_name ?? object?.info?.log_name ?? '',
      source: MSG_LOCAL,
      file: files ?? [],
      func_id: object?.sub_func_id ?? object?.func_id ?? '',
    });
    url = `${URL_CONVERTER_JOB}`;
  } else {
    url = `${URL_ANALYSIS_HISTORY}/${object.func_id}/${object.history_id}`;
  }
  if (json === undefined) {
    const { info } = await getRequest(url);
    return {
      rid: info.rid,
    };
  } else {
    const { info } = await postRequestJsonData(url, undefined, json);
    return {
      rid: info.rid,
    };
  }
};

export const deleteConvertJob = async ({ jobId }) => {
  const { info } = await deleteRequest(URL_CONVERTER_JOB, jobId);
  return info;
};

export const deleteHistoryJob = async ({ HistoryId }) => {
  const { status } = await deleteRequest(URL_ANALYSIS_HISTORY, HistoryId);
  return status;
};

export const getConvertJobStatus = async ({ jobId }) => {
  if (jobId ?? false) {
    const { info } = await getRequestParam(URL_CONVERTER_JOB, jobId);
    const { total_files, error_files, success_files, status } = info;

    return {
      status: status,
      percent:
        total_files > 0
          ? Math.ceil(
              ((error_files + success_files) / total_files) * 100,
            ).toString()
          : '0',
      detail: {
        error_files: error_files,
        success_files: success_files,
        total_files: total_files,
        converted: info.inserted,
      },
    };
  }
};

/******************************************* MULTI ****************************************/
export const update_multiJobInfo = async ({ func_id, object, rid }) => {
  console.log('[update_multiJobInfo]rid', rid);
  console.log('[update_multiJobInfo]object', object);
  console.log('[update_multiJobInfo]func_id', func_id);
  const jobType = object.job_type;
  const { info, status } = await putRequest({
    obj:
      jobType === MSG_LOCAL
        ? {
            rid: rid,
            fid: object.fid,
            multi_info_id: object.multi_info_id,
          }
        : jobType === MSG_REMOTE
        ? {
            multi_info_id: object.multi_info_id,
            rid: rid,
            db_id: object.db_id,
            table_name: object.table_name,
            equipment_name: object.equipment_name,
            period_start: object.selected.start,
            period_end: object.selected.end,
          }
        : jobType === MSG_SQL
        ? {
            rid: rid,
            multi_info_id: object.multi_info_id,
            db_id: object.db_id,
            sql: object.sql,
          }
        : {},
    url: `${URL_ANALYSIS_DEFAULT_MULTI}/${func_id}`,
  });
  return {
    info: info,
    status: status,
  };
};
