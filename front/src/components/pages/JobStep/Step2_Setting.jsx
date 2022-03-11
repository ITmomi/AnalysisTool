import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import useRuleSettingInfo from '../../../hooks/useRuleSettingInfo';
import { css } from '@emotion/react';
import {
  MSG_ADD_NEW,
  MSG_DISABLE,
  MSG_LOCAL,
  MSG_REMOTE,
  MSG_SQL,
} from '../../../lib/api/Define/Message';
import { useParams } from 'react-router';
import {
  E_STEP_2,
  E_STEP_3,
  E_STEP_ANALYSIS,
  R_OK,
} from '../../../lib/api/Define/etc';
import {
  getFileName,
  getFindData,
  getFormdataFiles,
  getParseData,
  getParseJsonData,
  getTableForm,
} from '../../../lib/util/Util';
import { Table } from 'antd';
import { NotificationBox } from '../../UI/molecules/NotificationBox';
import { FormCard } from '../../UI/atoms/Modal';
import { StepInputForm } from '../../UI/organisms/StepInputForm';
import { E_JOB_STEP } from '../../../lib/api/Define/JobStepEnum';
import { useMutation, useQuery } from 'react-query';
import { QUERY_KEY } from '../../../lib/api/Define/QueryKey';
import { SingleJobStepConf as steps } from '../../../hooks/useJobStepInfo';
import {
  deleteRuleName,
  getStep2ResourceUpdate,
  getTableList,
} from '../../../lib/api/axios/useJobStepRequest';
import {
  getEquipmentValidDate,
  getEquipmentList,
  postRequestFormData,
  getRequestParam,
} from '../../../lib/api/axios/requests';
const tableWrapper = css`
  display: contents;
`;
const titleStyle = css`
  font-weight: 400;
`;

const EnableLocalType = ({
  isNext,
  funcStepInfo,
  convertStepInfo,
  isEditMode,
}) => {
  return Boolean(
    !isNext
      ? funcStepInfo?.src_file
      : isEditMode ?? false
      ? convertStepInfo?.log_define?.rule_name !== undefined
      : convertStepInfo?.log_define?.log_name !== undefined,
  );
};

const EnableRemoteType = ({ funcStepInfo }) => {
  const { info } = funcStepInfo;
  return Boolean(
    !!(info?.db_id ?? false) &&
      !!(info?.equipment_name ?? false) &&
      !!(info?.selected?.start ?? false) &&
      !!(info?.selected?.end ?? false),
  );
};

const EnableSQLType = ({ funcStepInfo }) => {
  const { info } = funcStepInfo;
  return Boolean(!!(info?.db_id ?? false) && !!(info?.sql ?? false));
};

