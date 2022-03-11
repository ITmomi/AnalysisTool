import useRuleSettingInfo from '../../../hooks/useRuleSettingInfo';
import React, { useEffect, useState } from 'react';
import {
  Collapse,
  Table,
  Button,
  Input,
  Select,
  Form,
  Radio,
  Divider,
  notification,
  Tooltip,
} from 'antd';
import {
  MSG_ANALYSIS_REGEXP,
  MSG_COMMON_REGEXP,
  MSG_LOCAL,
  MSG_MULTI,
  MSG_PREVIOUS_TABLE,
  MSG_SELECT_COMBOBOX,
  MSG_STEP5_AGGREGATION,
  MSG_STEP5_ANALYSIS,
  MSG_STEP5_FILTER_KEY,
  MSG_TABLE_TITLE_DELETE,
  MSG_TABLE_TITLE_DISP_ORDER,
  MSG_TABLE_TITLE_GROUP,
  MSG_TABLE_TITLE_SOURCE_COLUMN,
  MSG_TABLE_TITLE_TILE,
  MSG_TABLE_TITLE_TOTAL,
  MSG_UPLOAD_SCRIPT,
} from '../../../lib/api/Define/Message';
import PropTypes from 'prop-types';
import {
  E_MULTI_TYPE,
  E_SINGLE_TYPE,
  E_STEP_2,
  E_STEP_4,
} from '../../../lib/api/Define/etc';
import { css } from '@emotion/react';
import {
  getFileName,
  getParseData,
  getTableForm,
} from '../../../lib/util/Util';
import TableComponent from './TableComponents';
import { useDebouncedCallback } from 'use-debounce';
import InputForm from '../../UI/atoms/Input/InputForm';
import { useQuery } from 'react-query';
import { QUERY_KEY } from '../../../lib/api/Define/QueryKey';
import { getRemoteDBInfo } from '../../../lib/api/axios/useMgmtRequest';
import { PlayCircleFilled, TableOutlined } from '@ant-design/icons';
import { getAnalysisScriptPreview } from '../../../lib/api/axios/useJobStepRequest';
import { NotificationBox } from '../../UI/molecules/NotificationBox';
import { ScriptEdit } from '../../UI/organisms/ScriptModal';
import QuestionCircleOutlined from '@ant-design/icons/lib/icons/QuestionCircleOutlined';
import {
  AnalysisPeriodRegex,
  AnyRegex,
  CommonRegex,
} from '../../../lib/util/RegExp';
import Step2_Multi_Setting from './MultiAnalysis/Step2_Setting';
import Step2_Setting from './Step2_Setting';
import Step4_Setting from './Step4_Setting';
const { Column } = Table;

const { Panel } = Collapse;
const { Option } = Select;
const tableWrapper = css`
  display: flex;
  max-width: 100%;

  & table {
    &:first-of-type > thead > tr > th {
      background: #f0f5ff;
    }
  }
  & > form {
    width: 1470px;
    & > div {
      margin-bottom: 0;
      &:first-of-type.ant-form-item {
        margin-bottom: 0;
      }
    }
  }
  & table > tbody > tr {
    & > td {
      &:first-of-type {
        text-align: center;
      }
      &:last-of-type {
        text-align: center;
      }
    }
  }
`;
const filterWrapper = css`
  display: grid;
  width: 100%;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto;
  gap: 1rem;
  margin: 1rem 0;
  & .ant-form-item-label {
    display: block;
    text-align: left;
  }
  & .ant-form-item-control {
    display: block;
    max-width: 100%;
    width: 100%;
  }
  & .ant-form-item {
    margin-bottom: 0;
  }
  & .ant-col-20,
  & .ant-col-8 {
    flex: none;
  }
`;

const step5_convert_script_style = css`
  & > div {
    max-width: 100%;
  }
  & > form.ant-form ant-form-horizontal {
    max-width: 572px;
  }
  & .ant-col.ant-col-8.ant-form-item-label {
    flex-basis: 114px;
  }
  & .ant-form-item-control-input-content {
    min-width: 400px;
  }
  & .ant-upload-list-item-info {
    width: fit-content;
    & span.ant-upload-list-item-name {
      width: fit-content;
      max-width: 1192px;
    }
  }
`;
const step5_script_button_style = css`
  display: flex;
  justify-content: space-between;
  & button {
    border-radius: 8px !important;
    &:not(button[disabled]) {
      background-color: #73d144 !important;
      color: #fff !important;
      border-color: #73d144 !important;
      &:hover {
        color: #fff !important;
        background-color: #7ce73f !important;
        border-color: #7ce73f !important;
      }
    }
  }
`;
const tailLayout = {
  labelCol: { span: 8 },
  wrapperCol: { span: 20 },
};
const DEFINE_MAX_SELECT = 4;
const CUSTOM_SELECT = 'custom';
const SEQUENTIAL_SELECT = 'sequential';
const SCRIPT_SELECT = 'script';
const DEFINE_GROUP_BY_PERIOD = 'period';
const DEFINE_GROUP_BY_COLUMN = 'column';

