import {
  initAnalysisAction,
  AnalysisSummaryData,
  AnalysisDetailData,
  DetailHeaderReducer,
  DetailDataReducer,
  SummaryDataReducer,
  SummaryHeaderReducer,
  SummarySubMenuReducer,
  AnalysisSummarySubItemData,
  SummaryArgsReducer,
  SummaryYAxiosReducer,
  DetailYAxiosReducer,
  DetailOptionReducer,
} from '../reducers/slices/AnalysisInfo';
import { useDispatch, useSelector } from 'react-redux';
import { useCallback } from 'react';

export default function useAnalysisInfo() {
  const dispatch = useDispatch();
  const SummaryData = useSelector(AnalysisSummaryData);
  const SummarySubItem = useSelector(AnalysisSummarySubItemData);
  const SummaryArgs = SummaryData.args;
  const SummaryYAxis = SummaryData.yAxis;

  const DetailData = useSelector(AnalysisDetailData);
  const DetailOptions = DetailData.selectedOptions;
  const DetailYAxis = DetailData.yAxis;
  const columnInfo = (type) =>
    type === 'summary' ? SummaryData.column : DetailData.column;
  const dataSource = (type) =>
    type === 'summary' ? SummaryData.dataSource : DetailData.dataSource;

  const setYAxisValue = useCallback(
    (type, value) => {
      type === 'summary'
        ? dispatch(SummaryYAxiosReducer(value))
        : dispatch(DetailYAxiosReducer(value));
    },
    [dispatch],
  );

  const setColumnInfo = useCallback(
    (type, value) => {
      type === 'summary'
        ? dispatch(SummaryHeaderReducer(value))
        : dispatch(DetailHeaderReducer(value));
    },
    [dispatch],
  );
  const setDataSource = useCallback(
    (type, value) => {
      type === 'summary'
        ? dispatch(SummaryDataReducer(value))
        : dispatch(DetailDataReducer(value));
    },
    [dispatch],
  );

  const initAnalysisValue = useCallback(() => {
    dispatch(initAnalysisAction());
  }, [dispatch]);

  const setSummarySubItem = useCallback(
    (value) => {
      dispatch(SummarySubMenuReducer(value));
    },
    [dispatch],
  );
  const setSummaryArgs = useCallback(
    (value) => {
      dispatch(SummaryArgsReducer(value));
    },
    [dispatch],
  );

  const setDetailOptions = useCallback(
    (value) => {
      dispatch(DetailOptionReducer(value));
    },
    [dispatch],
  );

  return {
    DetailYAxis,
    SummaryYAxis,
    setYAxisValue,
    initAnalysisValue,
    columnInfo,
    dataSource,
    setDataSource,
    setColumnInfo,
    SummaryData,
    DetailData,
    SummarySubItem,
    setSummarySubItem,
    SummaryArgs,
    setSummaryArgs,
    DetailOptions,
    setDetailOptions,
  };
}
