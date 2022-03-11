import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import * as slice from '../reducers/slices/ResultInfo';

const useResultInfo = () => {
  const dispatch = useDispatch();

  const setAnalysisInfo = useCallback(
    (v) => {
      dispatch(slice.UpdateAnalysisReducer(v));
    },
    [dispatch],
  );

  const setOriginalInfo = useCallback(
    (v) => {
      dispatch(slice.UpdateOriginalReducer(v));
    },
    [dispatch],
  );

  const setSelectedRow = useCallback(
    (v) => {
      dispatch(slice.UpdateSelectedRowReducer(v));
    },
    [dispatch],
  );

  const setOriginalFilteredRows = useCallback(
    (v) => {
      dispatch(slice.UpdateOriginalFilteredRowsReducer(v));
    },
    [dispatch],
  );

  const setAnalysisGraphInfo = useCallback(
    (v) => {
      dispatch(slice.UpdateAnalysisGraphInfoReducer(v));
    },
    [dispatch],
  );

  const setOriginalGraphInfo = useCallback(
    (v) => {
      dispatch(slice.UpdateOriginalGraphInfoReducer(v));
    },
    [dispatch],
  );

  const setSavedAnalysisAggregation = useCallback(
    (v) => {
      dispatch(slice.UpdateSavedAnalysisAggregationReducer(v));
    },
    [dispatch],
  );

  const setVisualization = useCallback(
    (v) => {
      dispatch(slice.UpdateVisualizationReducer(v));
    },
    [dispatch],
  );

  const initializing = useCallback(() => {
    dispatch(slice.initialAction());
  }, [dispatch]);

  return {
    analysisData: useSelector((state) => state.ResultInfo.analysis),
    originalData: useSelector((state) => state.ResultInfo.original),
    selectedRow: useSelector((state) => state.ResultInfo.selectedRow),
    originalFilteredRows: useSelector(
      (state) => state.ResultInfo.originalFilteredRows,
    ),
    analysisGraphInfo: useSelector(
      (state) => state.ResultInfo.analysisGraphInfo,
    ),
    originalGraphInfo: useSelector(
      (state) => state.ResultInfo.originalGraphInfo,
    ),
    savedAnalysisAggregation: useSelector(
      (state) => state.ResultInfo.savedAnalysisAggregation,
    ),
    visualization: useSelector((state) => state.ResultInfo.visualization),
    setAnalysisInfo,
    setOriginalInfo,
    setSelectedRow,
    setOriginalFilteredRows,
    setAnalysisGraphInfo,
    setOriginalGraphInfo,
    setSavedAnalysisAggregation,
    setVisualization,
    initializing,
  };
};

export default useResultInfo;
