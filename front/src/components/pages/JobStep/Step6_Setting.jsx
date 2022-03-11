import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Empty } from 'antd';
import { css } from '@emotion/react';
import useRuleSettingInfo from '../../../hooks/useRuleSettingInfo';
import {
  E_STEP_5,
  E_SINGLE_TYPE,
  E_STEP_2,
  E_STEP_3,
} from '../../../lib/api/Define/etc';
import GraphAddEdit from '../../UI/organisms/GraphAddEdit/GraphAddEdit';
import {
  graphBodyStyle,
  emptyWrapper,
} from '../JobAnalysis/AnalysisGraph/styleGroup';
import {
  drawGraph,
  usePrevious,
} from '../JobAnalysis/AnalysisGraph/functionGroup';
import GraphComponent from '../JobAnalysis/AnalysisGraph/Fragments/GraphComponent';
import VisualSetting from './VisualSetting';
import { getParseData } from '../../../lib/util/Util';

const mainWrapper = css`
  font-family: saira;
  width: 100%;
`;
const addGraphButtonEvent = () => {
  console.log('[STEP6]addGraphButtonEvent');
};
const ContentsForm = ({ data }) => {
  return <VisualSetting data={data} type={E_SINGLE_TYPE} />;
};
ContentsForm.propTypes = {
  data: PropTypes.object,
};

const PreviewForm = ({ type }) => {
  const {
    visualStepInfo,
    updateVisualInfo,
    ruleStepConfig,
    funcStepInfo,
  } = useRuleSettingInfo();
  const [isOpen, setIsOpen] = useState(false);
  const [currentIdx, setCurrentIdx] = useState('');
  const [sInfo, setInfo] = useState({
    step: undefined,
    origin_data: undefined,
  });
  const previousVisual = usePrevious(visualStepInfo);
  const previousData = usePrevious(sInfo.origin_data);

  const getVisualStep_OriginalData = ({ type, funcStepInfo }) => {
    return type === E_SINGLE_TYPE
      ? E_STEP_5
      : funcStepInfo.use_org_analysis === true
      ? E_STEP_2
      : E_STEP_3;
  };
  const openEdit = (idx) => {
    setCurrentIdx(idx);
    setIsOpen(true);
  };

  const onDelete = (idx) => {
    updateVisualInfo({
      ...visualStepInfo,
      items: visualStepInfo.items.map((v, i) => {
        return i === idx ? '' : v;
      }),
    });
  };

  useEffect(() => {
    console.log('[useEffect]visualStepInfo', visualStepInfo);
    if (visualStepInfo.items.length > 0) {
      const baseData =
        sInfo.origin_data?.row ??
        sInfo.origin_data?.data?.row ??
        sInfo.origin_data?.data?.map((o) => {
          const pData = getParseData(o);
          return { [pData.id]: pData.value.row };
        }) ??
        {};
      const dataChanged =
        JSON.stringify(previousData) !== JSON.stringify(sInfo.origin_data);
      const scriptChanged =
        JSON.stringify(previousVisual?.function_graph_type) !==
        JSON.stringify(visualStepInfo.function_graph_type);
      const filterPreviousItems = previousVisual?.items ?? [];

      visualStepInfo.items.forEach((v, i) => {
        const isChange =
          previousVisual === undefined ||
          JSON.stringify(filterPreviousItems[i]) !== JSON.stringify(v) ||
          scriptChanged ||
          dataChanged;
        if (isChange && v !== '') {
          drawGraph(baseData, v, visualStepInfo, 'step', i);
        }
      });
    }
  }, [visualStepInfo, sInfo.origin_data]);

  useEffect(() => {
    const step = getVisualStep_OriginalData({ type, funcStepInfo });
    const step_data = ruleStepConfig.find((v) => v.step === step);

    updateVisualInfo({
      function_graph_type:
        visualStepInfo.function_graph_type.length > 0
          ? visualStepInfo.function_graph_type
          : step_data?.data?.visualization?.function_graph_type ?? [],
      graph_list:
        visualStepInfo.graph_list.length > 0
          ? visualStepInfo.graph_list
          : step_data?.data?.visualization?.graph_list ?? [],
      items: step_data?.data?.visualization?.items ?? visualStepInfo.items,
    });
    setInfo({
      step: step,
      origin_data: step_data.data,
    });
  }, []);

  return (
    <>
      <div css={mainWrapper}>
        <div
          css={
            visualStepInfo.items.length > 0 &&
            visualStepInfo.items.filter((v) => v !== '').length > 0
              ? graphBodyStyle
              : emptyWrapper
          }
        >
          {visualStepInfo.items.length > 0 &&
          visualStepInfo.items.filter((v) => v !== '').length > 0 ? (
            visualStepInfo.items.map((v, i) => {
              return v !== '' ? (
                <GraphComponent
                  key={i}
                  index={i}
                  editFunc={openEdit}
                  deleteFunc={onDelete}
                  type="step"
                />
              ) : (
                ''
              );
            })
          ) : (
            <Empty description="No graphs to display." />
          )}
        </div>
      </div>

      {sInfo?.origin_data ?? false ? (
        <GraphAddEdit
          data={sInfo.origin_data}
          closer={() => setIsOpen(false)}
          isOpen={isOpen}
          mode="edit"
          index={currentIdx}
        />
      ) : (
        ''
      )}
    </>
  );
};
PreviewForm.propTypes = {
  type: PropTypes.string,
};
const Step6_Setting = ({ children }) => {
  return <div>{children}</div>;
};

Step6_Setting.propTypes = {
  children: PropTypes.node,
};
Step6_Setting.btn_addGraph = addGraphButtonEvent;
Step6_Setting.view_contents = ContentsForm;
Step6_Setting.view_preview = PreviewForm;

export default Step6_Setting;
