import axios from 'axios';
import PropTypes from 'prop-types';
import { getParseJsonData } from '../../util/Util';
import {
  URL_CONVERTER_JOB,
  URL_RESOURCE_MAIN_CATEGORY,
  URL_EXPORT,
  URL_RESOURCE_REMOTE_VALID_DATE,
  URL_RESOURCE_REMOTE_EQUIPMENTS,
} from '../Define/URL';
import { E_MULTI_TYPE, RESPONSE_NG, RESPONSE_OK } from '../Define/etc';

const client = axios.create();
const jsonConfig = {
  headers: {
    'Content-Type': 'application/json',
  },
};
const FormDataConfig = {
  headers: {
    'Content-Type': 'multipart/form-data',
  },
};
export const exportFile = async (url, filename) => {
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename); //any other extension
  document.body.appendChild(link);
  link.click();
  link.remove();
};

export const getRequest = async (url) => {
  const { data, status } = await client.get(url);
  return {
    status: status,
    info: data,
  };
};

export const getRequestParam = async (url, param) => {
  const { data, status } = await client.get(
    param === undefined ? `${url}` : `${url}/` + param,
  );
  return {
    status: status,
    info: data,
  };
};

export const putRequest = async ({ url, obj }) => {
  const { data, status } = await client.put(
    url,
    JSON.stringify(obj),
    jsonConfig,
  );
  return {
    status: status,
    info: data.msg,
    data: data,
  };
};

export const deleteRequest = async (url, param) => {
  const { data, status } = await client.delete(`${url}/` + param);
  console.log('data: ', data);
  console.log('status: ', status);
  return {
    status: status,
    info: data.msg,
    data: data,
  };
};

export const postRequestFormData = async (url, form) => {
  const { data, status } = await client.post(url, form, FormDataConfig);
  return {
    status: status,
    info: data,
  };
};

export const postRequestJsonData = async (url, param, items) => {
  if (param !== undefined) {
    const parameter = param.map((obj) => {
      return `${obj.id}=${obj.value}`;
    });
    const { data, status, errors } = await client.post(
      `${url}?${parameter}`,
      items,
      jsonConfig,
    );
    console.log('[postRequestJsonData]data', data);
    console.log('[postRequestJsonData]status', status);
    console.log('[postRequestJsonData]errors', errors);

    return {
      status: status,
      info: status === 200 ? data : errors,
    };
  } else {
    const { data, status } = await client.post(url, items, jsonConfig);
    return {
      status: status,
      info: data,
    };
  }
};

export const updateCategoryList = async (categories) => {
  const { data, statusText, msg } = await client.post(
    URL_RESOURCE_MAIN_CATEGORY,
    categories,
    jsonConfig,
  );
  console.log('statusText: ', statusText);
  console.log('data: ', data);
  console.log('msg: ', msg);

  return {
    status: statusText,
    menu: data,
  };
};

export const postRequestItems = async ({ items, url }) => {
  const param = items
    .filter((obj) => obj.content !== undefined)
    .map((obj) => {
      return [obj.target, obj.content];
    });
  const request = Object.fromEntries(param);

  const { data, statusText } = await client.post(
    url,
    JSON.stringify(request),
    jsonConfig,
  );
  console.log('statusText: ', statusText);
  console.log('data: ', data);

  return {
    status: statusText,
    info: data.data,
  };
};
export const putRequestItems = async ({ items, url }) => {
  const request = items
    .filter((obj) => obj.content !== undefined)
    .reduce((acc, obj) => ({ ...acc, [obj.target]: obj.content }), {});

  console.log('request: ', request);

  const { data, statusText, msg } = await putRequest({
    url: url,
    obj: request,
  });
  console.log('statusText: ', statusText);
  console.log('data: ', data);
  console.log('msg: ', msg);

  return {
    status: statusText,
    msg: data.data,
  };
};

export const reqZipFileUpload = async (url, file) => {
  const response = await client.post(url, file, {
    header: { 'Content-Type': 'multipart/form-data' },
  });
  console.log(response);
  return {
    status: response.status,
    data: response.data,
  };
};
// const encode = (s) => {
//   const out = [];
//   for (let i = 0; i < s.length; i++) {
//     out[i] = s.charCodeAt(i);
//   }
//   return new Uint8Array(out);
// };
export const getRequestJsonExport = async (url, param) => {
  const ret = { status: undefined };
  const modified = `${url}` + `?${param?.join('&')}` ?? '';
  console.log('modified', modified);
  await client
    .get(modified)
    .then((response) => {
      console.log(response);
      const data = JSON.stringify(response.data);
      // const data = encode(str);

      const url = URL.createObjectURL(
        new Blob([data], {
          type: 'application/json;charset=utf-8',
        }),
      );
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'function_export.json');
      document.body.appendChild(link);
      link.click();
      link.remove();
      ret.status = RESPONSE_OK;
    })
    .catch(function (error) {
      console.log(error);
      ret.status = RESPONSE_NG;
    });
  return ret;
};

