import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  getConfigStepInfo,
  UpdateStepConfigReducer,
  getConvertStepInfo,
  UpdateConvertStepInfoReducer,
  getFilterStepInfo,
  UpdateFilterStepInfoReducer,
  UpdateAnalysisStepInfoReducer,
  getAnalysisStepInfo,
  getVisualStepInfo,
  UpdateVisualStepInfoReducer,
  getFuncStepInfo,
  UpdateFuncStepReducer,
  initialAction,
} from '../reducers/slices/RuleSettingInfo';

const useRuleSettingInfo = () => {
  const dispatch = useDispatch();
  const ruleStepConfig = useSelector(getConfigStepInfo);
  const convertStepInfo = useSelector(getConvertStepInfo);
  const filterStepInfo = useSelector(getFilterStepInfo);
  const analysisStepInfo = useSelector(getAnalysisStepInfo);
  const visualStepInfo = useSelector(getVisualStepInfo);
  const funcStepInfo = useSelector(getFuncStepInfo);

  const initialRuleSetting = useCallback(() => {
    dispatch(initialAction());
  }, [dispatch]);

  const setRuleStepConfig = useCallback(
    (value) => {
      console.log('setRuleStepConfig', value);
      dispatch(UpdateStepConfigReducer(value));
    },
    [dispatch],
  );

  const updateFuncInfo = useCallback(
    (object) => {
      dispatch(UpdateFuncStepReducer(object));
    },
    [dispatch],
  );

  const updateConvertInfo = useCallback(
    (object) => {
      dispatch(UpdateConvertStepInfoReducer(object));
    },
    [dispatch],
  );
  const updateFilterInfo = useCallback(
    (object) => {
      dispatch(UpdateFilterStepInfoReducer(object));
    },
    [dispatch],
  );
  const updateAnalysisInfo = useCallback(
    (object) => {
      dispatch(UpdateAnalysisStepInfoReducer(object));
    },
    [dispatch],
  );
  const updateVisualInfo = useCallback(
    (object) => {
      dispatch(UpdateVisualStepInfoReducer(object));
    },
    [dispatch],
  );

  return {
    setRuleStepConfig,
    ruleStepConfig,
    updateConvertInfo,
    convertStepInfo,
    updateFilterInfo,
    filterStepInfo,
    updateAnalysisInfo,
    analysisStepInfo,
    updateVisualInfo,
    visualStepInfo,
    updateFuncInfo,
    funcStepInfo,
    initialRuleSetting,
  };
};

export default useRuleSettingInfo;
