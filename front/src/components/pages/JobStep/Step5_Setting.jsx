import React from 'react';
import PropTypes from 'prop-types';
import { css } from '@emotion/react';
import { Table } from 'antd';
import { MSG_REMOTE, MSG_SQL } from '../../../lib/api/Define/Message';
import {
  E_SINGLE_TYPE,
  E_STEP_5,
  E_STEP_6,
  E_STEP_LOG_SELECT,
  R_OK,
} from '../../../lib/api/Define/etc';
import { AnyRegex } from '../../../lib/util/RegExp';
import {
  getArray,
  getFormdataFiles,
  getParseJsonData,
  getTableForm,
} from '../../../lib/util/Util';
import { postRequestFormData } from '../../../lib/api/axios/requests';
import { SingleJobStepConf as steps } from '../../../hooks/useJobStepInfo';
import { NotificationBox } from '../../UI/molecules/NotificationBox';
import AnalysisSetting from './AnalysisSetting';
const tableWrapper = css`
  display: contents;
`;

const NextButtonEvent = async ({
  setLoading,
  analysisStepInfo,
  data,
  func_id,
  originLog,
}) => {
  setLoading(true);
  if (EnableCheck(analysisStepInfo) ?? false) {
    const result = await PreviewRequest({
      analysisStepInfo,
      setData: data.func,
      func_id,
      data: data.data,
      originLog,
    }).then((_) => _);
    console.log('PreviewResult', result);
    return {
      info: undefined,
      next: E_STEP_6,
      preview: { current: result.step, info: result.data },
    };
  } else {
    return {
      info: undefined,
      next: E_STEP_6,
      preview: undefined,
    };
  }
};
const PreviewRequest = async ({
  analysisStepInfo,
  func_id,
  data,
  originLog,
  setData,
}) => {
  const analysisTmp = { ...analysisStepInfo };

  const { items, filter_default, aggregation_default } = analysisTmp;

  if (originLog === undefined || originLog === null) {
    console.log('data is empty');
  } else {
    const obj = Object.assign(
      {},
      {
        data: {
          row: originLog.row,
          disp_order: originLog.disp_order,
        },
        analysis:
          (analysisTmp?.type ?? 'setting') === 'setting'
            ? {
                type: 'setting',
                items: items === undefined ? [] : getArray(items, false, true),
                filter_default:
                  filter_default === undefined ? [] : filter_default,
                aggregation_default:
                  aggregation_default === undefined ? {} : aggregation_default,
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
                filter_default:
                  filter_default === undefined ? [] : filter_default,
              },
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
        steps[E_STEP_5].preview,
        FormObj,
      );
      console.log('info', info);
      console.log('status', status);
      if (status === R_OK) {
        if (info.result === true || info.result === undefined) {
          const tableData = getTableForm({ info: info.data, max_row: 5 });
          setData((prevState) => ({
            ...prevState,
            ['analysis_header']: tableData.columns,
            ['analysis_data']: tableData.dataSource,
            ['analysis_error']: undefined,
          }));
          return { data: info.data, step: E_STEP_5 };
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
  analysisStepInfo,
  func_id,
  data,
  originLog,
  setData,
}) => {
  return PreviewRequest({
    analysisStepInfo,
    func_id,
    data,
    originLog,
    setData,
  }).then((_) => _);
};
const PreviousButtonEvent = (funcStepInfo) => {
  return funcStepInfo.source_type === MSG_REMOTE ||
    funcStepInfo.source_type === MSG_SQL
    ? { step: E_STEP_LOG_SELECT, status: 'pass' }
    : { step: 0, status: 'false' };
};
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
    <AnalysisSetting onChange={onChange} data={data} type={E_SINGLE_TYPE} />
  );
};
ContentsForm.propTypes = {
  data: PropTypes.object,
  onChange: PropTypes.func,
};

const PreviewForm = ({ data }) => {
  if (data == null) return <></>;

  const { analysis_header, analysis_data, analysis_error } = data;

  if (
    analysis_header === undefined &&
    analysis_data === undefined &&
    analysis_error === undefined
  )
    return <></>;

  return (
    <div css={tableWrapper}>
      {analysis_error !== undefined ? (
        <>{analysis_error}</>
      ) : (
        <Table
          bordered
          pagination={false}
          columns={analysis_header}
          dataSource={analysis_data}
          size="middle"
          rowKey="key"
          scroll={{ x: 'max-content' }}
        />
      )}
    </div>
  );
};
PreviewForm.propTypes = {
  data: PropTypes.object,
};
const Step5_Setting = ({ children }) => {
  return <div>{children}</div>;
};

Step5_Setting.propTypes = {
  children: PropTypes.node,
};

Step5_Setting.btn_next = NextButtonEvent;
Step5_Setting.btn_previous = PreviousButtonEvent;
Step5_Setting.btn_preview = PreviewButtonEvent;
Step5_Setting.check_next = EnableCheck;
Step5_Setting.check_preview = EnableCheck;
Step5_Setting.view_contents = ContentsForm;
Step5_Setting.view_preview = PreviewForm;

export default Step5_Setting;