const AnalysisTable = ({
  dataSource,
  deleteHandler,
  columnOptions,
  typeOptions,
  onChangeText,
  onClickScript,
}) => {
  const SelectDisable = (record, type) => {
    switch (record[type]) {
      case SEQUENTIAL_SELECT:
      case CUSTOM_SELECT:
      case SCRIPT_SELECT:
        return false;
    }
    return true;
  };
  return (
    <div>
      <Table
        bordered
        pagination={false}
        size="small"
        rowKey="key"
        dataSource={dataSource}
        scroll={{ x: 'max-content' }}
      >
        <Column
          title={MSG_TABLE_TITLE_DISP_ORDER}
          dataIndex="idx"
          key="idx"
          render={(_, row, index) => {
            return <>{index + 1}</>;
          }}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_SELECT_COMBOBOX}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_SOURCE_COLUMN}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="source_col"
          key="source_col"
          render={(_, record) => (
            <>
              {columnOptions.type === E_MULTI_TYPE ? (
                <TableComponent.cascade
                  target={'source_col'}
                  record={record}
                  options={columnOptions.options}
                  onChange={onChangeText}
                  selectV={record?.source_col ?? []}
                  multiple={true}
                />
              ) : (
                <TableComponent.select
                  target={'source_col'}
                  record={record}
                  options={columnOptions.options}
                  onChange={onChangeText}
                  regEx={{ pattern: AnyRegex, message: '' }}
                />
              )}
            </>
          )}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_COMMON_REGEXP}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_TILE}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="title"
          key="title"
          render={(_, record) => (
            <TableComponent.input
              target={'title'}
              record={record}
              onChange={onChangeText}
              size={'middle'}
              regEx={{ pattern: CommonRegex, message: '' }}
            />
          )}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_ANALYSIS_REGEXP}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_GROUP}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="group_analysis"
          key="group_analysis"
          render={(_, record) => (
            <div css={{ display: 'flex', columnGap: '4px' }}>
              <TableComponent.input
                target={'group_analysis'}
                record={record}
                onChange={onChangeText}
                disabled={SelectDisable(record, 'group_analysis_type')}
                onClick={() =>
                  onClickScript({
                    target: 'group_analysis',
                    record: record,
                    value: record['group_analysis'],
                    type: record['group_analysis_type'],
                  })
                }
                regEx={{ pattern: AnyRegex, message: '' }}
              />
              <TableComponent.select
                target={'group_analysis_type'}
                record={record}
                options={typeOptions}
                onChange={onChangeText}
                regEx={{ pattern: AnyRegex, message: '' }}
              />
            </div>
          )}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_ANALYSIS_REGEXP}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_TOTAL}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="total_analysis"
          key="total_analysis"
          render={(_, record) => (
            <div css={{ display: 'flex', columnGap: '4px' }}>
              <TableComponent.input
                target={'total_analysis'}
                record={record}
                onChange={onChangeText}
                disabled={SelectDisable(record, 'total_analysis_type')}
                onClick={() =>
                  onClickScript({
                    target: 'total_analysis',
                    record: record,
                    value: record['total_analysis'],
                    type: record['total_analysis_type'],
                  })
                }
                regEx={{ pattern: AnyRegex, message: '' }}
              />
              <TableComponent.select
                target={'total_analysis_type'}
                record={record}
                options={typeOptions}
                onChange={onChangeText}
                regEx={{ pattern: AnyRegex, message: '' }}
              />
            </div>
          )}
        />
        <Column
          title={MSG_TABLE_TITLE_DELETE}
          dataIndex="delete"
          key="delete"
          render={(_, record) => (
            <TableComponent.delete
              record={record}
              deleteHandler={deleteHandler}
              type={'custom'}
            />
          )}
        />
      </Table>
    </div>
  );
};
AnalysisTable.propTypes = {
  dataSource: PropTypes.array,
  deleteHandler: PropTypes.func,
  columnOptions: PropTypes.object,
  typeOptions: PropTypes.array,
  onChangeText: PropTypes.func,
  onClickScript: PropTypes.func,
};

