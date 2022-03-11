import {
  deleteRequest,
  getRequest,
  postRequestFormData,
  postRequestJsonData,
  putRequest,
} from './requests';
import {
  URL_OVERLAY_ANALYSIS,
  URL_OVERLAY_CONVERT,
  URL_OVERLAY_CONVERT_STATUS,
  URL_OVERLAY_ETC,
  URL_OVERLAY_REMOTE_EQUIPMENT,
  URL_OVERLAY_EQUIPMENT_INFO,
  URL_OVERLAY_SETTING_INFO,
  URL_OVERLAY_ANALYSIS_INFO,
  URL_OVERLAY,
  URL_OVERLAY_CPVS_LOAD,
  URL_OVERLAY_PLATE_INFO,
} from '../Define/URL';
import { getParseJsonData } from '../../util/Util';
import { OVERLAY_ADC_CATEGORY } from '../Define/etc';

export const post_Overlay_Local_FilesUpload = async (formData) => {
  const { status, info } = await postRequestFormData(
    URL_OVERLAY_CONVERT,
    formData,
  );

  return {
    upload_id: status === 200 ? info.rid : '0',
  };
};

export const get_Overlay_Local_ConvertStatus = async ({ jobId, category }) => {
  if (jobId ?? false) {
    const { info } = await getRequest(
      `${URL_OVERLAY_CONVERT_STATUS}/${category}/${jobId}`,
    );

    let result = {
      status: info.status,
      percent:
        info.total_files > 0
          ? Math.ceil(
              ((info.error_files + info.success_files) / info.total_files) *
                100,
            ).toString()
          : '0',
      detail: {
        error_files: info.error_files,
        success_files: info.success_files,
        total_files: info.total_files,
        converted: info.inserted,
      },
    };

    if (info.info) {
      result = {
        ...result,
        targetInfo: info.info,
      };
    }

    return result;
  }
};

/*
 * Json
 * : category: ADCMEASUREMENT
 * : db_id: 1
 * : fab: “Fab1”
 * : equipment: “Equipment1”
 * */
export const get_Overlay_Remote_Info = async (params) => {
  const parseParam = getParseJsonData(params)
    .filter((obj) => obj.value !== null)
    .map((obj) => {
      return `${obj.id}=${obj.value}`;
    });
  const { info } = await getRequest(
    `${URL_OVERLAY_REMOTE_EQUIPMENT}?${parseParam.join('&')}`,
  );
  return info;
};

export const post_Overlay_Analysis = async (data) => {
  const { status, info } = await postRequestJsonData(
    URL_OVERLAY_ANALYSIS,
    undefined,
    JSON.stringify(data),
  );
  return {
    status: status,
    info: info,
  };
};

export const post_Overlay_Plate_Info = async (cat, id, data) => {
  const { info } = await postRequestJsonData(
    `${URL_OVERLAY_PLATE_INFO}/${cat}/${id}`,
    undefined,
    JSON.stringify(data),
  );
  return info;
};

export const get_Overlay_Remote_Equipment_Info = async (params) => {
  const parseParam = getParseJsonData(params)
    .filter((obj) => obj.value !== null)
    .map((obj) => {
      return `${obj.id}=${obj.value}`;
    });
  const { info } = await getRequest(
    `${URL_OVERLAY_EQUIPMENT_INFO}?${parseParam.join('&')}`,
  );
  return info;
};

export const get_Overlay_Correction_Setting_Info = async (name) => {
  const { info } = await getRequest(`${URL_OVERLAY_SETTING_INFO}/${name}`);
  return info;
};

export const get_Overlay_Analysis_Info = async (cat, id) => {
  const { info } = await getRequest(
    `${URL_OVERLAY_ANALYSIS_INFO}/${cat}/${id}`,
  );
  return info;
};

export const put_Overlay_etc_setting = async ({ obj, fab_name }) => {
  const { div, plate_size } = obj;

  const json = {
    div: { upper: div.div_upper, lower: div.div_lower },
    plate_size: { size_x: plate_size.size_x, size_y: plate_size.size_y },
  };
  const { status } = await putRequest({
    obj: json,
    url: `${URL_OVERLAY_ETC}/${fab_name}`,
  });
  return status;
};
export const get_Overlay_preset_Info = async ({ mode, id }) => {
  const { info } = await getRequest(`${URL_OVERLAY}/${mode}/cpvs/preset/${id}`);
  return info;
};
const getCPVSItems = (shots, keys, shot_num) => {
  const obj = shots?.[keys].find((o) => o.shot.id === shot_num);
  const keylist = Object.keys(obj);
  return keylist.reduce(
    (acc, o) =>
      o === 'shot'
        ? { ...acc, [`${keys}mode`]: obj.shot.mode }
        : { ...acc, [o]: obj[o].value, [`${o}_chk`]: obj[o].checked },
    {},
  );
};
export const add_Overlay_preset_info = async ({ preset, shots, mode }) => {
  const json = {
    preset: preset,
    items:
      mode === OVERLAY_ADC_CATEGORY
        ? Object.keys(shots).map((shot_num) => ({
            shot_no: shot_num,
            ...shots[shot_num],
          }))
        : shots?.cp
            .map((o) => o.shot.id)
            .map((shotN) => ({
              ...getCPVSItems(shots, 'cp', shotN),
              ...getCPVSItems(shots, 'vs', shotN),
              shot_no: shotN,
            })),
  };
  //url, param, items
  const { info } = await postRequestJsonData(
    `${URL_OVERLAY}/${mode}/cpvs/preset`,
    undefined,
    json,
  );
  return info.id;
};
export const update_Overlay_preset_info = async ({
  preset,
  shots,
  mode,
  preset_id,
}) => {
  const json = {
    preset: preset,
    items:
      mode === OVERLAY_ADC_CATEGORY
        ? Object.keys(shots).map((shot_num) => ({
            shot_no: shot_num,
            ...shots[shot_num],
          }))
        : shots?.cp
            .map((o) => o.shot.id)
            .map((shotN) => ({
              ...getCPVSItems(shots, 'cp', shotN),
              ...getCPVSItems(shots, 'vs', shotN),
              shot_no: shotN,
            })),
  };
  //url, param, items
  const { status } = await putRequest({
    url: `${URL_OVERLAY}/${mode}/cpvs/preset/${preset_id}`,
    obj: json,
  });
  return status;
};

export const delete_Overlay_preset_info = async ({ id, mode, tab }) => {
  //url, param, items
  const { status } = await deleteRequest(
    `${URL_OVERLAY}/${mode}/cpvs/preset`,
    id,
  );
  return { status, id, mode, tab };
};

export const post_Overlay_job_FilesUpload = async (formData) => {
  const { status, info } = await postRequestFormData(
    URL_OVERLAY_CPVS_LOAD,
    formData,
  );

  return { status, cp_vs: info };
};
