import React, { useState } from 'react';
import { JobSetting } from '../../UI/organisms';
import ProgressModal from '../../UI/organisms/ProgressModal';
import { useHistory, useLocation } from 'react-router';
import {
  getEquipmentValidDate,
  getEquipmentList,
} from '../../../lib/api/axios/requests';
import useJobSettingInfo from '../../../hooks/useJobSettingInfo';
import {
  arrayRemove,
  arrayShift,
  arrayUnshift,
  getParseData,
} from '../../../lib/util/Util';
import { ANALYSIS, MAIN, PROCESS } from '../../../lib/api/Define/URL';
import NotificationBox from '../../UI/molecules/NotificationBox/Notification';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { QUERY_KEY } from '../../../lib/api/Define/QueryKey';
import {
  getConvertJobStatus,
  getRequestIdFromJobSetting,
  getResource_JobSetting,
  uploadFiles_JobSetting,
  deleteHistoryJob,
  update_multiJobInfo,
} from '../../../lib/api/axios/useJobSettingRequest';
import {
  MSG_HISTORY,
  MSG_LOCAL,
  MSG_MULTI,
  MSG_REMOTE,
  MSG_SQL,
} from '../../../lib/api/Define/Message';
import { E_MULTI_TYPE, R_OK } from '../../../lib/api/Define/etc';

