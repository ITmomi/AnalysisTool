import useRuleSettingInfo from './useRuleSettingInfo';
import { sortArrayOfObjects } from '../lib/util/Util';
import { createGraphItems } from '../components/pages/JobAnalysis/functionGroup';

const useJobStepSettingInfo = () => {
  const {
    ruleStepConfig,
    setRuleStepConfig,
    updateConvertInfo,
    updateAnalysisInfo,
    updateVisualInfo,
    updateFilterInfo,
    analysisStepInfo,
    convertStepInfo,
  } = useRuleSettingInfo();

  const addNextStepConfig = ({ next, info, setCurrent }) => {
    addStepPreviewAndNext({
      next: next,
      info: info,
      preview: undefined,
    });

    /* const isNextStepExist =
      ruleStepConfig.findIndex((obj) => obj.step === next) !== -1;
    if (isNextStepExist) {
      setRuleStepConfig(
        ruleStepConfig.map((target) =>
          target.step === next ? { ...target, config: info.config } : target,
        ),
      );
    } else {
      setRuleStepConfig(
        ruleStepConfig.concat({ step: next, config: info.config }),addStepPreviewAndNext
      );
    }*/
    setCurrent(next);
  };
  const addCurrentStepPreview = ({ current, info }) => {
    addStepPreviewAndNext({
      next: undefined,
      info: undefined,
      preview: { current: current, info: info },
    });
    /*    const isStepExist =
      ruleStepConfig.findIndex((obj) => obj.step === current) !== -1;
    if (isStepExist) {
      setRuleStepConfig(
        ruleStepConfig.map((obj2) =>
          obj2.step === current ? { ...obj2, data: info } : obj2,
        ),
      );
    } else {
      setRuleStepConfig(ruleStepConfig.concat({ step: current, data: info }));
    }*/
  };

  const addStepPreviewAndNext = ({ next, info, preview }) => {
    let ruleStep = [...ruleStepConfig];
    let cloneObj = {};

    if (preview?.current ?? false) {
      const { current: previewStep, info: previewInfo } = preview;
      const isPreviewStep =
        ruleStep.findIndex((obj) => obj.step === previewStep) !== -1;
      cloneObj = isPreviewStep
        ? ruleStep.map((obj2) =>
            obj2.step === previewStep ? { ...obj2, data: previewInfo } : obj2,
          )
        : ruleStep.concat({ step: previewStep, data: previewInfo });
      ruleStep = JSON.parse(JSON.stringify(cloneObj));
    }
    if (info ?? false) {
      const isNextStep = ruleStep.findIndex((obj) => obj.step === next) !== -1;
      cloneObj = isNextStep
        ? ruleStep.map((target) =>
            target.step === next ? { ...target, config: info.config } : target,
          )
        : ruleStep.concat({ step: next, config: info.config });
    }
    setRuleStepConfig(cloneObj);
  };

  const updateStepSetting = ({ info }) => {
    console.log('updateStepSetting ', info);
    if (info?.convert?.log_define ?? false) {
      console.log('update convert ');
      updateConvertInfo({
        ...convertStepInfo,
        log_define: {
          ...convertStepInfo.log_define,
          ...info?.convert?.log_define,
        },
        info:
          sortArrayOfObjects(info?.convert?.info ?? [], 'col_index').map(
            (obj, index) => {
              return {
                ...obj,
                key: index + 1,
                rec_type: 'DB',
                output_column_val: obj?.output_column ?? '',
              };
            },
          ) ?? [],
        header:
          sortArrayOfObjects(info?.convert?.header ?? [], 'col_index').map(
            (obj, index) => {
              return {
                ...obj,
                key: index + 1,
                rec_type: 'DB',
                output_column_val: obj?.output_column ?? '',
              };
            },
          ) ?? [],
        custom:
          info?.convert?.custom?.map((obj, index) => {
            return {
              ...obj,
              key: index + 1,
              rec_type: 'DB',
              output_column_val: obj?.output_column ?? '',
            };
          }) ?? [],
      });
    }
    console.log('update convert completed');

    if (
      (info?.analysis?.setting?.filter_default ||
        info?.analysis?.setting?.aggregation_default) ??
      false
    ) {
      console.log('update analysis ');
      updateAnalysisInfo({
        ...analysisStepInfo,
        setting: {
          filter_default: info?.analysis?.setting?.filter_default,
          aggregation_default: info?.analysis?.setting?.aggregation_default,
          items: info?.analysis?.setting?.items.map((obj, index) => {
            return { ...obj, key: index + 1 };
          }),
        },
      });
    }
    console.log('update analysis completed');

    if (info?.filter?.items ?? false) {
      console.log('update filter ');
      updateFilterInfo(
        info?.filter?.items.map((obj, index) => {
          return {
            ...obj,
            key: index + 1,
          };
        }) ?? [],
      );
    }
    console.log('update filter completed');

    if (info?.visualization ?? false) {
      console.log('update visualization ');
      updateVisualInfo({
        function_graph_type:
          info.visualization.function_graph_type.map((v) => {
            v.script = v.script
              .replaceAll(/""/g, '"')
              .replaceAll(/(^")|("$)/g, '');
            return v;
          }) ?? [],
        graph_list: info.visualization.graph_list ?? [],
        items: createGraphItems(info.visualization),
      });
      console.log('update visualization completed');
    }
  };

  return {
    addNextStepConfig,
    addCurrentStepPreview,
    updateStepSetting,
    addStepPreviewAndNext,
  };
};
export default useJobStepSettingInfo;