export const postRequestExport = async (formData) => {
  let status = RESPONSE_NG;
  for (let key of formData.keys()) {
    console.log('formData[key]', key);
  }
  for (let value of formData.values()) {
    console.log('formData[value]', value);
  }

  await postFormdataRequestExport(URL_EXPORT, formData).then((_) => _);

  return status;
};

export const postFormdataRequestExport = async (url, formData) => {
  let status = RESPONSE_NG;
  for (let key of formData.keys()) {
    console.log('formData[key]', key);
  }
  for (let value of formData.values()) {
    console.log('formData[value]', value);
  }

  await client
    .post(url, formData, {
      responseType: 'blob',
      header: { 'Content-Type': 'multipart/form-data' },
    })
    .then((response) => {
      console.log(response);
      status = RESPONSE_OK;
      const blob = new Blob([response.data], {
        type: response.headers['content-type'],
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'data.zip');
      document.body.appendChild(link);
      link.click();
      link.remove();
    })
    .catch(function (error) {
      console.log(error);
    });

  return status;
};

export const reqPostFocusJob = async (JobInfo, files) => {
  console.log('JobInfo', JobInfo);
  if ((JobInfo?.source || 'local') === 'remote') {
    const request = {
      period: JobInfo.period,
    };
    console.log('JSON', JSON.stringify(request));
    const data = await client.post(
      `/api/analysis/remote/${JobInfo.func_id}/${JobInfo.equipment_name}`,
      JSON.stringify(request),
      jsonConfig,
    );
    console.log('response: ', data);
    return {
      status: data.status,
      jobId: data.statusText === 'OK' ? data.data.rid : '0',
    };
  } else {
    const request = {
      log_name: JobInfo.log_name,
      source: (JobInfo?.source || 'local').toLowerCase(),
      file: files, //file folder 넣어주기...
    };
    console.log('JSON', JSON.stringify(request));
    const data = await client.post(
      URL_CONVERTER_JOB,
      JSON.stringify(request),
      jsonConfig,
    );
    console.log('response: ', data);
    return {
      status: data.status,
      jobId: data.statusText === 'OK' ? data.data.rid : '0',
    };
  }
};

export const getEquipmentList = async ({ db_id, table_name }) => {
  const { info } = await getRequest(
    `${URL_RESOURCE_REMOTE_EQUIPMENTS}/${db_id}/${table_name}`,
  );
  return {
    info: info,
  };
};

export const getEquipmentValidDate = async ({
  db_id,
  table_name,
  equipment_name,
}) => {
  const { info } = await getRequest(
    `${URL_RESOURCE_REMOTE_VALID_DATE}/${db_id}/${table_name}/${equipment_name}`,
  );
  return {
    info: info,
  };
};

export const getStatusFocusJob = async (jobId) => {
  console.log('[getStatusFocusJob]jobId', jobId);
  const { data } = await client.get(URL_CONVERTER_JOB + '/' + jobId);
  console.log('getStatusFocusJob: ', data);
  const { total_files, error_files, success_files, status } = data;

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
      converted: data.inserted,
    },
  };
};

getStatusFocusJob.propTypes = {
  rid: PropTypes.string,
};

export const getSummaryData = async (logName, jobId, json) => {
  console.log('[getSummaryData]', json);
  const param = getParseJsonData(json)
    .filter((obj) => obj.value !== null)
    .map((obj) => {
      return `${obj.id}=${obj.value}`;
    });
  const url = `/api/analysis/summaries/${logName}/${jobId}?${param.join('&')}`;
  const { data } = await client.get(url);
  return {
    data: data.data !== undefined ? data.data : [],
    items: data.items !== undefined ? data.items : [],
  };
};

getSummaryData.propTypes = {
  logName: PropTypes.string.isRequired,
  jobId: PropTypes.string.isRequired,
  jobName: PropTypes.string,
  startDate: PropTypes.string.isRequired,
  endData: PropTypes.string.isRequired,
};

