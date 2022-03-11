import { useCallback, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  AnalysisSummaryData,
  SummaryArgsReducer,
} from '../reducers/slices/AnalysisInfo';
import {getCurrentPath, getSupportUrl} from "../reducers/slices/BasicInfo";

const initialState = {
  log_name: '',
  job_id: '',
  jobList: [],
  periodSetting:[]
};
export default function useJobStatus() {
  const [JobList, setJobList] = useState(null);
  const [subSetting, setSubSetting] = useState([]);
  const [detailJobInfo, setDetail] = useState(null);
  const SummaryData = useSelector(AnalysisSummaryData);
  const SummaryArgs = SummaryData.args;
  const currentPath = useSelector(getCurrentPath);
  const supportUrl = useSelector(getSupportUrl);

  const dispatch = useDispatch();

  const setSummaryArgs = useCallback(
    (value) => {
      dispatch(SummaryArgsReducer(value));
    },
    [dispatch],
  );

  const initJobListInfo = useCallback(() => {
    setJobList(initialState);
  }, [setJobList]);

  const setJobListInfo = useCallback(
    (jobList) => {
      setJobList(jobList);
    },
    [JobList],
  );

  const settingItems = useCallback(
    (items) => {
      setSubSetting(items);
    },
    [subSetting],
  );

  const initDetailJobInfo = useCallback(() => {
    setDetail(null);
  }, []);

  const setDetailJobInfo = useCallback(
    (detail) => {
      setDetail(detail);
    },
    [detailJobInfo],
  );

  return {
    JobList,
    initJobListInfo,
    setJobListInfo,

    detailJobInfo,
    setDetailJobInfo,
    initDetailJobInfo,

    subSetting,
    settingItems,
    SummaryArgs,
    setSummaryArgs,
    currentPath,
    supportUrl,
  };
}
