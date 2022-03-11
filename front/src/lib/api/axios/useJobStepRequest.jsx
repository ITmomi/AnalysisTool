import { deleteRequest, getRequest, postRequestJsonData } from './requests';
import {
  URL_PREVIEW_SQL,
  URL_RESOURCE_EDIT_STEP1,
  URL_RESOURCE_REMOTE_TABLE,
  URL_RESOURCE_RULE,
  URL_RESOURCE_STEP2_MULTI_SETTING,
  URL_PREVIEW_SAMPLELOG_MULTI,
} from '../Define/URL';
import { MSG_LOCAL, MSG_REMOTE, MSG_SQL } from '../Define/Message';
import {
  getRequestIdFromJobSetting,
  uploadFiles_JobSetting,
} from './useJobSettingRequest';

export const getStep1Resource = async ({ url }) => {
  const { info } = await getRequest(`${url}`);
  return {
    info: info,
  };
};

export const getEditStep1Resource = async ({ url }) => {
  const { info } = await getRequest(`${url}`);
  return {
    info: info,
  };
};
export const getStep2ResourceUpdate = async ({ func_id }) => {
  const { info } = await getRequest(`${URL_RESOURCE_EDIT_STEP1}/${func_id}`);
  return {
    info: info,
  };
};
export const getStep2MultiResource = async ({ func_id }) => {
  const { info } = await getRequest(
    `${URL_RESOURCE_STEP2_MULTI_SETTING}/${func_id}`,
  );
  return {
    info: info,
  };
};

export const getJobIdStep2MultiFunc = async ({ LocalStatus, object, data }) => {
  const wait = (timeToDelay) =>
    new Promise((resolve) => setTimeout(resolve, timeToDelay));
  if (object ?? false) {
    if (object.source_type === MSG_LOCAL && (data ?? false)) {
      let jobStatus;
      const { upload_id } = await uploadFiles_JobSetting(data, object);
      const { rid } = await getRequestIdFromJobSetting({
        source: object?.source_type,
        object: object,
        files: upload_id,
      });
      do {
        jobStatus = await LocalStatus({ rid });
        await wait(1000).then(console.log('eeeeeeee'));
      } while (
        (jobStatus?.percent ?? 0) !== '100' ||
        (jobStatus?.status ?? 'running') === 'running'
      );
      return {
        id: object.multi_info_id,
        status:
          jobStatus?.status === 'success'
            ? (jobStatus?.detail?.converted ?? 0) === 0
              ? 'error'
              : 'completed'
            : jobStatus.status,
        rid: rid,
        fid: upload_id,
      };
    } else if (
      object.source_type === MSG_SQL ||
      object.source_type === MSG_REMOTE
    ) {
      const { rid } = await getRequestIdFromJobSetting({
        source: object?.source_type,
        object: { ...object?.info, func_id: object.sub_func_id },
      });
      return {
        id: object.multi_info_id,
        status: 'completed',
        rid: rid,
      };
    }
  }
};

export const getStep2MultiPreview = async ({
  list,
  use_org_analysis,
  func_id,
}) => {
  const { info } = await postRequestJsonData(
    `${URL_PREVIEW_SAMPLELOG_MULTI}`,
    undefined,
    JSON.stringify({
      use_org_analysis: use_org_analysis ?? false,
      func_id: func_id,
      func_list: list.map((obj) => {
        return {
          func_id: obj.sub_func_id,
          tab_name: obj.tab_name,
          rid: obj.rid,
        };
      }),
    }),
  );
  return { info };
};

export const getTableList = async ({ db_id }) => {
  const { info } = await getRequest(`${URL_RESOURCE_REMOTE_TABLE}/${db_id}`);
  return {
    info: info,
    id: db_id,
  };
};

export const deleteRuleName = async ({ rule_id }) => {
  const { data } = await deleteRequest(URL_RESOURCE_RULE, rule_id);
  return {
    info: data,
    rule_id: rule_id,
  };
};

export const getAnalysisScriptPreview = async ({ obj }) => {
  const { info, status } = await postRequestJsonData(
    URL_PREVIEW_SQL,
    undefined,
    JSON.stringify(obj),
  );
  return {
    info: info,
    status: status,
  };
};