export const getDetailData = async (logName, jobId, params) => {
  const {
    groupBy,
    groupValue,
    selectedRows,
    startDate,
    endDate,
    jobName,
  } = params;
  let url =
    `/api/analysis/details/${logName}/${jobId}?group_by=${groupBy}&group_value=${groupValue}&start=${startDate}&end=${endDate}` +
    (jobName !== null ? `&jobname=${jobName}` : ``);

  selectedRows.map((item) => {
    url += `&group_selected=${item}`;
  });

  const { data } = await client.get(url);

  return {
    data: data.data !== undefined ? data.data : [],
  };
};

getDetailData.propTypes = {
  logName: PropTypes.string.isRequired,
  jobId: PropTypes.string.isRequired,
  params: PropTypes.shape({
    groupBy: PropTypes.string.isRequired,
    groupValue: PropTypes.string.isRequired,
    selectedRows: PropTypes.array.isRequired,
    startDate: PropTypes.string.isRequired,
    endData: PropTypes.string.isRequired,
    jobName: PropTypes.string,
  }),
};

export const getAnalysisOptionInfo = async (fId, rId, jtype) => {
  const { data } = await client.get(
    jtype === E_MULTI_TYPE
      ? `api/analysis/default/${jtype}/${fId}`
      : `api/analysis/default/${jtype}/${fId}/${rId}`,
  );
  return data;
};

export const getAnalysisData = async (param, type) => {
  let url,
    obj = {};

  if (type.match(/multi/)) {
    url = `api/analysis/multi/${param.fId}?start=${param.start}&end=${param.end}&aggregation_key=${param.agMain}&aggregation_val=${param.agSub}`;
  } else {
    url = `api/analysis/${param.fId}/${param.rId}?start=${param.start}&end=${param.end}&aggregation_key=${param.agMain}&aggregation_val=${param.agSub}`;
  }

  Object.keys(param.filter).forEach((k) => {
    url += `&filter_key=${k}`;
    if (Array.isArray(param.filter[k])) {
      param.filter[k].map((v) => (url += `&${k}=${v}`));
    } else {
      url += `&${k}=${
        param.filter[k] === undefined || param.filter[k] === null
          ? ''
          : param.filter[k]
      }`;
    }
  });

  await client
    .get(url)
    .then((res) => {
      obj = {
        data: res.data.data,
        option: res.data.option,
        message: '',
      };
    })
    .catch((e) => {
      obj = {
        data: {},
        option: {},
        message: e.response.data.msg,
      };
    });

  return obj;
};

export const postHistoryData = async (obj) => {
  let result = {};
  await client
    .post('/api/analysis/history/new', JSON.stringify(obj), jsonConfig)
    .then(() => {
      result.status = RESPONSE_OK;
    })
    .catch(() => {
      result.status = RESPONSE_NG;
    });

  return result;
};

export const getOriginalData = async (param, type) => {
  let url,
    obj = {};

  if (type.match(/multi/) === null || type.match(/setting/)) {
    if (type.match(/multi/)) {
      url = `api/analysis/data/multi/${param.fId}?start=${param.start}&end=${param.end}&aggregation_key=${param.agMain}&aggregation_val=${param.agSub}`;
    } else {
      url = `api/analysis/data/${param.fId}/${param.rId}?start=${param.start}&end=${param.end}&aggregation_key=${param.agMain}&aggregation_val=${param.agSub}`;
    }

    Object.keys(param.filter).forEach((k) => {
      url += `&filter_key=${param.filter[k].target}`;
      if (Array.isArray(param.filter[k].selected)) {
        param.filter[k].selected.forEach(
          (v) => (url += `&${param.filter[k].target}=${v}`),
        );
      } else {
        url += `&${param.filter[k].target}=${
          param.filter[k].selected === undefined ||
          param.filter[k].selected === null
            ? ''
            : param.filter[k].selected
        }`;
      }
    });

    if (param.selected.length > 0) {
      param.selected.forEach((v) => (url += `&selected=${v}`));
    } else {
      url += `&selected=`;
    }
  } else {
    url = `api/analysis/data/multi/${param.fId}?start=${param.start}&end=${param.end}`;
  }

  await client
    .get(url)
    .then((res) => {
      obj = {
        data: res.data.data,
        option: res.data.option,
        items: res.data.visualization.items,
        common_axis_x: res.data.visualization.common_axis_x ?? [],
        message: '',
      };
    })
    .catch((e) => {
      obj = {
        data: {},
        option: {},
        items: [],
        common_axis_x: [],
        message: e.response.data.msg,
      };
    });

  return obj;
};
