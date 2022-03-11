import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { css } from '@emotion/react';
import { Table, Tabs } from 'antd';
import {
  getArray,
  getFormdataFiles,
  getParseJsonData,
  getTableForm,
} from '../../../../lib/util/Util';
import { postRequestFormData } from '../../../../lib/api/axios/requests';
import { MultiJobStepConf as steps } from '../../../../hooks/useJobStepInfo';

const tableWrapper = css`
  display: contents;
`;

const multiPreviewStyle = css`
  display: inline-grid;
  width: 100%;
  & div.ant-tabs-nav {
    margin: 0px;
  }
  & div.ant-tabs-tab {
    background: transparent !important;
    border: none !important;
  }
  & div.ant-tabs-tab-active {
    color: #1890ff !important;
    background: #fafafa !important;
    border: 1px solid #f5f5f5 !important;
  }
`;
import {
  E_STEP_3,
  E_STEP_4,
  R_OK,
  E_MULTI_TYPE,
} from '../../../../lib/api/Define/etc';
import { AnyRegex } from '../../../../lib/util/RegExp';
import { NotificationBox } from '../../../UI/molecules/NotificationBox';
import AnalysisSetting from '../AnalysisSetting';
const NextButtonEvent = async ({
  setLoading,
  analysisStepInfo,
  funcStepInfo,
  data,
  func_id,
  originLog,
}) => {
  setLoading(true);
  if (EnableCheck(analysisStepInfo) ?? false) {
    const result = await PreviewRequest({
      funcStepInfo,
      analysisStepInfo,
      func_id,
      data: data.data,
      originLog,
      setData: data.func,
    }).then((_) => _);
    console.log('PreviewResult', result);
    return {
      info: undefined,
      next: E_STEP_4,
      preview: { current: result.step, info: result.data },
    };
  } else {
    return {
      info: undefined,
      next: E_STEP_4,
      preview: undefined,
    };
  }
};
const PreviewRequest = async ({
  funcStepInfo,
  analysisStepInfo,
  func_id,
  data,
  originLog,
  setData,
}) => {
  const analysisTmp = { ...analysisStepInfo };
  const analysisItems = getArray(analysisTmp?.items ?? [], false, true).map(
    (obj) => ({
      ...obj,
      source_col: obj.source_col.map((obj2) => obj2.join('/')),
    }),
  );
  const analysisObj =
    (analysisTmp?.type ?? 'setting') === 'setting'
      ? {
          type: 'setting',
          items: analysisItems,
          filter_default: analysisTmp?.filter_default ?? [],
          aggregation_default: analysisTmp?.aggregation_default ?? {},
        }
      : (analysisTmp?.type ?? 'setting') === 'script'
      ? {
          type: 'script',
          script: {
            db_id: analysisStepInfo.script.db_id,
            sql: analysisStepInfo.script.sql,
            file_name: analysisStepInfo.script.file_name,
            use_script: analysisStepInfo.script.use_script,
          },
        }
      : {
          type: 'none',
          filter_default: analysisTmp?.filter_default ?? [],
        };

  if (originLog === undefined || originLog === null) {
    console.log('data is empty');
  } else {
    const obj = Object.assign(
      {},
      {
        func_list: funcStepInfo.list.map((obj) => ({
          func_id: obj.func_id,
          tab_name: obj.tab_name,
          rid: obj.rid,
        })),
        analysis: analysisObj,
      },
    );
    const requestObj = getParseJsonData({
      json_data: new Blob([JSON.stringify(obj)], {
        type: 'application/json',
      }),
      func_id: func_id ?? null,
      script_file: getFormdataFiles(data?.step5_script ?? null),
      use_script: analysisStepInfo?.script?.use_script ?? false,
    }).filter((obj) => obj.value !== null);
    const FormObj = new FormData();
    requestObj.map((obj) => FormObj.append(obj.id, obj.value));
    try {
      const { info, status } = await postRequestFormData(
        steps[E_STEP_3].preview,
        FormObj,
      );
      console.log('status', status);
      if (status === R_OK) {
        if (info.result === true || info.result === undefined) {
          let tableData = {};
          if ((analysisTmp?.type ?? 'setting') === 'none') {
            info.data.map((obj) => {
              Object.assign(
                tableData,
                Object.fromEntries(
                  Object.entries(obj).map(([v1, v2]) => [
                    v1,
                    getTableForm({ info: v2, max_row: 5 }),
                  ]),
                ),
              );
            });
          } else {
            tableData = getTableForm({ info: info.data, max_row: 5 });
          }
          console.log('tableData', tableData);
          setData((prevState) => ({
            ...prevState,
            ['analysis_header']:
              (analysisTmp?.type ?? 'setting') === 'none'
                ? Object.fromEntries(
                    Object.entries(tableData).map(([key, val]) => [
                      key,
                      val.columns,
                    ]),
                  )
                : tableData.columns,
            ['analysis_data']:
              (analysisTmp?.type ?? 'setting') === 'none'
                ? Object.fromEntries(
                    Object.entries(tableData).map(([key, val]) => [
                      key,
                      val.dataSource,
                    ]),
                  )
                : tableData.dataSource,
            ['analysis_error']: undefined,
          }));
          console.log('result', { data: info, step: E_STEP_3 });
          const visualizationInfo = {
            function_graph_type: info?.visualization?.function_graph_type
              ? info.visualization.function_graph_type
              : originLog?.visualization?.function_graph_type
              ? originLog.visualization.function_graph_type
              : [],
            graph_list: info?.visualization?.graph_list
              ? info.visualization.graph_list
              : originLog?.visualization?.graph_list
              ? originLog.visualization.graph_list
              : [],
            items: info?.visualization?.items
              ? info.visualization.items
              : originLog?.visualization?.items
              ? originLog.visualization.items
              : [],
            common_axis_x: info?.visualization?.common_axis_x
              ? info.visualization.common_axis_x
              : originLog?.visualization?.common_axis_x
              ? originLog.visualization.common_axis_x
              : [],
          };
          return {
            data: {
              ...info,
              visualization: { ...visualizationInfo },
            },
            step: E_STEP_3,
          };
        } else {
          console.log('info.result === false');
          NotificationBox('error', info.err);
          return { data: undefined, step: undefined };
        }
      }
    } catch (e) {
      if (e.response) {
        const {
          data: { msg },
        } = e.response;
        console.log(e.response);
        NotificationBox('error', msg);
      }
    }
  }
};
const PreviewButtonEvent = ({
  funcStepInfo,
  analysisStepInfo,
  func_id,
  data,
  originLog,
  setData,
}) => {
  return PreviewRequest({
    funcStepInfo,
    analysisStepInfo,
    func_id,
    data,
    originLog,
    setData,
  }).then((_) => _);
};
const PreviousButtonEvent = () => {};

