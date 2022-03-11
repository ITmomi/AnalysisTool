import {
  deleteRequest,
  getRequest,
  postRequestFormData,
  postRequestItems,
  putRequestItems,
} from './requests';
import {
  URL_IMPORT_DBTABLE,
  URL_SETTING_CHECK_DB_CONNECTION,
  URL_SETTING_GET_LOCAL,
  URL_SETTING_GET_REMOTE,
  URL_SETTING_GET_TABLES,
} from '../Define/URL';

export const dbConnectionCheck = async (data) => {
  const { info } = await postRequestItems({
    items: data,
    url: URL_SETTING_CHECK_DB_CONNECTION,
  });
  return info;
};
export const getLocalDBInfo = async () => {
  const { info } = await getRequest(URL_SETTING_GET_LOCAL);
  return info;
};
export const getRemoteDBInfo = async ({ db_id }) => {
  const { info } = await getRequest(
    db_id === undefined
      ? URL_SETTING_GET_REMOTE
      : `${URL_SETTING_GET_REMOTE}/${db_id}`,
  );
  return info;
};
export const getDBTableInfo = async () => {
  const { info } = await getRequest(URL_SETTING_GET_TABLES);
  return info;
};

export const updateDBInfo = async ({ items, url }) => {
  const { status } = await putRequestItems({ items: items, url: url });
  return status;
};

export const deleteDBInfo = async ({ url, db_id }) => {
  const { info } = await deleteRequest(url, db_id);
  return info;
};

export const addDBInfo = async ({ items, url }) => {
  const { status } = await postRequestItems({ items: items, url: url });
  return status;
};
export const getDBStatus = async ({ url, db_id }) => {
  if (db_id ?? false) {
    const { info } = await getRequest(`${url}/${db_id}/status`);
    return {
      info: info,
      id: db_id,
    };
  }
};

export const importDBInfo = async (file) => {
  const { info } = await postRequestFormData(URL_IMPORT_DBTABLE, file);
  return info;
};