const Job = () => {
  const [isProcessJob, setProcessJob] = useState(false);
  const [refetchInterval, setRefetchInterval] = useState(0);
  const [reloadEquipment, setReloadEquipment] = useState(false);
  const [reloadPeriod, setReloadPeriod] = useState(false);
  const history = useHistory();
  const location = useLocation();
  const queryClient = useQueryClient();
  const {
    isOpenCreateJob,
    closeCreateJob,
    openCreateJob,
    setJobSettingResource,
    jobSettingInfo,
    setJobSettingInfo,
    currentPath,
    setCurrentPath,
    urlList,
    jobResource,
    multiHistory,
    setMultiHistory,
  } = useJobSettingInfo();

  const jobSettingResource = useQuery(
    [QUERY_KEY.JOBSETTING_INIT, currentPath[0]],
    () => getResource_JobSetting({ func_id: currentPath[0] }),
    {
      enabled: !!(
        urlList?.map((obj) => obj.func).includes(currentPath[0]) ?? false
      ),
      onError: (error) => {
        NotificationBox('ERROR', error.message, 4.5);
      },
      onSuccess: ({ info }) => {
        const current_func = currentPath[0];
        openCreateJob();
        setReloadPeriod(false);
        setReloadEquipment(false);
        setJobSettingResource(
          info,
          current_func,
          urlList.find((o) => o.func === current_func).source,
        );
      },
    },
  );
  useQuery(
    [
      QUERY_KEY.JOBSETTING_USER_FAB_EQUIPMENT_LIST,
      jobSettingInfo?.db_id,
      jobSettingInfo?.table_name,
    ],
    () =>
      getEquipmentList({
        db_id:
          jobSettingInfo?.source_type === E_MULTI_TYPE
            ? jobSettingInfo.list.find(
                (o) => o.source === jobSettingInfo.source,
              )?.db_id
            : jobSettingInfo?.db_id,
        table_name:
          jobSettingInfo?.source_type === E_MULTI_TYPE
            ? jobSettingInfo.list.find(
                (o) => o.source === jobSettingInfo.source,
              )?.table_name
            : jobSettingInfo?.table_name,
      }),
    {
      enabled: reloadEquipment && jobSettingInfo?.job_type === MSG_REMOTE,
      onError: (error) => {
        NotificationBox('ERROR', error.message, 4.5);
      },
      onSuccess: ({ info }) => {
        setJobSettingInfo((prev) =>
          jobSettingInfo?.source_type === E_MULTI_TYPE
            ? {
                ...prev,
                list: prev?.list.map((o) =>
                  o.source === prev.source ? { ...o, info: info } : o,
                ),
              }
            : { ...prev, info: info },
        );
      },
      onSettled: () => {
        setReloadEquipment(false);
      },
    },
  );

  useQuery(
    [
      QUERY_KEY.JOBSETTING_EQUIPMENT_VALID_DATE,
      jobSettingInfo?.db_id,
      jobSettingInfo?.table_name,
    ],
    () =>
      getEquipmentValidDate({
        db_id:
          jobSettingInfo?.source_type === E_MULTI_TYPE
            ? jobSettingInfo.list.find(
                (o) => o.source === jobSettingInfo.source,
              )?.db_id
            : jobSettingInfo?.db_id,
        table_name:
          jobSettingInfo?.source_type === E_MULTI_TYPE
            ? jobSettingInfo.list.find(
                (o) => o.source === jobSettingInfo.source,
              )?.table_name
            : jobSettingInfo?.table_name,
        equipment_name:
          jobSettingInfo?.source_type === E_MULTI_TYPE
            ? jobSettingInfo.list.find(
                (o) => o.source === jobSettingInfo.source,
              )?.equipment_name
            : jobSettingInfo?.equipment_name,
      }),
    {
      enabled: reloadPeriod && jobSettingInfo?.job_type === MSG_REMOTE,
      onError: (error) => {
        NotificationBox('ERROR', error.message, 4.5);
      },
      onSuccess: ({ info }) => {
        const obj = {
          period: { start: info.start, end: info.end },
          selected: { start: info.start, end: info.end },
        };
        setJobSettingInfo((prev) =>
          jobSettingInfo?.source_type === E_MULTI_TYPE
            ? {
                ...prev,
                list: prev?.list.map((o) =>
                  o.source === prev.source ? { ...o, ...obj } : o,
                ),
              }
            : { ...prev, ...obj },
        );
      },
      onSettled: () => {
        setReloadPeriod(false);
      },
    },
  );
  const deleteHistory = useMutation(
    [QUERY_KEY.JOBSETTING_DELETE_HISTORY],
    (historyId) => deleteHistoryJob({ HistoryId: historyId }),
    {
      onError: (error) => {
        NotificationBox('ERROR', error.message, 4.5);
      },
      onSuccess: (status) => {
        if (status === R_OK) {
          queryClient
            .invalidateQueries([QUERY_KEY.JOBSETTING_INIT, currentPath[0]])
            .then((_) => _);
        }
      },
    },
  );
  const convertJobStatus = useQuery(
    [QUERY_KEY.JOBSETTING_CONVERT_JOB_STATUS, jobSettingInfo?.job_id],
    () => getConvertJobStatus({ jobId: jobSettingInfo?.job_id }),
    {
      enabled:
        jobSettingInfo?.job_type === MSG_LOCAL &&
        !!(jobSettingInfo?.job_id ?? false) &&
        isProcessJob,
      refetchInterval: refetchInterval,
      onSuccess: (data) => {
        if (data.percent === '100' && data.status !== 'running') {
          setRefetchInterval(0);
        }
      },
      onError: (error) => {
        NotificationBox('ERROR', error.message, 4.5);
        setRefetchInterval(0);
      },
    },
  );
  const updateMultiJobInfo = useMutation(
    [QUERY_KEY.JOBSETTING_MULTIJOB_UPDATE],
    ({ id, obj, rid }) =>
      update_multiJobInfo({ func_id: id, object: obj, rid }),
  );

  const localJobConvert = useMutation(
    [QUERY_KEY.JOBSETTING_LOCAL_JOB],
    ({ upload_id, jobInfo }) =>
      getRequestIdFromJobSetting({
        source:
          jobSettingInfo?.source_type === E_MULTI_TYPE
            ? jobInfo?.job_type
            : jobInfo?.source,
        object: jobInfo,
        files: upload_id,
      }),
    {
      onError: (error) => {
        NotificationBox('ERROR', error.message, 4.5);
      },
      onSuccess: ({ rid }) => {
        console.log('[jobConvert]JobId', rid);
        setJobSettingInfo({ ...jobSettingInfo, job_id: rid });
        setRefetchInterval(1000);
      },
    },
  );
  const jobFileUpload = useMutation(
    [QUERY_KEY.JOBSETTING_FILE_UPLOAD],
    (jobInfo) =>
      uploadFiles_JobSetting(jobInfo?.file_name ?? undefined, jobInfo),
    {
      onError: (error) => {
        NotificationBox('ERROR', error.message, 4.5);
      },
      onSuccess: ({ upload_id, jobInfo }) => {
        if (jobSettingInfo?.source_type === E_MULTI_TYPE) {
          setJobSettingInfo((prevState) => ({
            ...prevState,
            list: prevState?.list.map((o) =>
              o.source === jobInfo.source ? { ...o, fid: upload_id } : o,
            ),
          }));
        }
        localJobConvert.mutate({ upload_id: upload_id, jobInfo });
      },
    },
  );

  const remoteJob = useMutation(
    [QUERY_KEY.JOBSETTING_REMOTE_JOB],
    ({ source, jobInfo }) =>
      getRequestIdFromJobSetting({ source: source, object: jobInfo }),
    {
      onError: (error) => {
        NotificationBox('ERROR', error.message, 4.5);
      },
      onSuccess: ({ rid }) => {
        if (jobSettingInfo?.source_type !== E_MULTI_TYPE) {
          goAnalysisPage(
            jobSettingInfo.job_type,
            urlList.find((obj) => obj.func === jobSettingInfo.func_id) ?? {
              func: '',
              path: [],
            },
            rid,
          );
          closeCreateJob();
        }
      },
    },
  );
  const getListData = (list) => {
    const common = (obj) => {
      return {
        source_type: obj.source_type,
        tab_name: obj.tab_name,
        rid: obj.rid,
        sub_func_id: obj?.func_id ?? obj?.sub_func_id,
      };
    };
    return list.map((obj) =>
      obj.source_type === MSG_LOCAL
        ? { ...common(obj), fid: obj.fid }
        : obj.source_type === MSG_REMOTE
        ? {
            ...common(obj),
            db_id: obj.db_id,
            table_name: obj.table_name,
            equipment_name: obj.equipment_name,
            period_start: obj?.selected?.start ?? obj.period_start,
            period_end: obj?.selected?.end ?? obj.period_end,
          }
        : obj.source_type === MSG_SQL
        ? { ...common(obj), db_id: obj.db_id, sql: obj.sql }
        : {},
    );
  };
  const goAnalysisPage = (type, jobPath, rid) => {
    if (jobPath.func !== '') {
      const newPath = currentPath.slice(currentPath.indexOf(MAIN)); //
      newPath.unshift(jobPath.func); //
      newPath.unshift(ANALYSIS); //
      setCurrentPath(newPath);
    }
    const getMultiListInfo = () => {
      if (jobSettingInfo.job_type === MSG_HISTORY) {
        const sHistory = multiHistory.resource.find(
          (o) => o.id === jobSettingInfo.history_id,
        );
        return getListData(sHistory.info.formList);
      } else return getListData(jobSettingInfo.list);
    };

    if (type === E_MULTI_TYPE || (rid ?? false)) {
      history.push({
        pathname: ANALYSIS,
        state:
          type === E_MULTI_TYPE
            ? {
                history_id: `${jobSettingInfo?.history_id ?? undefined}`,
                job_type: E_MULTI_TYPE,
                func_id: `${jobSettingInfo.func_id}`,
                list: getMultiListInfo(),
              }
            : {
                history_id: `${jobSettingInfo?.history_id ?? undefined}`,
                equipment_name: `${
                  jobSettingInfo?.equipment_name ?? undefined
                }`,
                job_type: `${
                  jobSettingInfo?.source_type ?? jobSettingInfo?.source
                }`,
                func_id: `${jobSettingInfo.func_id}`,
                job_id: `${rid}`,
                db_id: `${jobSettingInfo?.db_id ?? undefined}`,
                sql: `${jobSettingInfo?.sql ?? undefined}`,
              },
      });
    } else {
      NotificationBox('ERROR', 'Failed to create jobID', 4.5);
    }
  };

  const startEnableCheck = () => {
    const source = jobSettingInfo?.source ?? MSG_MULTI;
    const job =
      jobSettingInfo?.source_type === E_MULTI_TYPE
        ? jobSettingInfo?.MULTI_TAB === MSG_HISTORY
          ? multiHistory.resource.find(
              (o) => o.id === jobSettingInfo.history_id,
            )?.info
          : {}
        : jobSettingInfo;
    if (source === MSG_LOCAL) {
      return Boolean(
        !!job?.file_name &&
          !!job?.log_name &&
          deleteHistory.isLoading === false,
      );
    } else if (source === MSG_REMOTE) {
      return Boolean(
        !!job?.db_id &&
          !!job?.equipment_name &&
          deleteHistory.isLoading === false,
      );
    } else if (source === MSG_SQL) {
      return Boolean(
        !!job?.db_id && !!job?.sql && deleteHistory.isLoading === false,
      );
    } else if (job === undefined) {
      return false;
    } else {
      //history??
      console.log('jobSetting source(job_type): ', jobSettingInfo?.job_type);
      return Boolean(deleteHistory.isLoading === false);
    }
  };
  const startAnalysis = async () => {
    if ((jobSettingInfo?.source ?? jobSettingInfo?.source_type) === MSG_LOCAL) {
      closeJobModal({ next: PROCESS });
      setProcessJob(true);
      jobFileUpload.mutate(jobSettingInfo);
    } else if (jobSettingInfo?.source_type === MSG_MULTI) {
      if (jobSettingInfo?.job_type !== MSG_HISTORY) {
        closeJobModal({ next: PROCESS });
        setProcessJob(true);
      } else {
        closeJobModal({ next: undefined });
        goAnalysisPage(
          E_MULTI_TYPE,
          urlList.find((obj) => obj.func === jobSettingInfo.func_id) ?? {
            func: '',
            path: [],
          },
          undefined,
        );
      }
    } else {
      closeJobModal({ next: undefined });
      await remoteJob.mutate({
        source: jobSettingInfo.job_type,
        jobInfo: jobSettingInfo,
      });
    }
  };

  const closeJobModal = ({ next }) => {
    closeCreateJob();
    Array.isArray(next)
      ? setCurrentPath(next)
      : next === undefined
      ? setCurrentPath(arrayShift(currentPath))
      : setCurrentPath(arrayUnshift(currentPath, next));
  };

  const endProcessModal = async (status, converted) => {
    if (status === 'COMPLETE' && converted > 0) {
      const jobPath = urlList.find(
        (obj2) => obj2.func === jobSettingInfo?.func_id,
      ) ?? { func: '', path: [] };
      if (jobPath.func !== undefined) {
        const newPath = currentPath.slice(currentPath.indexOf(MAIN));
        newPath.unshift(jobPath.func);
        newPath.unshift(ANALYSIS);
        setCurrentPath(newPath);
      }
      history.push({
        pathname: ANALYSIS,
        state: {
          job_type: `${
            jobSettingInfo?.source_type ?? jobSettingInfo?.type ?? 'local'
          }`,
          func_id: `${jobSettingInfo?.func_id ?? undefined}`,
          job_id: `${jobSettingInfo.job_id}`,
          path: jobPath?.path ?? [],
          list:
            jobSettingInfo?.source_type === MSG_MULTI
              ? getListData(jobSettingInfo.list)
              : undefined,
        },
      });
      setProcessJob(false);
      setJobSettingInfo(undefined);
    } else if (converted === -1) {
      setCurrentPath(arrayRemove(currentPath, location.pathname));
      setProcessJob(false);
      setJobSettingInfo(undefined);
    }
  };

  const contentChange = (event) => {
    const item = getParseData(event);
    console.log('contentChange', item);
    if (item.id === 'source') {
      const { formList } = jobResource;
      const JobInfo = formList.find((obj) => obj.key === item.value);
      console.log('JobInfo', JobInfo);
      setJobSettingInfo((prevState) =>
        JobInfo?.type ?? JobInfo?.job_type === 'history'
          ? {
              ...prevState,
              [item.id]: item.value,
              ['history_id']: JobInfo.history_id,
              ['job_type']: JobInfo?.type ?? JobInfo?.source_type,
            }
          : {
              ...prevState,
              [item.id]: item.value,
              ['job_type']: JobInfo?.type ?? JobInfo?.source_type,
            },
      );
    } else if (item.id === 'HISTORY') {
      setJobSettingInfo((prevState) => ({
        ...prevState,
        ['history_id']: item.value,
        ['job_type']: 'history',
      }));
    } else if (item.id === 'DELETE_HISTORY') {
      const { formList } = jobResource;
      const JobInfo = formList.find((obj) => obj.key === item.value) ?? {};
      deleteHistory.mutate(JobInfo.history_id);
    } else if (item.id === 'db_id') {
      const obj = {
        db_id: item.value,
        equipment_name: '',
        user_fab: '',
        selected: { start: '', end: '' },
        period: { start: '', end: '' },
      };
      setJobSettingInfo((prevState) =>
        jobSettingInfo?.source_type === E_MULTI_TYPE
          ? {
              ...prevState,
              list: prevState?.list.map((o) =>
                o.source === jobSettingInfo.source
                  ? { ...o, ...obj, rid: undefined }
                  : o,
              ),
            }
          : { ...prevState, ...obj },
      );
      setReloadEquipment(true);
    } else if (item.id === 'user_fab') {
      const obj = {
        equipment_name: '',
        user_fab: item.value,
        selected: { start: '', end: '' },
        period: { start: '', end: '' },
      };
      setJobSettingInfo((prevState) =>
        jobSettingInfo?.source_type === E_MULTI_TYPE
          ? {
              ...prevState,
              list: prevState?.list.map((o) =>
                o.source === prevState.source
                  ? { ...o, ...obj, rid: undefined }
                  : o,
              ),
            }
          : { ...prevState, ...obj },
      );
    } else if (item.id === 'equipment_name') {
      const obj = {
        equipment_name: item.value,
        selected: { start: '', end: '' },
        period: { start: '', end: '' },
      };
      setJobSettingInfo((prevState) =>
        jobSettingInfo?.source_type === E_MULTI_TYPE
          ? {
              ...prevState,
              list: prevState?.list.map((o) =>
                o.source === prevState.source
                  ? { ...o, ...obj, rid: undefined }
                  : o,
              ),
            }
          : { ...prevState, ...obj },
      );
      setReloadPeriod(true);
    } else if (item.id === 'period') {
      setJobSettingInfo((prevState) =>
        jobSettingInfo?.source_type === E_MULTI_TYPE
          ? {
              ...prevState,
              list: prevState?.list.map((o) =>
                o.source === prevState.source
                  ? { ...o, selected: item.value, rid: undefined }
                  : o,
              ),
            }
          : { ...prevState, selected: item.value },
      );
    } else if (item.id === 'src_file') {
      setJobSettingInfo((prevState) =>
        jobSettingInfo?.source_type === E_MULTI_TYPE
          ? {
              ...prevState,
              list: prevState?.list.map((o) =>
                o.source === prevState.source
                  ? {
                      ...o,
                      file_name: item.value,
                      rid: undefined,
                      fid: undefined,
                    }
                  : o,
              ),
            }
          : {
              ...prevState,
              file_name: item.value,
            },
      );
    } else {
      setJobSettingInfo((prevState) => ({
        ...prevState,
        [item.id]: item.value,
      }));
    }
  };

  const checkAnalysisStatus = async (
    setStatusFunc,
    setPercentFunc,
    contentsFunc,
  ) => {
    setStatusFunc(convertJobStatus?.data?.status ?? undefined);
    setPercentFunc(convertJobStatus?.data?.percent ?? 0);
    contentsFunc(convertJobStatus?.data?.detail ?? undefined);
  };

  const checkMultiAnalysisStatus = async (
    setStatusFunc,
    setCurrentFunc,
    currentJob,
  ) => {
    let nextJob = jobSettingInfo.list.find((o) => o.rid === undefined);
    if (currentJob === undefined) {
      if (nextJob === undefined) {
        goAnalysisPage(
          E_MULTI_TYPE,
          urlList.find((obj) => obj.func === jobSettingInfo.func_id) ?? {
            func: '',
            path: [],
          },
          undefined,
        );
        setRefetchInterval(0);
        setProcessJob(false);
      } else {
        if (nextJob.job_type === MSG_LOCAL) {
          jobFileUpload.mutate(nextJob);
          setCurrentFunc(nextJob.source);
        } else if ([MSG_REMOTE, MSG_SQL].includes(nextJob.job_type)) {
          remoteJob.mutate({ source: nextJob.job_type, jobInfo: nextJob });
          setCurrentFunc(nextJob.source);
        }
      }
    } else {
      const Job = jobSettingInfo.list.find((o) => o.source === currentJob);
      if (Job.job_type === MSG_LOCAL) {
        const statusData = convertJobStatus?.data ?? {
          percent: 0,
          status: 'running',
        };
        if (
          statusData.percent === '100' &&
          statusData.status === 'success' &&
          (nextJob?.source ?? undefined) === currentJob
        ) {
          try {
            if (updateMultiJobInfo.isIdle) {
              await updateMultiJobInfo.mutate({
                id: jobSettingInfo.func_id,
                obj: Job,
                rid: jobSettingInfo.job_id,
              });
            } else if (updateMultiJobInfo.isSuccess) {
              setJobSettingInfo((prevState) => ({
                ...prevState,
                list: prevState?.list.map((o) =>
                  o.source === currentJob
                    ? { ...o, rid: prevState?.job_id ?? undefined }
                    : o,
                ),
                job_id: undefined,
              }));
              setCurrentFunc(undefined);
            }
          } catch (e) {
            console.log(e);
          }
        } else if (statusData.status === 'error') {
          setStatusFunc(statusData.status);
          setRefetchInterval(0);
        }
      } else if (
        [MSG_REMOTE, MSG_SQL].includes(Job.job_type) &&
        (remoteJob.data?.rid ?? false)
      ) {
        if (updateMultiJobInfo.isIdle) {
          await updateMultiJobInfo.mutate({
            id: jobSettingInfo.func_id,
            obj: Job,
            rid: jobSettingInfo.job_id,
          });
        } else if (updateMultiJobInfo.isSuccess) {
          setJobSettingInfo((prevState) => ({
            ...prevState,
            list: prevState?.list.map((o) =>
              o.source === currentJob ? { ...o, rid: remoteJob.data?.rid } : o,
            ),
            job_id: undefined,
          }));
          setCurrentFunc(undefined);
        }
      }
    }
  };

  if (jobSettingResource.isLoading) return <></>;
  return (
    <>
      {' '}
      <JobSetting
        isOpen={isOpenCreateJob}
        startFunc={startAnalysis}
        closeFunc={closeJobModal}
        changeFunc={contentChange}
        resource={jobResource}
        info={jobSettingInfo}
        history={{ info: multiHistory, setfunc: setMultiHistory }}
        enableCheckFunc={startEnableCheck}
      />
      <ProgressModal
        isOpen={isProcessJob}
        closeFunc={endProcessModal}
        statusFunc={
          jobSettingInfo?.source_type === E_MULTI_TYPE
            ? checkMultiAnalysisStatus
            : checkAnalysisStatus
        }
        info={jobSettingInfo}
      />
    </>
  );
};

export default Job;