const EnableCheck = (analysisStepInfo) => {
  if ((analysisStepInfo?.type ?? 'setting') === 'none') {
    return true;
  } else if ((analysisStepInfo?.type ?? 'setting') === 'script') {
    return Boolean(analysisStepInfo?.script?.file_name ?? false);
  } else {
    const isValidSourceColumn = Boolean(
      !analysisStepInfo.items.filter(
        (o) => AnyRegex.test(o.source_col) === false,
      ).length,
    );
    const isValidTitle = Boolean(
      !analysisStepInfo?.items?.filter((o) => AnyRegex.test(o.type) === false)
        .length,
    );
    const isValidTotalType = Boolean(
      !analysisStepInfo?.items?.filter(
        (o) => AnyRegex.test(o.total_analysis_type) === false,
      ).length,
    );
    const isValidTotal = Boolean(
      !analysisStepInfo?.items?.filter(
        (o) => AnyRegex.test(o.total_analysis) === false,
      ).length,
    );
    const isValidAnalysisType = Boolean(
      !analysisStepInfo?.items?.filter(
        (o) => AnyRegex.test(o.group_analysis_type) === false,
      ).length,
    );
    const isValidAnalysis = Boolean(
      !analysisStepInfo?.items?.filter(
        (o) => AnyRegex.test(o.group_analysis) === false,
      ).length,
    );
    return (
      (analysisStepInfo?.items?.length > 0 &&
        isValidSourceColumn &&
        isValidTitle &&
        isValidTotalType &&
        isValidTotal &&
        isValidAnalysisType &&
        isValidAnalysis &&
        ((analysisStepInfo?.aggregation_default?.type !== undefined &&
          analysisStepInfo?.aggregation_default?.type !== '' &&
          analysisStepInfo?.aggregation_default?.val !== '') ||
          analysisStepInfo?.aggregation_default?.type === 'all')) ??
      false
    );
  }
};

