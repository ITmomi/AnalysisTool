import { useState, useCallback } from 'react';
import {
  getValidPeriod,
  initialSettingAction,
  UpdateDurationReducer,
} from '../reducers/slices/SettingInfo';
import { useDispatch, useSelector } from 'react-redux';
import {
  getCurrentPath,
  getSupportUrl,
  UpdateCurrentPathReducer,
} from '../reducers/slices/BasicInfo';
import { getFindData } from '../lib/util/Util';
import { MSG_LOCAL, MSG_REMOTE, MSG_SQL } from '../lib/api/Define/Message';
import { E_MULTI_TYPE } from '../lib/api/Define/etc';

const initialState = {
  log_name: '',
  source: '',
  target_path: [],
  equipment_type: '',
};
const initialHistory = { id: undefined, resource: [] };

const useJobSettingInfo = () => {
  const [isOpenCreateJob, setCreateJob] = useState(false);
  const [jobResource, setJobResource] = useState(null);
  const [multiHistory, setMultiHistory] = useState(initialHistory);
  const [jobSettingInfo, setJobSettingInfo] = useState(initialState);
  const dispatch = useDispatch();
  const validPeriod = useSelector(getValidPeriod);
  const currentPath = useSelector(getCurrentPath);
  const urlList = useSelector(getSupportUrl);

  const setValidPeriod = useCallback(
    (value) => {
      dispatch(UpdateDurationReducer(value));
    },
    [dispatch],
  );
  const initValidPeriod = useCallback(() => {
    dispatch(initialSettingAction());
  }, [dispatch]);

  const setCurrentPath = useCallback(
    (value) => {
      dispatch(UpdateCurrentPathReducer(value));
    },
    [dispatch],
  );

  const openCreateJob = useCallback(() => {
    setCreateJob(true);
    setMultiHistory(initialHistory);
  }, [setCreateJob]);

  const closeCreateJob = useCallback(() => {
    setCreateJob(false);
  }, [setCreateJob]);
  const getSettingInfo = ({ source, setting, func_id }) => {
    const job = setting.formList.find((o) => o.key === source);
    const job_type = job?.type ?? job?.source_type ?? MSG_LOCAL;
    return job_type === MSG_LOCAL
      ? {
          job_type: MSG_LOCAL,
          source: source,
          source_type: MSG_LOCAL,
          log_name: getFindData(setting.form[source], 'log_name', undefined),
          func_id: func_id,
        }
      : job_type === MSG_REMOTE
      ? {
          job_type: MSG_REMOTE,
          source: source,
          source_type: MSG_REMOTE,
          db_id: getFindData(setting.form[source], 'db_id', undefined),
          table_name: getFindData(
            setting.form[source],
            'table_name',
            undefined,
          ),
          user_fab: getFindData(setting.form[source], 'user_fab', undefined),
          equipment_name: getFindData(setting.form[source], 'equipment_name'),
          period: getFindData(setting.form[source], 'period', undefined),
          selected: getFindData(setting.form[source], 'period', undefined),
          func_id: func_id,
        }
      : {
          job_type: MSG_SQL,
          source: source,
          source_type: MSG_SQL,
          db_id: getFindData(setting.form[source], 'db_id', undefined),
          sql: getFindData(setting.form[source], 'sql', undefined),
          func_id: func_id,
        };
  };
  const getSettingList = ({ resource }) => {
    return resource.formList
      .filter((element) => element?.history_id === undefined)
      .map((element) =>
        Object.assign(
          {},
          getSettingInfo({
            func_id: element.sub_func_id,
            source: element.key,
            setting: resource,
          }),
          element.source_type === MSG_LOCAL
            ? {
                multi_info_id: element.multi_info_id,
                tab_name: element.tab_name,
                rid: element.rid,
                fid: element.fid,
              }
            : {
                multi_info_id: element.multi_info_id,
                tab_name: element.tab_name,
                rid: element.rid,
              },
        ),
      );
  };
  const setJobSettingResource = useCallback(
    (setting, func_id, type) => {
      setJobResource(setting);
      setJobSettingInfo(
        type === E_MULTI_TYPE
          ? {
              job_type: E_MULTI_TYPE,
              source_type: E_MULTI_TYPE,
              list: getSettingList({ resource: setting }),
              func_id: func_id,
            }
          : getSettingInfo({
              func_id,
              source: type,
              setting,
            }),
      );
    },
    [setJobResource],
  );

  return {
    isOpenCreateJob,
    openCreateJob,
    closeCreateJob,
    jobResource,
    setJobSettingResource,
    multiHistory,
    setMultiHistory,
    jobSettingInfo,
    setJobSettingInfo,
    validPeriod,
    setValidPeriod,
    initValidPeriod,
    currentPath,
    setCurrentPath,
    urlList,
  };
};

export default useJobSettingInfo;
