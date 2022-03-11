import React from 'react';
import PropTypes from 'prop-types';
import { css } from '@emotion/react';
import { Table } from 'antd';
import {
  CommonRegex,
  RuleNameRegex,
  TableNameRegex,
} from '../../../lib/util/RegExp';
import { E_STEP_4, E_STEP_3, R_OK } from '../../../lib/api/Define/etc';
import {
  getArray,
  getFormdataFiles,
  getParseJsonData,
  getTableForm,
} from '../../../lib/util/Util';
import { postRequestFormData } from '../../../lib/api/axios/requests';
import { SingleJobStepConf as steps } from '../../../hooks/useJobStepInfo';
import { URL_PREVIEW_CONVERTED } from '../../../lib/api/Define/URL';
import { NotificationBox } from '../../UI/molecules/NotificationBox';
import ConvertSetting from './ConvertSetting';

const tableWrapper = css`
  display: contents;
`;

const notificationWrapper = css`
  & > p:not(:first-of-type) {
    margin-bottom: 0;
  }
  & > p:first-of-type {
    font-weight: bold;
  }
  & > p > span {
    color: #1890ff;
    font-weight: bold;
    margin-right: 0.5rem;
  }
`;

const TableErrorMsg = (info) => {
  const table = Object.keys(info.err);
  const idx = table.findIndex((item) => info.err[item].length !== 0);
  const contents = info.err[table[idx]][0];
  const columnName = contents.msg[0].key;
  const errMsg = `[${contents.msg[0].name}]: ${contents.msg[0].reason}`;
  return (
    <div css={notificationWrapper}>
      <p>[{table[idx]} Columns ] SETTING ERROR</p>
      <p>
        <span>Index:</span> {contents.index + 1}
      </p>
      <p>
        <span>Columns:</span> {columnName}
      </p>
      <p>
        <span>ErrorMsg:</span> {errMsg}
      </p>
    </div>
  );
};
const PreviewRequest = async ({
  convertStepInfo,
  func_id,
  data,
  originLog,
  setData,
}) => {
  const convertTmp = { ...convertStepInfo };

  const infoArr = getArray(convertTmp?.info ?? [], true, false);
  const customArr = getArray(convertTmp?.custom ?? [], false, false);
  const headerArr = getArray(convertTmp?.header ?? [], true, false);

  {
    const obj = Object.assign(
      {},
      {
        data: originLog?.data ?? originLog ?? [],
        convert: {
          log_define:
            convertStepInfo.mode === 'empty'
              ? {
                  log_name: convertStepInfo.log_define.log_name,
                  table_name: convertStepInfo.log_define.table_name,
                }
              : {
                  log_name: convertStepInfo.log_define.log_name,
                  table_name: convertStepInfo.log_define.table_name,
                  rule_name: convertStepInfo.log_define.rule_name,
                },
          info: infoArr ?? [],
          header: headerArr ?? [],
          custom: customArr ?? [],
        },
      },
    );
    const requestObj = getParseJsonData({
      json_data: new Blob([JSON.stringify(obj)], {
        type: 'application/json',
      }),
      mode: convertStepInfo?.mode ?? '',
      func_id: func_id ?? null,
      script_file: getFormdataFiles(data?.step3_script ?? null),
      use_script: convertStepInfo?.script?.use_script ?? false,
    }).filter((obj) => obj.value !== null);
    const FormObj = new FormData();
    requestObj.map((obj) => FormObj.append(obj.id, obj.value));
    try {
      const { info, status } = await postRequestFormData(
        convertStepInfo.mode !== 'empty'
          ? steps[E_STEP_3].preview
          : URL_PREVIEW_CONVERTED,
        FormObj,
      );
      console.log('info', info);
      console.log('status', status);
      if (status === R_OK) {
        if (info.result === true) {
          const tableData = getTableForm({ info: info.data, max_row: 5 });
          setData((prevState) => ({
            ...prevState,
            ['convert_header']: tableData.columns,
            ['convert_data']: tableData.dataSource,
            ['convert_error']: undefined,
          }));
          return { data: info.data, step: E_STEP_3 };
        } else {
          console.log('info.result === false');
          if (typeof info.err === 'object') {
            NotificationBox('error', TableErrorMsg(info), 0);
          } else {
            NotificationBox('error', info.err);
          }
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
  convertStepInfo,
  func_id,
  data,
  originLog,
  setData,
}) => {
  return PreviewRequest({
    convertStepInfo,
    setData,
    func_id,
    data,
    originLog,
  }).then((_) => _);
};

const PreviousButtonEvent = () => {};

const NextButtonEvent = async ({
  setLoading,
  convertStepInfo,
  data,
  func_id,
  originLog,
}) => {
  if (EnableCheck(convertStepInfo) ?? false) {
    setLoading(true);
    const result = await PreviewRequest({
      convertStepInfo,
      setData: data.func,
      func_id,
      data: data.data,
      originLog,
    }).then((_) => _);
    console.log('PreviewResult', result);
    if (result === undefined) {
      setLoading(false);
      return {
        info: undefined,
        next: E_STEP_3,
        preview: undefined,
      };
    } else {
      return {
        info: undefined,
        next: E_STEP_4,
        preview: { current: result.step, info: result.data },
      };
    }
  } else {
    return {
      info: undefined,
      next: E_STEP_4,
      preview: undefined,
    };
  }
};
const EnableCheck = (convertStepInfo) => {
  const isValidLogName = CommonRegex.test(
    convertStepInfo?.log_define?.log_name ?? '',
  );
  const isValidTableName = TableNameRegex.test(
    convertStepInfo?.log_define?.table_name ?? '',
  );
  const isValidRuleName = RuleNameRegex.test(
    convertStepInfo?.log_define?.rule_name ?? '',
  );

  return convertStepInfo.mode === 'empty'
    ? Boolean(
        convertStepInfo?.log_define?.log_name &&
          convertStepInfo?.log_define?.table_name,
      )
    : Boolean(
        convertStepInfo?.log_define?.log_name &&
          isValidLogName &&
          convertStepInfo?.log_define?.table_name &&
          (convertStepInfo.mode === 'new' ? isValidTableName : true) &&
          convertStepInfo?.log_define?.rule_name &&
          (convertStepInfo.mode === 'new' ? isValidRuleName : true),
      );
};

const ContentsForm = ({ data, onChange }) => {
  return <ConvertSetting data={data} onChange={onChange} />;
};
ContentsForm.propTypes = {
  data: PropTypes.object,
  onChange: PropTypes.func,
};

const PreviewForm = ({ data }) => {
  if (data == null) return <></>;

  const { convert_header, convert_data, convert_error } = data;

  if (
    convert_header === undefined &&
    convert_data === undefined &&
    convert_error === undefined
  )
    return <></>;

  return (
    <div css={tableWrapper}>
      {convert_error !== undefined ? (
        <>{convert_error}</>
      ) : (
        <Table
          bordered
          pagination={false}
          columns={convert_header}
          dataSource={convert_data}
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
const Step3_Setting = ({ children }) => {
  return <div>{children}</div>;
};

Step3_Setting.propTypes = {
  children: PropTypes.node,
};
Step3_Setting.btn_next = NextButtonEvent;
Step3_Setting.btn_previous = PreviousButtonEvent;
Step3_Setting.btn_preview = PreviewButtonEvent;
Step3_Setting.check_next = EnableCheck;
Step3_Setting.check_preview = EnableCheck;
Step3_Setting.view_contents = ContentsForm;
Step3_Setting.view_preview = PreviewForm;

export default Step3_Setting;