const ContentsForm = ({ data, onChange }) => {
  return (
    <AnalysisSetting onChange={onChange} data={data} type={E_MULTI_TYPE} />
  );
};
ContentsForm.propTypes = {
  data: PropTypes.object,
  onChange: PropTypes.func,
};

const { TabPane } = Tabs;
const PreviewForm = ({ data }) => {
  const [tabSetting, setTabSetting] = useState({
    list: [],
    selected: undefined,
  });

  if (data == null) return <></>;
  const { analysis_header, analysis_data, analysis_error } = data;
  const TabChangeEvent = (e) => {
    setTabSetting((prev) => {
      return { ...prev, selected: e };
    });
  };

  useEffect(() => {
    console.log('analysis_header', analysis_header);
    console.log('Array.isArray', Array.isArray(analysis_header));
    if (Array.isArray(analysis_header) === true) {
      setTabSetting({ list: [], selected: undefined });
    } else {
      const keyList = Object.keys(analysis_header ?? {});
      setTabSetting({ list: keyList ?? [], selected: keyList[0] });
    }
  }, [analysis_header]);

  if (
    analysis_header === undefined &&
    analysis_data === undefined &&
    analysis_error === undefined
  )
    return <></>;

  return (
    <>
      {tabSetting?.selected !== undefined ? (
        <div css={multiPreviewStyle}>
          <Tabs
            type="card"
            onChange={TabChangeEvent}
            activeKey={tabSetting.selected}
          >
            {tabSetting.list.map((tab) => (
              <>
                <TabPane tab={tab} key={tab}>
                  <div css={tableWrapper}>
                    <Table
                      bordered
                      pagination={false}
                      columns={analysis_header?.[tab] ?? []}
                      dataSource={analysis_data?.[tab] ?? []}
                      size="middle"
                      rowKey="key"
                      scroll={{ x: 'max-content' }}
                    />
                  </div>
                </TabPane>
              </>
            ))}
          </Tabs>
        </div>
      ) : (
        <div css={tableWrapper}>
          <Table
            bordered
            pagination={false}
            columns={
              Array.isArray(analysis_header ?? []) ? analysis_header : []
            }
            dataSource={Array.isArray(analysis_data ?? []) ? analysis_data : []}
            size="middle"
            rowKey="key"
            scroll={{ x: 'max-content' }}
          />
        </div>
      )}
    </>
  );
};
PreviewForm.propTypes = {
  data: PropTypes.object,
};
const Step3_Multi_Setting = ({ children }) => {
  return <div>{children}</div>;
};

Step3_Multi_Setting.propTypes = {
  children: PropTypes.node,
};

Step3_Multi_Setting.btn_next = NextButtonEvent;
Step3_Multi_Setting.btn_previous = PreviousButtonEvent;
Step3_Multi_Setting.btn_preview = PreviewButtonEvent;
Step3_Multi_Setting.check_next = EnableCheck;
Step3_Multi_Setting.check_preview = EnableCheck;
Step3_Multi_Setting.view_contents = ContentsForm;
Step3_Multi_Setting.view_preview = PreviewForm;

export default Step3_Multi_Setting;