const PreviewRequest = async ({ funcStepInfo, func_id, data, setData }) => {
  const originLogData = data?.src_file ?? null;
  const source = funcStepInfo.source_type;

  if (source === MSG_LOCAL && !!originLogData === false) {
    console.log('file is empty');
    return { data: undefined, step: undefined };
  } else {
    try {
      const param = getParseJsonData(
        source === MSG_REMOTE
          ? {
              source: funcStepInfo.source_type,
              equipment_name: funcStepInfo.info.equipment_name,
              table_name: funcStepInfo.info.table_name,
              db_id: funcStepInfo.info.db_id,
              start: funcStepInfo.info.selected.start,
              end: funcStepInfo.info.selected.end,
              func_id: func_id ?? null,
              script_file: getFormdataFiles(data?.step2_script ?? null),
              use_script: funcStepInfo?.script?.use_script ?? false,
            }
          : source === MSG_LOCAL
          ? {
              source: funcStepInfo.source_type,
              use_script: funcStepInfo?.script?.use_script ?? false,
              func_id: func_id ?? null,
              files: getFormdataFiles(data?.src_file ?? null),
              script_file: getFormdataFiles(data?.step2_script ?? null),
            }
          : source === MSG_SQL
          ? {
              source: funcStepInfo.source_type,
              db_id: funcStepInfo.info.db_id,
              sql: funcStepInfo.info.sql,
              use_script: funcStepInfo?.script?.use_script ?? false,
              func_id: func_id ?? null,
              script_file: getFormdataFiles(data?.step2_script ?? null),
            }
          : {},
      ).filter((obj) => obj.value !== null);
      const FormObj = new FormData();
      param.map((obj) => FormObj.append(obj.id, obj.value));
      const { info, status } = await postRequestFormData(
        steps[E_STEP_2].preview,
        FormObj,
      );
      if (status === R_OK) {
        if (info.result) {
          const tableData = getTableForm({ info: info.data, max_row: 5 });
          setData((prevState) =>
            source === MSG_SQL || source === MSG_REMOTE
              ? {
                  ...prevState,
                  ['log_header']: tableData.columns,
                  ['log_data']: tableData.dataSource,
                  ['log_error']: undefined,
                  ['filter_header']: tableData.columns,
                  ['filter_data']: tableData.dataSource,
                  ['filter_error']: undefined,
                }
              : {
                  ...prevState,
                  ['log_header']: tableData.columns,
                  ['log_data']: tableData.dataSource,
                  ['log_error']: undefined,
                },
          );
          return { data: info, step: E_STEP_2 };
        } else {
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
      return { data: undefined, step: undefined };
    }
  }
};

const NextRequest = async ({
  func_id,
  convertStepInfo,
  data,
  source_type,
  preview,
}) => {
  const isEditMode = !!(func_id ?? false);
  const { log_define } = convertStepInfo;
  console.log('log_define', log_define);
  console.log('data', data);
  const { info, status } = await getRequestParam(
    isEditMode
      ? `${steps[E_STEP_2].edit}/${func_id}/${log_define.log_name}`
      : `${steps[E_STEP_2].new}`,
    isEditMode
      ? data.data?.new_rule ?? true
        ? undefined
        : `${log_define.rule_id}`
      : log_define?.log_name ?? false
      ? `${log_define.log_name}`
      : undefined,
  );
  if (status === R_OK) {
    return {
      info: { config: info },
      next:
        source_type === MSG_REMOTE || source_type === MSG_SQL
          ? E_STEP_ANALYSIS
          : E_STEP_3,
      preview: preview,
    };
  }
};

const NextButtonEvent = async ({
  setLoading,
  funcStepInfo,
  convertStepInfo,
  func_id,
  data,
}) => {
  setLoading(true);

  if (PreviewEnableCheck(funcStepInfo) ?? false) {
    const result = await PreviewRequest({
      funcStepInfo,
      func_id,
      data: data.data,
      setData: data.func,
    }).then((_) => _);
    console.log('PreviewResult', result);
    if (result.step === E_STEP_2) {
      return NextRequest({
        func_id,
        data,
        convertStepInfo,
        source_type: funcStepInfo.source_type,
        preview: { current: E_STEP_2, info: result.data },
      }).then((_) => _);
    } else {
      setLoading(false);
    }
  } else {
    return NextRequest({
      func_id,
      data,
      convertStepInfo,
      source_type: funcStepInfo.source_type,
      preview: undefined,
    }).then((_) => _);
  }
};
const PreviewButtonEvent = ({ funcStepInfo, func_id, data, setData }) => {
  return PreviewRequest({ funcStepInfo, func_id, data, setData }).then(
    (_) => _,
  );
};
const PreviousButtonEvent = () => {};
const PreviewEnableCheck = (funcStepInfo) => {
  const { source_type } = funcStepInfo;
  return source_type === MSG_LOCAL
    ? EnableLocalType({
        isEditMode: undefined,
        funcStepInfo,
        convertStepInfo: undefined,
        isNext: false,
      })
    : source_type === MSG_REMOTE
    ? EnableRemoteType({ funcStepInfo })
    : source_type === MSG_SQL
    ? EnableSQLType({ funcStepInfo })
    : false;
};

const NextEnableCheck = (funcStepInfo, convertStepInfo, isEditMode) => {
  const { source_type } = funcStepInfo;
  return source_type === MSG_LOCAL
    ? EnableLocalType({
        isEditMode,
        funcStepInfo,
        convertStepInfo,
        isNext: true,
      })
    : source_type === MSG_REMOTE
    ? EnableRemoteType({ funcStepInfo })
    : source_type === MSG_SQL
    ? EnableSQLType({ funcStepInfo })
    : false;
};

const remote_info_initial = {
  db_id: undefined,
  table_name: undefined,
  equipment_name: undefined,
  selected: {
    start: undefined,
    end: undefined,
  },
  period: {
    start: undefined,
    end: undefined,
  },
};
/*============================================================================
==                         STEP 2 CONTENTS                                  ==
============================================================================*/
const STEP2_MSG_ADD = 'add';
const STEP2_MSG_NEW = 'new';
const STEP2_MSG_EDIT = 'edit';
const STEP2_MSG_LOG_SELECT = 'empty';
const INPUT_TYPE_CSV = 'csv';

const ContentsForm = ({ data, onChange }) => {
  const {
    ruleStepConfig,
    updateConvertInfo,
    updateFuncInfo,
    funcStepInfo,
    convertStepInfo,
    setRuleStepConfig,
  } = useRuleSettingInfo();
  const { func_id } = useParams();
  const [config, setConfig] = useState(null);
  const [newRule, setNewRule] = useState(false);
  const [deleteRule, setDeleteRule] = useState(undefined);

  /*
   *  1. DB_ID가 설정되면 요청 된다. (DB_ID가 변경되어도 요청)
   *  2. Edit 로 들어온 경우에는 Table Name 의 요청은 필요없다.
   * */
  useQuery(
    [QUERY_KEY.STEP2_DB_TABLE_LIST, funcStepInfo?.info?.db_id],
    () => getTableList({ db_id: funcStepInfo?.info?.db_id }),
    {
      enabled: !!funcStepInfo?.info?.db_id && func_id === undefined,
      onSuccess: ({ info }) => {
        onChange({ table_name: info });
        console.log('[getDBDetailQuery]info', info);
      },
    },
  );

  /*
   *  1. DB_ID & Table Name 하나라도 변경 되면, 요청을 한다.
   *  2. Edit 로 들어온 경우에도 user/Fab/Equipment 가 필요하다.
   * */

  useQuery(
    [
      QUERY_KEY.STEP2_USER_FAB_EQUIPMENT_LIST,
      funcStepInfo?.info?.db_id,
      funcStepInfo?.info?.table_name,
    ],
    () =>
      getEquipmentList({
        db_id: funcStepInfo?.info?.db_id,
        table_name: funcStepInfo?.info?.table_name,
      }),
    {
      enabled: !!funcStepInfo?.info?.db_id && !!funcStepInfo?.info?.table_name,
      onSuccess: ({ info }) => {
        onChange(info);
        console.log('[getDBDetailQuery]info', info);
      },
    },
  );

  /*
   *  1. DB_ID /TABLE_NAME/EQUIPMENT_NAME 이 설정 되면 Equipment 의 유효한 정보를 가져온다.
   * */

  useQuery(
    [
      QUERY_KEY.STEP2_EQUIPMENT_VALID_DATE,
      funcStepInfo?.info?.db_id,
      funcStepInfo?.info?.table_name,
      funcStepInfo?.info?.equipment_name,
    ],
    () =>
      getEquipmentValidDate({
        db_id: funcStepInfo?.info?.db_id,
        table_name: funcStepInfo?.info?.table_name,
        equipment_name: funcStepInfo?.info?.equipment_name,
      }),
    {
      enabled:
        !!funcStepInfo?.info?.db_id &&
        !!funcStepInfo?.info?.table_name &&
        !!funcStepInfo?.info?.equipment_name,
      onSuccess: ({ info }) => {
        updateFuncInfo({
          ...funcStepInfo,
          info: {
            ...funcStepInfo.info,
            period: { start: info.start, end: info.end },
            selected: { start: info.start, end: info.end },
          },
        });
      },
    },
  );

  useQuery(
    [QUERY_KEY.STEP2_RESOURCE_UPDATE, func_id, deleteRule],
    () => getStep2ResourceUpdate({ func_id: func_id }),
    {
      enabled: !!func_id && !!deleteRule,
      onSuccess: ({ info }) => {
        setDeleteRule(undefined);
        storeStepConfig(info);
      },
    },
  );

  //============================================================================
  const storeStepConfig = (info) => {
    const cloneStep = ruleStepConfig.slice();
    const existIdx = ruleStepConfig.findIndex((obj) => obj.step === E_STEP_2);
    if (existIdx !== -1) {
      cloneStep.splice(existIdx, 1, {
        ...ruleStepConfig[existIdx],
        config: info,
      });
      setRuleStepConfig(cloneStep);
    }
  };
  const deleteMutation = useMutation(
    [QUERY_KEY.MGMT_DB_DELETE],
    (rule_id) => deleteRuleName({ rule_id: rule_id }),
    {
      onError: (error) => {
        NotificationBox(error.statusText, error.message);
        setDeleteRule(undefined);
      },
      onSuccess: ({ info, rule_id }) => {
        setDeleteRule(rule_id);
        updateConvertInfo({
          ...convertStepInfo,
          rule_list: info?.options ?? [],
          log_define: {
            ...convertStepInfo.log_define,
            rule_id:
              convertStepInfo.log_define.rule_id === rule_id
                ? null
                : convertStepInfo.log_define.rule_id,
            rule_name:
              convertStepInfo.log_define.rule_id === rule_id
                ? ''
                : convertStepInfo.log_define.rule_name,
          },
        });
      },
    },
  );
  const LocalConfigChange = (event) => {
    const item = getParseData(event);
    switch (item.id) {
      case E_JOB_STEP.STEP2_RULE_NAME:
        onChange({
          new_rule: item.value.rule_name === MSG_ADD_NEW,
          [E_JOB_STEP.STEP2_RULE_NAME]: item.value.rule_name,
        });
        updateConvertInfo({
          ...convertStepInfo,
          mode:
            item.value.rule_name === MSG_ADD_NEW
              ? STEP2_MSG_ADD
              : STEP2_MSG_EDIT,
          log_define: {
            ...convertStepInfo.log_define,
            rule_id:
              item.value.rule_name === MSG_ADD_NEW ? null : item.value.id,
            rule_name:
              item.value.rule_name === MSG_ADD_NEW ? '' : item.value.rule_name,
          },
        });
        break;
      case E_JOB_STEP.STEP2_LOG_NAME:
        if (item.value === MSG_ADD_NEW) {
          onChange({
            new_rule: func_id ? true : MSG_DISABLE,
            [item.id]: item.value,
          });
          updateConvertInfo({
            ...convertStepInfo,
            mode: STEP2_MSG_NEW,
            log_define: {
              ...convertStepInfo.log_define,
              log_name: '',
              table_name: '',
              rule_id: 'null',
              rule_name: '',
              input_type: INPUT_TYPE_CSV,
            },
          });
        } else if (data?.new_rule === MSG_DISABLE) {
          onChange({ new_rule: newRule, [item.id]: item.value });
          updateConvertInfo({
            ...convertStepInfo,
            mode: newRule === true ? STEP2_MSG_ADD : STEP2_MSG_LOG_SELECT,
            log_define: {
              ...convertStepInfo.log_define,
              log_name: item.value,
              input_type: INPUT_TYPE_CSV,
            },
          });
        } else {
          onChange(event);
          updateConvertInfo({
            ...convertStepInfo,
            mode:
              data?.new_rule === true
                ? STEP2_MSG_ADD
                : func_id !== undefined
                ? convertStepInfo?.log_define?.rule_name === '' ?? true
                  ? STEP2_MSG_ADD
                  : STEP2_MSG_EDIT
                : STEP2_MSG_LOG_SELECT,
            log_define: {
              ...convertStepInfo.log_define,
              log_name: item.value,
              input_type: INPUT_TYPE_CSV,
            },
          });
        }
        break;
      case 'new_rule':
        if ((data?.new_rule ?? false) !== item.value) {
          setNewRule(item.value);
          onChange(event);
          updateConvertInfo({
            ...convertStepInfo,
            mode: item.value === true ? STEP2_MSG_ADD : STEP2_MSG_LOG_SELECT,
          });
        }
        break;
      case 'src_file':
        {
          const fileName = getFileName(item.value);
          updateFuncInfo({
            ...funcStepInfo,
            src_file: fileName,
          });
          onChange({ src_file: item.value });
        }
        break;
    }
  };
  const RemoteConfigChange = (event) => {
    const item = getParseData(event);

    switch (item.id) {
      case 'table_name':
        updateFuncInfo({
          ...funcStepInfo,
          info: {
            ...funcStepInfo.info,
            [item.id]: item.value,
            equipment_name: '',
            user_fab: '',
            period: { start: '', end: '' },
            selected: { start: '', end: '' },
          },
        });
        break;
      case 'equipment_name':
        updateFuncInfo({
          ...funcStepInfo,
          info: {
            ...funcStepInfo.info,
            [item.id]: item.value,
            period: { start: '', end: '' },
            selected: { start: '', end: '' },
          },
        });
        break;
      case 'db_id':
        updateFuncInfo({
          ...funcStepInfo,
          info:
            func_id ?? false
              ? {
                  ...funcStepInfo.info,
                  [item.id]: item.value,
                  equipment_name: '',
                  user_fab: '',
                  period: { start: '', end: '' },
                  selected: { start: '', end: '' },
                }
              : {
                  ...remote_info_initial,
                  [item.id]: item.value,
                },
        });
        break;
      case 'user_fab':
        updateFuncInfo({
          ...funcStepInfo,
          info: {
            ...funcStepInfo.info,
            [item.id]: item.value,
            equipment_name: '',
            period: { start: '', end: '' },
            selected: { start: '', end: '' },
          },
        });
        break;
      case 'period':
        {
          updateFuncInfo({
            ...funcStepInfo,
            info: {
              ...funcStepInfo.info,
              selected: { start: item.value.start, end: item.value.end },
            },
          });
        }
        break;
    }
  };
  const SQLConfigChange = (event) => {
    const item = getParseData(event);

    switch (item.id) {
      case 'sql':
        updateFuncInfo({
          ...funcStepInfo,
          info: {
            ...funcStepInfo.info,
            [item.id]: item.value,
          },
        });
        break;
    }
  };

  const change = (event) => {
    const item = getParseData(event);
    switch (item.id) {
      case 'source':
        if (funcStepInfo.source_type !== item.value) {
          updateConvertInfo({
            ...convertStepInfo,
            mode:
              item.value === 'remote'
                ? STEP2_MSG_LOG_SELECT
                : convertStepInfo.mode,
          });
          updateFuncInfo({ ...funcStepInfo, source_type: item.value });
        }
        break;
      case 'file_name':
        {
          const fileName = getFileName(item.value);
          updateFuncInfo({
            ...funcStepInfo,
            script: {
              file_name: fileName,
              use_script: item.value !== null,
            },
          });
          onChange({ step2_script: item.value });
        }
        break;
      case 'use_script':
        updateFuncInfo({
          ...funcStepInfo,
          script: {
            ...funcStepInfo.script,
            use_script: item.value,
          },
        });
        break;
      case 'src_file':
      case 'new_rule':
      case 'log_name':
      case 'rule_name':
        LocalConfigChange(event);
        break;
      case 'equipment_name':
      case 'db_id':
      case 'table_name':
      case 'user_fab':
      case 'period':
        RemoteConfigChange(event);
        break;
      case 'sql':
        SQLConfigChange(event);
        break;
      case 'DELETE':
        deleteMutation.mutate(item.value.id);
        break;
      default:
        onChange(event);
        break;
    }
  };
  //============================================================================
  useEffect(() => {
    console.log('contents components mount', func_id);
    const step2 = ruleStepConfig.find((step) => step.step === E_STEP_2).config;
    setConfig(step2);
    const { form, data: stepData } = step2;
    //Edit 화면으로 들어왔을때. step2 데이터에서 정보를 가져와서 REDUX 에 저장해줘야한다.
    if (func_id) {
      const source =
        funcStepInfo?.source_type ?? getFindData(stepData, 'source', undefined);
      const obj =
        source === 'remote'
          ? {
              db_id:
                funcStepInfo?.info?.db_id ??
                getFindData(stepData, 'db_id', undefined),
              table_name: getFindData(stepData, 'table_name', undefined),
              equipment_name: getFindData(
                stepData,
                'equipment_name',
                undefined,
              ),
            }
          : source === 'sql'
          ? {
              db_id:
                funcStepInfo?.info?.db_id ??
                getFindData(stepData, 'db_id', undefined),
              sql:
                funcStepInfo?.info?.sql ??
                getFindData(stepData, 'sql', undefined),
            }
          : {};
      const script = {
        use_script:
          funcStepInfo?.script?.use_script ??
          getFindData(stepData, 'use_script', undefined) ??
          false,
        file_name:
          funcStepInfo?.script?.file_name ??
          getFindData(stepData, 'file_name', undefined) ??
          null,
      };
      updateFuncInfo({
        ...funcStepInfo,
        source_type: source,
        info: obj,
        script: script,
      });
    }
    const ruleNameItem =
      form?.[MSG_LOCAL]?.find((obj) =>
        obj?.title.includes('Log Type'),
      )?.items?.find((item) => item.target === 'rule_name') ?? {};
    updateConvertInfo({
      ...convertStepInfo,
      mode:
        convertStepInfo?.mode ??
        (func_id === undefined ? STEP2_MSG_NEW : STEP2_MSG_ADD),
      rule_list: convertStepInfo?.rule_list ?? ruleNameItem?.options ?? [],
      log_define:
        (func_id ?? false) &&
        !(!!convertStepInfo?.log_define?.rule_name ?? false)
          ? {
              ...convertStepInfo.log_define,
              rule_name: '',
              rule_id: null,
              log_name: getFindData(stepData, 'log_name', undefined),
            }
          : convertStepInfo?.log_define ?? {},
    });
    if (data?.new_rule ?? true) {
      setNewRule(func_id ? true : data?.new_rule === true ?? false);
    }
    return () => {
      console.log('contents components unmount');
    };
  }, []);

  //============================================================================
  if (config === null) return <></>;

  return (
    <div css={{ width: '500px' }}>
      {(
        config?.form?.[funcStepInfo?.source_type ?? MSG_LOCAL] ?? config.data
      ).map((item, idx) => (
        <div key={idx}>
          <FormCard title={item.title} titleStyle={titleStyle}>
            <div>
              {item.items.map((idx2, i) => (
                <StepInputForm
                  key={i}
                  data={data}
                  item={item.items[i]}
                  changeFunc={change}
                />
              ))}
            </div>
          </FormCard>
        </div>
      ))}
    </div>
  );
};
ContentsForm.propTypes = {
  data: PropTypes.object,
  onChange: PropTypes.func,
};

const PreviewForm = ({ data }) => {
  if (data == null) return <></>;
  const { log_header, log_data } = data;

  if (log_header === undefined || log_data === undefined) return <></>;

  return (
    <div css={tableWrapper}>
      <Table
        bordered
        pagination={false}
        columns={log_header}
        dataSource={log_data}
        size="middle"
        rowKey="key"
        scroll={{ x: 'max-content' }}
      />
    </div>
  );
};
PreviewForm.propTypes = {
  data: PropTypes.object,
};
const Step2_Setting = ({ children }) => {
  return <div>{children}</div>;
};

Step2_Setting.propTypes = {
  children: PropTypes.node,
};

Step2_Setting.btn_next = NextButtonEvent;
Step2_Setting.btn_previous = PreviousButtonEvent;
Step2_Setting.btn_preview = PreviewButtonEvent;
Step2_Setting.check_next = NextEnableCheck;
Step2_Setting.check_preview = PreviewEnableCheck;
Step2_Setting.view_contents = ContentsForm;
Step2_Setting.view_preview = PreviewForm;

export default Step2_Setting;