const AnalysisSetting = ({ data, onChange, type }) => {
  const {
    ruleStepConfig,
    updateAnalysisInfo,
    analysisStepInfo,
    funcStepInfo,
  } = useRuleSettingInfo();
  const [config, setConfig] = useState(undefined);
  const [filterCSelect, setFilterCSelect] = useState([]);
  const [scriptRun, setScriptRun] = useState(false);
  const [filterKey, setFilterKey] = useState([]);
  const [editScript, setEditScript] = useState({
    visible: false,
    record: undefined,
    target: undefined,
    column_script_default: undefined,
    column_script: undefined,
  });
  const { source_type } = funcStepInfo;
  const [form] = Form.useForm();
  const [dbList, setDbList] = useState([]);
  const setDeboundcedText = useDebouncedCallback(
    ({ target, record, value }) => onInputChange({ target, record, value }),
    100,
  );

  useQuery(
    [QUERY_KEY.STEP5_DATASOURCE_LIST],
    () => getRemoteDBInfo({ db_id: undefined }),
    {
      onSuccess: (info) => {
        setDbList(
          info?.items?.map((obj) => {
            return { id: obj.id, name: obj.name };
          }) ?? [],
        );
        console.log('[STEP5_DATASOURCE_LIST]info', info);
      },
    },
  );

  useQuery(
    [QUERY_KEY.STEP5_SQL_QUERY],
    () =>
      getAnalysisScriptPreview({
        obj: {
          db_id: analysisStepInfo?.script?.db_id,
          sql: analysisStepInfo?.script?.sql,
        },
      }),
    {
      enabled: Boolean(scriptRun),
      onError: (err) => {
        NotificationBox('ERROR', err.message);
        setScriptRun(false);
      },
      onSuccess: ({ info }) => {
        setScriptRun(false);
        const table = getTableForm({ info: info.data, max_row: 10 });
        notification.open({
          message: 'Result OK',
          description: (
            <div css={tableWrapper} style={{ minWidth: '600px' }}>
              <Table
                bordered
                pagination={false}
                columns={table.columns}
                dataSource={table.dataSource}
                size="middle"
                rowKey="key"
                scroll={{ x: 'max-content' }}
              />
            </div>
          ),
          duration: 0,
          placement: 'topLeft',
          icon: <TableOutlined style={{ color: '#108ee9' }} />,
        });
      },
    },
  );
  const ScriptModalSetVisible = (visible) => {
    setEditScript({ ...editScript, visible: visible });
  };
  const onChangeText = ({ record, target, value }) => {
    setDeboundcedText({ record, target, value });
  };
  const ScriptModalOnChange = (value) => {
    console.log('value', value);
    setDeboundcedText({
      target: editScript.target,
      record: editScript.record,
      value: value?.['column_script'] ?? undefined,
    });
  };
  const ScriptModalSelect = ({ target, record, value, type }) => {
    if (type === SCRIPT_SELECT) {
      console.log('SCRIPT_SELECT');
      setEditScript({
        ...editScript,
        visible: true,
        record: record,
        target:
          target === 'total_analysis' ? 'total_analysis' : 'group_analysis',
        column_script:
          value ?? false ? value : editScript.column_script_default,
      });
    }
  };
  const RunHandler = () => {
    console.log('RunHandler');
    setScriptRun(true);
  };
  const handleDelete = (key) => {
    const dataSource = [...analysisStepInfo.items];
    updateAnalysisInfo({
      ...analysisStepInfo,
      items: dataSource.filter((item) => item.key !== key),
    });
  };
  const handleAdd = () => {
    const dataSource = [...analysisStepInfo?.items] ?? [];
    let newData = {
      ['key']: '',
      title: '',
      group_analysis_type: '',
      group_analysis: '',
      total_analysis_type: '',
      total_analysis: '',
      source_col: '',
    };
    newData.key =
      dataSource.length === 0
        ? 0
        : Math.max(...dataSource.map((obj) => obj.key)) + 1;
    updateAnalysisInfo({
      ...analysisStepInfo,
      items: [...dataSource, newData],
    });
  };
  const updateFilter = (filter_list) => {
    const getRowData = (row, key) => {
      return Object.entries(row ?? {}).map((obj) => obj[1][key]);
    };
    const step4 =
      type === E_SINGLE_TYPE
        ? ruleStepConfig.find((obj) => obj.step === E_STEP_4)?.data ?? //local
          ruleStepConfig.find((obj) => obj.step === E_STEP_2)?.data ?? //remote,sql
          []
        : ruleStepConfig.find((obj) => obj.step === E_STEP_2)?.data?.data ?? [];
    setFilterKey(filter_list);
    setFilterCSelect(
      filter_list.map((v1) => {
        let arr = [];
        if (Array.isArray(step4)) {
          step4.map((o) =>
            Object.entries(o).forEach(([, value]) => {
              Object.assign(arr, getRowData(value.row, v1));
            }),
          );
        } else {
          arr = getRowData(step4?.row ?? step4?.data?.row, v1);
        }
        return {
          label: v1,
          options: arr.filter((i, j) => arr.indexOf(i) === j) ?? [],
        };
      }),
    );
    console.log('filter_list', filter_list);
  };

  const onInputChange = ({ record, target, value }) => {
    const dataSource = [...analysisStepInfo.items];
    const checkType = (target) => {
      if (target === 'total_analysis_type') {
        return value === CUSTOM_SELECT ||
          value === SEQUENTIAL_SELECT ||
          value === SCRIPT_SELECT
          ? { [target]: value, ['total_analysis']: '' }
          : { [target]: value, ['total_analysis']: value };
      }
      if (target === 'group_analysis_type') {
        return value === CUSTOM_SELECT ||
          value === SEQUENTIAL_SELECT ||
          value === SCRIPT_SELECT
          ? { [target]: value, ['group_analysis']: '' }
          : { [target]: value, ['group_analysis']: value };
      }
      return undefined;
    };
    if (target === 'total_analysis_type' || target === 'group_analysis_type') {
      ScriptModalSelect({
        target:
          target === 'total_analysis_type'
            ? 'total_analysis'
            : 'group_analysis',
        record: record,
        value: null,
        type: value,
      });
    }
    updateAnalysisInfo({
      ...analysisStepInfo,
      items: dataSource.map((obj) =>
        obj.key === record.key
          ? Object.assign({}, obj, checkType(target) ?? { [target]: value })
          : obj,
      ),
    });
  };

  useEffect(() => {
    console.log('[STEP5]data: ', data);
    const ruleConfig = ruleStepConfig.find(
      (item) =>
        item?.config?.src_col_list !== undefined ||
        item?.data?.src_col_list !== undefined ||
        item.config?.analysis?.calc_type !== undefined ||
        item.config?.analysis?.setting?.calc_type !== undefined ||
        item.data?.analysis?.calc_type !== undefined ||
        item.data?.analysis?.setting?.calc_type !== undefined ||
        item.data?.calc_type !== undefined,
    );
    console.log('[STEP5]ruleConfig: ', ruleConfig);
    let srcColList = [];
    if (type === E_MULTI_TYPE) {
      ruleConfig?.data?.data.map((obj) =>
        Object.entries(obj).forEach(([key, val]) =>
          srcColList.push({
            label: key,
            value: key,
            children: val.src_col_list.map((obj) => ({
              label: obj,
              value: obj,
            })),
          }),
        ),
      );
    } else {
      srcColList =
        ruleConfig?.data?.src_col_list ??
        ruleConfig?.data?.data?.src_col_list ??
        ruleConfig?.config?.analysis?.setting.src_col_list ??
        [];
    }
    console.log('[STEP5]SrcColList: ', srcColList);
    setConfig(
      Object.assign(
        {},
        {
          src_col_list: srcColList,
          filter_key_list:
            ruleConfig?.data?.filter_key_list ?? //local
            ruleConfig?.data?.data?.filter_key_list ?? //remote, remote
            ruleConfig?.config?.analysis?.setting.filter_key_list ??
            ruleConfig?.data?.analysis?.filter_key_list ??
            [],
          aggregation_type:
            ruleConfig?.config?.analysis?.setting.aggregation_type ??
            ruleConfig?.data?.analysis?.setting.aggregation_type ??
            ruleConfig?.data?.setting.aggregation_type ??
            [],
          calc_type:
            ruleConfig?.config?.analysis?.setting.calc_type ??
            ruleConfig?.data?.analysis?.setting.calc_type ??
            ruleConfig?.data?.setting.calc_type ??
            [],
        },
      ),
    );
    setEditScript((prevState) => ({
      ...prevState,
      column_script_default:
        ruleConfig?.config?.analysis?.setting?.column_script_default ??
        ruleConfig?.data?.analysis?.setting?.column_script_default ??
        ruleConfig?.data?.setting?.column_script_default ??
        '',
    }));
    updateFilter(analysisStepInfo?.filter_default?.map((obj) => obj.key) ?? []);
    if (analysisStepInfo?.type === undefined) {
      let items =
        ruleConfig?.config?.analysis?.setting?.items ?? //source === local
        ruleConfig?.data?.setting?.items ?? //source === remote/SQL
        ruleConfig?.data?.analysis?.setting?.items ?? //multi/source === local
        [];
      if (type === MSG_MULTI) {
        items = items.map((item) => ({
          ...item,
          source_col: (item?.source_col?.split(',') ?? []).map((obj) =>
            obj.split('/'),
          ),
        }));
      }
      updateAnalysisInfo({
        ...analysisStepInfo,
        type:
          ruleConfig?.config?.analysis?.type ?? //source === local
          ruleConfig?.data?.type ?? //source === remote/SQL
          ruleConfig?.data?.analysis?.type ?? //multi/source === local
          'setting',
        script:
          ruleConfig?.config?.analysis?.script ?? //source === local
          ruleConfig?.data?.script ?? //source === remote/SQL
          ruleConfig?.data?.analysis?.script ?? //multi/source === local
          {},
        items: items.map((obj, index) => {
          return { ...obj, key: index + 1 };
        }),
        aggregation_default:
          ruleConfig?.config?.analysis?.setting?.aggregation_default ?? //source === local
          ruleConfig?.data?.setting?.aggregation_default ?? //source === remote/SQL
          ruleConfig?.data?.analysis?.setting?.aggregation_default ?? //source === remote/SQL
          {},
        filter_default:
          ruleConfig?.config?.analysis?.setting?.filter_default ?? //source === local
          ruleConfig?.data?.setting?.filter_default ?? //source === remote/SQL
          ruleConfig?.data?.analysis?.setting?.filter_default ?? //source === remote/SQL
          [],
      });
    }
  }, []);

  const filteredOptions =
    config?.filter_key_list?.filter((o) => !filterKey.includes(o)) ?? [];

  const onFormLayoutChange = (e) => {
    const v = getParseData(e);
    switch (v.id) {
      case 'filter_key':
        {
          const filter_list = [...analysisStepInfo.filter_default];
          updateFilter(v.value);
          if (v.value.length < filter_list.length) {
            const copy =
              filter_list.filter((obj) => v.value.includes(obj.key)) ?? [];
            updateAnalysisInfo({
              ...analysisStepInfo,
              filter_default: copy,
            });
          } else if (v.value.length > filter_list.length) {
            const copy = v.value.map(
              (obj) =>
                filter_list.find((obj2) => obj2.key === obj) ?? {
                  key: obj,
                  val: null,
                },
            );
            updateAnalysisInfo({
              ...analysisStepInfo,
              filter_default: copy,
            });
          }
        }
        break;
      case 'group_by':
        onChange({ ['group_value']: '' });
        form.setFieldsValue({ ['group_value']: '' });
        updateAnalysisInfo({
          ...analysisStepInfo,
          aggregation_default: {
            ['type']: v.value,
            ['val']: '',
          },
        });
        break;
      case 'group_value':
        updateAnalysisInfo({
          ...analysisStepInfo,
          aggregation_default: {
            ...analysisStepInfo.aggregation_default,
            ['val']: form.getFieldValue('group_value'),
          },
        });
        break;
      case 'type':
        updateAnalysisInfo({
          ...analysisStepInfo,
          [v.id]: v.value,
        });
        break;
      case 'db_id':
      case 'sql':
      case 'use_script':
        updateAnalysisInfo({
          ...analysisStepInfo,
          script: {
            ...analysisStepInfo.script,
            [v.id]: v.value,
          },
        });
        break;
      case 'file_name':
        {
          const fileName = getFileName(v.value);
          updateAnalysisInfo({
            ...analysisStepInfo,
            script: {
              ...analysisStepInfo.script,
              file_name: fileName,
              use_script: v.value !== null,
            },
          });
          onChange({ step5_script: v.value });
        }
        break;
      default:
        {
          const copy = analysisStepInfo?.filter_default.map((obj) =>
            obj.key === v.id ? { ...obj, ['val']: v.value } : obj,
          );
          updateAnalysisInfo({
            ...analysisStepInfo,
            filter_default: copy,
          });
        }

        break;
    }
  };
  if (config === undefined) return <></>;

  const AnalysisSetting = css`
    max-width: 85%;
    min-width: 75%;
    & .ant-col.ant-form-item-label.ant-form-item-label-left {
      flex-basis: 114px;
    }
    & .analysis-by {
      margin-bottom: 1rem;
      & .ant-radio-button-wrapper {
        color: #8c8c8c;
      }
      & .ant-radio-button-wrapper-checked {
        color: #fff !important;
      }
      & .ant-radio-button-wrapper:not(:first-of-type)::before {
        width: 0px;
      }
      & .ant-form-item-label {
        max-width: 130px;
      }
      & .ant-form-item-control-input {
        max-width: 870px;
      }
    }
  `;
  const step5_aggregation_style = css`
    margin: 10px 0px;
    & .ant-form-item-control-input-content {
      & > div {
        &:last-of-type {
          & .ant-form-item-control-input {
            width: 243px;
          }
        }
      }
    }
  `;
  const step5_script_data_style = css`
    & form.ant-form.ant-form-horizontal {
      margin-left: 114px;
    }
  `;
  console.log('filterCSelect', filterCSelect);

  return (
    <div css={AnalysisSetting}>
      <Collapse defaultActiveKey={[1, 2]}>
        <Panel header={MSG_PREVIOUS_TABLE} key="1">
          <div
            style={{
              fontWeight: '14px',
              margin: '10px',
              display: 'flex',
              justifyContent: 'center',
            }}
          >
            {type === E_SINGLE_TYPE ? (
              source_type === MSG_LOCAL ? (
                <Step4_Setting.view_preview data={data} />
              ) : (
                <Step2_Setting.view_preview data={data} />
              )
            ) : (
              <Step2_Multi_Setting.view_preview data={data} type={type} />
            )}
          </div>
        </Panel>
        <Panel header={MSG_STEP5_ANALYSIS} key="2">
          <div className="analysis-by">
            <span css={{ fontWeight: 700, color: '#096dd9' }}>
              Analysis By :
            </span>
            <Radio.Group
              value={analysisStepInfo?.type ?? 'setting'}
              buttonStyle="solid"
              onChange={(e) => onFormLayoutChange({ type: e.target.value })}
            >
              <Radio.Button
                value="setting"
                style={{
                  marginLeft: '8px',
                  borderRadius: '8px',
                  borderColor: 'transparent',
                  '&:before': { backgroundColor: 'transparent' },
                }}
              >
                UserSetting
              </Radio.Button>
              <Radio.Button
                value="script"
                style={{
                  margin: '0px 3px',
                  borderRadius: '8px',
                  borderColor: 'transparent',
                  '&:before': { backgroundColor: 'transparent' },
                }}
              >
                Script
              </Radio.Button>
              <Radio.Button
                value="none"
                style={{
                  margin: '0px 3px',
                  borderRadius: '8px',
                  borderColor: 'transparent',
                  '&:before': { backgroundColor: 'transparent' },
                }}
              >
                None
              </Radio.Button>
            </Radio.Group>
          </div>
          {(analysisStepInfo?.type ?? 'setting') === 'setting' ? (
            <div>
              <div css={{ margin: '10px 10px' }}>
                <Divider orientation={'left'} style={{ fontWeight: 700 }}>
                  {'Analysis Setting'}{' '}
                </Divider>
                <div>
                  <Button
                    onClick={() => handleAdd()}
                    type="primary"
                    style={{ marginBottom: 16, marginTop: 10 }}
                  >
                    Add a row
                  </Button>
                </div>
                <div css={tableWrapper} style={{ fontWeight: '12px' }}>
                  <AnalysisTable
                    dataSource={analysisStepInfo?.items ?? []}
                    columnOptions={{
                      type: type,
                      options: config?.src_col_list ?? [],
                    }}
                    typeOptions={config?.calc_type ?? []}
                    deleteHandler={handleDelete}
                    onChangeText={onChangeText}
                    onClickScript={ScriptModalSelect}
                  />
                </div>
              </div>
            </div>
          ) : (
            <></>
          )}
          <div css={tableWrapper} style={{ fontWeight: '12px' }}>
            <Form
              {...{ labelCol: { span: 5 }, wrapperCol: { span: 35 } }}
              form={form}
              onValuesChange={onFormLayoutChange}
              initialValues={{
                ['group_by']: analysisStepInfo?.aggregation_default?.type ?? '',
                ['group_value']:
                  analysisStepInfo?.aggregation_default?.val ?? '',
                ['filter_key']:
                  analysisStepInfo?.filter_default.map((obj) => obj.key) ?? [],
              }}
            >
              <ScriptEdit
                target={'column_script'}
                script={editScript.column_script}
                visible={editScript.visible}
                title={'Python Editor'}
                onChangeScript={ScriptModalOnChange}
                setVisible={ScriptModalSetVisible}
              />
              {(analysisStepInfo?.type ?? 'setting') === 'setting' ? (
                <div css={step5_aggregation_style}>
                  <Form.Item label={MSG_STEP5_AGGREGATION}>
                    <Form.Item
                      name={'group_by'}
                      style={{ display: 'inline-block' }}
                      validateTrigger={['onChange']}
                      validateStatus={
                        AnyRegex.test(
                          analysisStepInfo?.aggregation_default?.type,
                        ) ?? true
                          ? ''
                          : analysisStepInfo?.aggregation_default?.type ?? false
                          ? 'error'
                          : 'warning'
                      }
                    >
                      <Select
                        style={{ width: '150px' }}
                        value={
                          analysisStepInfo?.aggregation_default?.type ?? ''
                        }
                      >
                        {
                          // eslint-disable-next-line react/jsx-key
                          config.aggregation_type.map((item, idx) => {
                            return (
                              <Option
                                key={`aggregation_type_${idx}`}
                                value={item}
                              >
                                {item}
                              </Option>
                            );
                          })
                        }
                      </Select>
                    </Form.Item>
                    <Form.Item
                      name={'group_value'}
                      style={{
                        display: 'inline-block',
                        marginLeft: '1rem',
                        Width: '233px',
                      }}
                      validateTrigger={['onChange']}
                      validateStatus={
                        (analysisStepInfo?.aggregation_default?.type ?? '') ===
                        DEFINE_GROUP_BY_PERIOD
                          ? AnalysisPeriodRegex.test(
                              analysisStepInfo?.aggregation_default?.val,
                            ) ?? true
                            ? ''
                            : analysisStepInfo?.aggregation_default?.type ??
                              false
                            ? 'error'
                            : 'warning'
                          : (analysisStepInfo?.aggregation_default?.type ??
                              '') === DEFINE_GROUP_BY_COLUMN
                          ? AnyRegex.test(
                              analysisStepInfo?.aggregation_default?.val ??
                                config?.filter_key_list[0],
                            ) ?? true
                            ? ''
                            : analysisStepInfo?.aggregation_default?.type ??
                              false
                            ? 'error'
                            : 'warning'
                          : ''
                      }
                    >
                      {(analysisStepInfo?.aggregation_default?.type ?? '') ===
                      DEFINE_GROUP_BY_PERIOD ? (
                        <Input
                          allowClear
                          value={analysisStepInfo?.aggregation_default?.val}
                          placeholder={`with input ${DEFINE_GROUP_BY_PERIOD}`}
                        />
                      ) : (analysisStepInfo?.aggregation_default?.type ??
                          '') === DEFINE_GROUP_BY_COLUMN ? (
                        <Select
                          allowClear
                          value={
                            analysisStepInfo?.aggregation_default?.val ??
                            config?.filter_key_list[0] ??
                            ''
                          }
                          placeholder={`with select ${DEFINE_GROUP_BY_COLUMN}`}
                        >
                          {config.filter_key_list.map((item, idx) => {
                            return (
                              <Option key={idx} value={item}>
                                {item}
                              </Option>
                            );
                          })}
                        </Select>
                      ) : (
                        <></>
                      )}
                    </Form.Item>
                  </Form.Item>
                </div>
              ) : (
                <></>
              )}
              {(analysisStepInfo?.type ?? 'setting') !== 'script' ? (
                <div css={{ margin: '10px 10px' }}>
                  <Divider orientation={'left'} style={{ fontWeight: 700 }}>
                    {'Filter Setting'}{' '}
                  </Divider>
                  <Form.Item
                    label={MSG_STEP5_FILTER_KEY}
                    style={{
                      width: '1200px',
                      position: 'relative',
                      right: '10px',
                    }}
                  >
                    <Form.Item name={'filter_key'} style={{ display: 'flex' }}>
                      {
                        <Select
                          placeholder="Please select"
                          value={filterKey ?? []}
                          mode="multiple"
                          maxTagTextLength={10}
                          maxTagCount={'responsive'}
                        >
                          {filteredOptions?.map((item, idx) => {
                            return (
                              <Option
                                key={idx}
                                value={item}
                                disabled={
                                  filterKey.length === DEFINE_MAX_SELECT ?? true
                                }
                              >
                                {item}
                              </Option>
                            );
                          }) ?? <></>}
                        </Select>
                      }
                    </Form.Item>
                    <div css={filterWrapper}>
                      {filterCSelect.length > 0 ? (
                        filterCSelect.map((item, index) => {
                          const tmp = analysisStepInfo?.filter_default.find(
                            (obj) => obj.key === item.label,
                          );
                          console.log('tmp:', tmp);
                          return (
                            <Form.Item
                              {...tailLayout}
                              name={item.label}
                              label={item.label}
                              key={`fs_${index}`}
                            >
                              <Select
                                mode={'multiple'}
                                value={tmp?.val ?? []}
                                maxTagCount={'responsive'}
                                maxTagTextLength={10}
                                allowClear
                              >
                                {item.options.map((opt, idx) => {
                                  return (
                                    <Option key={idx} value={opt}>
                                      {opt}
                                    </Option>
                                  );
                                })}
                              </Select>
                            </Form.Item>
                          );
                        })
                      ) : (
                        <></>
                      )}
                    </div>
                  </Form.Item>
                </div>
              ) : (
                <></>
              )}
            </Form>
          </div>
          {(analysisStepInfo?.type ?? 'setting') === 'script' ? (
            <>
              <div css={{ margin: '10px 10px' }}>
                <div css={step5_convert_script_style}>
                  <Divider orientation="left" style={{ fontWeight: 700 }}>
                    {'Request Reference Data'}{' '}
                  </Divider>
                  <div style={{ maxWidth: '639px' }}>
                    <div css={step5_script_button_style}>
                      <InputForm.select
                        defaultV={analysisStepInfo?.script?.db_id ?? ''}
                        options={dbList ?? []}
                        formLabel={'Data Source'}
                        formName={'db_id'}
                        changeFunc={onFormLayoutChange}
                        required={true}
                      />
                      <Button
                        onClick={() => RunHandler()}
                        disabled={
                          Boolean(
                            !!(analysisStepInfo?.script?.db_id ?? false) &&
                              !!(analysisStepInfo?.script?.sql ?? false),
                          ) === false
                        }
                        icon={<PlayCircleFilled />}
                      >
                        RUN
                      </Button>
                    </div>
                    <div css={step5_script_data_style}>
                      <InputForm.textarea
                        formName={'sql'}
                        value={analysisStepInfo?.script?.sql ?? ''}
                        changeFunc={onFormLayoutChange}
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div css={{ margin: '10px 10px' }}>
                <div css={step5_convert_script_style}>
                  <Divider orientation="left" style={{ fontWeight: 700 }}>
                    {'Select Analysis Script'}{' '}
                  </Divider>
                  <div
                    css={{
                      display: 'flex',
                      flexDirection: 'column',
                      maxWidth: '270px',
                    }}
                  >
                    <div style={{ maxWidth: '700px' }}>
                      <InputForm.file
                        btnMsg={MSG_UPLOAD_SCRIPT}
                        formLabel={'script File: '}
                        formName={'file_name'}
                        changeFunc={onFormLayoutChange}
                        file={
                          analysisStepInfo?.script?.file_name ??
                          config?.script?.file_name ??
                          false
                            ? [
                                {
                                  uid: 1,
                                  name:
                                    analysisStepInfo?.script?.file_name ??
                                    config?.script?.file_name,
                                  status: 'done',
                                },
                              ]
                            : []
                        }
                        layout={{
                          labelAlign: 'left',
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <></>
          )}
        </Panel>
      </Collapse>
    </div>
  );
};
AnalysisSetting.propTypes = {
  data: PropTypes.object,
  onChange: PropTypes.func,
  type: PropTypes.string,
};
export default AnalysisSetting;
