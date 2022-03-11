import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { css } from '@emotion/react';
//import { useParams } from 'react-router';
import { Avatar, Button, Divider, List, Spin, Table, Tabs } from 'antd';
import { FormCard } from '../../../UI/atoms/Modal';
import useCommonJob from '../../../../hooks/useBasicInfo';
import InputForm from '../../../UI/atoms/Input/InputForm';
import {
  CheckOutlined,
  ClockCircleOutlined,
  CloseOutlined,
  EditOutlined,
  PaperClipOutlined,
} from '@ant-design/icons';
import {
  MSG_LOCAL,
  MSG_MULTI,
  MSG_REMOTE,
  MSG_SQL,
} from '../../../../lib/api/Define/Message';
import {
  getFindData,
  getParseData,
  getTableForm,
} from '../../../../lib/util/Util';
import StatusTag from '../../../UI/atoms/StatusTag/StatusTag';
import { useQuery } from 'react-query';
import { QUERY_KEY } from '../../../../lib/api/Define/QueryKey';
import {
  getJobIdStep2MultiFunc,
  getStep2MultiPreview,
  getStep2MultiResource,
} from '../../../../lib/api/axios/useJobStepRequest';
import { StepInputForm } from '../../../UI/organisms/StepInputForm';
import Text from 'antd/lib/typography/Text';
import useRuleSettingInfo from '../../../../hooks/useRuleSettingInfo';
import { AnyRegex } from '../../../../lib/util/RegExp';
import { NotificationBox } from '../../../UI/molecules/NotificationBox';
import {
  getEquipmentList,
  getEquipmentValidDate,
  getRequestParam,
} from '../../../../lib/api/axios/requests';
import { getConvertJobStatus } from '../../../../lib/api/axios/useJobSettingRequest';
import {
  E_MULTI_TYPE,
  E_SINGLE_TYPE,
  E_STEP_2,
  E_STEP_3,
  E_STEP_4,
  R_OK,
} from '../../../../lib/api/Define/etc';
import { MultiJobStepConf as steps } from '../../../../hooks/useJobStepInfo';
import { useParams } from 'react-router';
import DeleteButton from '../../../UI/molecules/PopConfirmButton/DeleteButton';

const tableWrapper = css`
  display: contents;
`;

const FormWrapper = css`
  min-width: 500px;
  min-height: 550px;
  background-color: #f0f5ff;
  margin: 1rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
  .ant-list-item-meta {
    align-items: center;
  }
  .ant-list-item-meta-avatar {
    & span {
      background: #6cd900;
      color: #ffffff;
    }
  }
  & h4 {
    overflow: hidden;
    text-overflow: ellipsis;
  }
  & .button-wrapper > button + button {
    margin-left: 6px;
  }
  & .ant-btn-dashed[disabled] {
    margin-left: 6px;
  }
  & .status-tag-wrapper {
    width: 120px;
    text-align: -webkit-center;
    & > span {
      margin-right: 0;
    }
  }
`;
const TabWrapper = css`
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
const FunctionListWrapper = css`
  min-height: calc(59%);
  font-weight: 400;
  max-height: 385px;
`;

const PreviewRequest = async ({
  data,
  funcStepInfo,
  updateFuncInfo,
  setData,
  func_id,
}) => {
  const LocalStatus = async ({ rid }) => {
    return await getConvertJobStatus({ jobId: rid });
  };
  const MultiRequest = async (object) => {
    return await getJobIdStep2MultiFunc({
      LocalStatus,
      object,
      data:
        object?.source_type === MSG_LOCAL
          ? data.src_file.find((o) => o.multi_info_id === object.multi_info_id)
              ?.value
          : undefined,
    })
      .then((info) => {
        return info;
      })
      .catch((e) => {
        if (e.response) {
          const {
            data: { msg },
          } = e.response;
          console.log(e.response);
          NotificationBox('error', msg);
        }
        return undefined;
      });
  };
  let jobList = [...funcStepInfo.list];
  let errFlag = false;
  let currentJob = jobList.find((o) => o.rid === undefined);
  if (currentJob !== undefined) {
    updateFuncInfo({
      ...funcStepInfo,
      list: jobList,
      currentJob: currentJob.multi_info_id,
    });
  }
  do {
    if (currentJob ?? false) {
      await MultiRequest(currentJob)
        .then((jobInfo) => {
          if (jobInfo === undefined) errFlag = true;
          else {
            console.log('done', jobInfo);
            jobList = jobList.map((obj) => {
              return obj.multi_info_id === jobInfo.id
                ? {
                    ...obj,
                    status: jobInfo.status,
                    rid: jobInfo.rid,
                    fid: jobInfo.fid,
                  }
                : obj;
            });
            currentJob = jobList.find(
              (o) =>
                o.rid === undefined &&
                o.multi_info_id !== (jobInfo?.id ?? undefined),
            );
            console.log('done!!!', currentJob);
            if (currentJob ?? false) {
              jobList = jobList.map((o) =>
                o.multi_info_id === currentJob.multi_info_id
                  ? { ...currentJob, status: 'processing' }
                  : o,
              );
            }
            updateFuncInfo({
              ...funcStepInfo,
              list: jobList,
              currentJob: currentJob?.multi_info_id ?? undefined,
            });
          }
        })
        .catch((err) => {
          NotificationBox('ERROR', err.message, 0);
          errFlag = true;
        })
        .finally(() => {
          if (errFlag) {
            updateFuncInfo({
              ...funcStepInfo,
              list: jobList.map((obj) => {
                return obj.multi_info_id === currentJob.multi_info_id
                  ? {
                      ...obj,
                      status: 'error',
                    }
                  : obj;
              }),
              currentJob: undefined,
            });
            currentJob = undefined;
          }
        });
    }
  } while (currentJob ?? false);
  const result = jobList.find(
    (o) => o.rid === undefined || !['completed', 'success'].includes(o.status),
  );
  if (result === undefined) {
    return await getStep2MultiPreview({
      list: jobList ?? [],
      func_id: func_id,
      use_org_analysis: funcStepInfo?.use_org_analysis ?? false,
    })
      .then(({ info }) => {
        console.log('================4=================', info);
        const tableData = {};
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
        setData({
          ...data,
          log_header: Object.fromEntries(
            Object.entries(tableData).map(([key, val]) => [key, val.columns]),
          ),
          log_data: Object.fromEntries(
            Object.entries(tableData).map(([key, val]) => [
              key,
              val.dataSource,
            ]),
          ),
          log_error: undefined,
        });
        updateFuncInfo({
          ...funcStepInfo,
          list:
            jobList.map((o) => {
              return { ...o, status: 'success', currentJob: undefined };
            }) ?? [],
        });
        return { data: info, step: E_STEP_2 };
      })
      .catch((err) => NotificationBox('ERROR', err.message, 0));
  } else {
    return { data: undefined, step: E_STEP_2 };
  }
};
const NextButtonEvent = async ({
  setLoading,
  funcStepInfo,
  updateFuncInfo,
  data,
  func_id,
}) => {
  const { use_org_analysis } = funcStepInfo;
  const isEditMode = !!(func_id ?? false);
  setLoading(true);
  if (EnableCheck({ funcStepInfo })) {
    const result = await PreviewRequest({
      func_id,
      funcStepInfo,
      updateFuncInfo,
      data: data.data,
      setData: data.func,
    }).then((_) => _);
    console.log('PreviewResult', result);
    if (result.step === E_STEP_2) {
      console.log('use_org_analysis', use_org_analysis);
      if (!isEditMode) {
        const { info, status } = await getRequestParam(
          `${steps[E_STEP_2].new}`,
          undefined,
        );
        if (status === R_OK) {
          return {
            info: { config: info },
            next: use_org_analysis ?? false ? E_STEP_4 : E_STEP_3,
            preview: { current: E_STEP_2, info: result.data },
          };
        }
      } else {
        return {
          info: undefined,
          next: use_org_analysis ?? false ? E_STEP_4 : E_STEP_3,
          preview: { current: E_STEP_2, info: result.data },
        };
      }
    }
  }
  return {
    info: undefined,
    next: E_STEP_2,
    preview: undefined,
  };
};
const PreviewButtonEvent = async ({
  updateFuncInfo,
  funcStepInfo,
  func_id,
  setData,
  data,
}) => {
  return PreviewRequest({
    updateFuncInfo,
    funcStepInfo,
    func_id,
    setData,
    data,
  });
};
const PreviousButtonEvent = ({ funcStepInfo }) => {
  return !funcStepInfo?.currentJob ?? true;
};

const EnableCheck = ({ funcStepInfo }) => {
  const list = funcStepInfo?.list ?? [];
  if (list.length > 0) {
    const result = list.map((o) => {
      return (
        Boolean(AnyRegex.test(o?.tab_name ?? '')) &&
        (o.source_type === MSG_LOCAL
          ? Boolean(o?.info.file_name?.length ?? 0)
          : o.source_type === MSG_SQL
          ? Boolean(o?.info?.db_id ?? 0) && Boolean(o?.info?.sql?.length ?? 0)
          : o.source_type === MSG_REMOTE
          ? Boolean(o?.info?.db_id ?? 0) &&
            Boolean(o?.info?.equipment_name?.length ?? 0) &&
            Boolean(o?.info?.selected?.start?.length ?? 0) &&
            Boolean(o?.info?.selected?.end?.length ?? 0)
          : false)
      );
    });
    return (
      (!funcStepInfo?.currentJob ?? true) &&
      result.filter((o) => o === false).length === 0
    );
  } else {
    return false;
  }
};

/*============================================================================
==                         STEP 2 CONTENTS                                  ==
============================================================================*/
const initData = {
  multi_info_id: '',
  sub_func_id: '',
  tab_name: '',
  info: '',
  source_type: '',
  status: '',
  form: undefined,
};
const ContentsForm = ({ onChange, data }) => {
  const { func_id } = useParams();
  const { supportUrl, MenuInfo } = useCommonJob();
  const [funcList, setFuncList] = useState([]);
  const [selected, setSelected] = useState(0);
  const { funcStepInfo, updateFuncInfo, ruleStepConfig } = useRuleSettingInfo();

  const customSwitch = {
    checkedChildren: <CheckOutlined />,
    unCheckedChildren: <CloseOutlined />,
  };
  const FuncInfo =
    funcStepInfo?.list?.find((obj) => obj.multi_info_id === selected) ??
    undefined;

  const getFormObject = (form, source) => {
    return source === MSG_LOCAL
      ? {
          log_name: getFindData(form, 'log_name', 'content'),
          file_name: form?.[2]?.items?.[0]?.file_name ?? undefined,
        }
      : source === MSG_REMOTE
      ? {
          db_id: getFindData(form, 'db_id', undefined),
          table_name: getFindData(form, 'table_name', undefined),
          user_fab: getFindData(form, 'user_fab', undefined),
          equipment_name: getFindData(form, 'equipment_name', undefined),
          period: getFindData(form, 'period', undefined),
          selected: getFindData(form, 'period', undefined),
        }
      : source === MSG_SQL
      ? {
          db_id: getFindData(form, 'db_id', undefined),
          sql: getFindData(form, 'sql', undefined),
        }
      : {};
  };
  //============================================================================
  useQuery(
    [QUERY_KEY.STEP2_MULTI_RESOURCE, selected],
    () =>
      getStep2MultiResource({
        func_id: FuncInfo?.sub_func_id ?? 0,
      }),
    {
      enabled:
        !!selected &&
        Boolean(FuncInfo?.sub_func_id ?? false) &&
        (!FuncInfo?.form ?? true),
      onSuccess: ({ info }) => {
        console.log(info);
        const source_type = info.source_type ?? MSG_LOCAL;
        updateFuncInfo({
          ...funcStepInfo,
          list: funcStepInfo.list.map((obj) =>
            obj.multi_info_id === selected
              ? {
                  ...obj,
                  source_type: source_type,
                  tab_name:
                    obj?.tab_name ??
                    getFindData(info.form, 'tab_name', 'content'),
                  info: getFormObject(info.form, source_type),
                  form: info.form,
                }
              : obj,
          ),
        });
      },
    },
  );

  /* * *
   *  1. DB_ID & Table Name 하나라도 변경 되면, 요청을 한다.
   *  2. Edit 로 들어온 경우에도 user/Fab/Equipment 가 필요하다.
   * */

  useQuery(
    [
      QUERY_KEY.STEP2_USER_FAB_EQUIPMENT_LIST,
      FuncInfo?.info?.db_id,
      FuncInfo?.info?.table_name,
    ],
    () =>
      getEquipmentList({
        db_id: FuncInfo?.info?.db_id,
        table_name: FuncInfo?.info?.table_name,
      }),
    {
      enabled: !!FuncInfo?.info?.db_id && !!FuncInfo?.info?.table_name,
      onSuccess: ({ info }) => {
        updateFuncInfo({
          ...funcStepInfo,
          list: funcStepInfo.list.map((o) =>
            o.multi_info_id === selected ? { ...o, ...info } : o,
          ),
        });
      },
    },
  );

  /*
   *  1. DB_ID /TABLE_NAME/EQUIPMENT_NAME 이 설정 되면 Equipment 의 유효한 정보를 가져온다.
   * */

  useQuery(
    [
      QUERY_KEY.STEP2_EQUIPMENT_VALID_DATE,
      FuncInfo?.info?.db_id,
      FuncInfo?.info?.table_name,
      FuncInfo?.info?.equipment_name,
    ],
    () =>
      getEquipmentValidDate({
        db_id: FuncInfo?.info?.db_id,
        table_name: FuncInfo?.info?.table_name,
        equipment_name: FuncInfo?.info?.equipment_name,
      }),
    {
      enabled:
        !!FuncInfo?.info?.db_id &&
        !!FuncInfo?.info?.table_name &&
        !!FuncInfo?.info?.equipment_name,
      onSuccess: ({ info }) => {
        updateFuncInfo({
          ...funcStepInfo,
          list: funcStepInfo.list.map((o) =>
            o.multi_info_id === selected
              ? {
                  ...o,
                  info: {
                    ...o.info,
                    period: { start: info.start, end: info.end },
                    selected: { start: info.start, end: info.end },
                  },
                }
              : o,
          ),
        });
      },
    },
  );

  const ridinitialize = { rid: undefined, status: undefined };
  const ChangeFunc = (event) => {
    const item = getParseData(event);

    switch (item.id) {
      case 'tab_name':
        updateFuncInfo({
          ...funcStepInfo,
          list: funcStepInfo.list.map((o) =>
            o.multi_info_id === selected
              ? { ...o, ...event, ...ridinitialize }
              : o,
          ),
        });
        break;
      case 'src_file':
        {
          console.log('item.value', item.value);
          const files_name =
            item.value?.getAll('files').map((o) => o.name) ?? null;
          onChange({
            src_file:
              (data?.src_file?.findIndex((o) => o.multi_info_id === selected) ??
                -1) !== -1
                ? data?.src_file.map((o) =>
                    o.multi_info_id === selected
                      ? { ...o, value: item.value }
                      : o,
                  )
                : data?.src_file?.length > 0 ?? false
                ? [
                    ...data?.src_file,
                    { multi_info_id: selected, value: item.value },
                  ]
                : [{ multi_info_id: selected, value: item.value }],
          });
          updateFuncInfo({
            ...funcStepInfo,
            list: funcStepInfo.list.map((o) =>
              o.multi_info_id === selected
                ? {
                    ...o,
                    ...ridinitialize,
                    info: {
                      ...o.info,
                      file_name: files_name,
                    },
                  }
                : o,
            ),
          });
        }
        break;
      case 'use_org_analysis':
        console.log('use_org_analysis', item.value);
        updateFuncInfo({
          ...funcStepInfo,
          ...ridinitialize,
          use_org_analysis: item.value,
        });
        break;
      case 'db_id':
      case 'table_name':
      case 'equipment_name':
      case 'user_fab':
      case 'period':
        RemoteConfigChange(event);
        break;
    }
  };
  const RemoteConfigChange = (event) => {
    const item = getParseData(event);

    switch (item.id) {
      case 'equipment_name':
        updateFuncInfo({
          ...funcStepInfo,
          list: funcStepInfo.list.map((o) =>
            o.multi_info_id === selected
              ? {
                  ...o,
                  ...ridinitialize,
                  info: {
                    ...o.info,
                    [item.id]: item.value,
                    period: { start: '', end: '' },
                    selected: { start: '', end: '' },
                  },
                }
              : o,
          ),
        });
        break;
      case 'db_id':
        updateFuncInfo({
          ...funcStepInfo,
          list: funcStepInfo.list.map((o) =>
            o.multi_info_id === selected
              ? {
                  ...o,
                  ...ridinitialize,
                  info:
                    FuncInfo.source_type === MSG_REMOTE
                      ? {
                          ...o.info,
                          [item.id]: item.value,
                          equipment_name: '',
                          user_fab: '',
                          period: { start: '', end: '' },
                          selected: { start: '', end: '' },
                        }
                      : {
                          ...o.info,
                          [item.id]: item.value,
                        },
                }
              : o,
          ),
        });
        break;
      case 'user_fab':
        updateFuncInfo({
          ...funcStepInfo,
          list: funcStepInfo.list.map((o) =>
            o.multi_info_id === selected
              ? {
                  ...o,
                  ...ridinitialize,
                  info: {
                    ...o.info,
                    [item.id]: item.value,
                    equipment_name: '',
                    period: { start: '', end: '' },
                    selected: { start: '', end: '' },
                  },
                }
              : o,
          ),
        });
        break;
      case 'period':
        {
          updateFuncInfo({
            ...funcStepInfo,
            list: funcStepInfo.list.map((o) =>
              o.multi_info_id === selected
                ? {
                    ...o,
                    ...ridinitialize,
                    info: {
                      ...o.info,
                      selected: {
                        start: item.value.start,
                        end: item.value.end,
                      },
                    },
                  }
                : o,
            ),
          });
        }
        break;
    }
  };
  const addHandler = (id) => {
    console.log('addHandler', id);
    const formList = func_id
      ? ruleStepConfig[E_STEP_2].config.data.formList
      : [];
    const origin_id_list =
      formList.map((obj) => obj.multi_info_id).filter((o) => o ?? false) ?? [];
    console.log('origin_id_list', origin_id_list);
    const list = [...(funcStepInfo?.list ?? '')];
    const idList = [...list.map((obj) => obj.multi_info_id), ...origin_id_list];
    const func_info = supportUrl.find((obj) => obj.func === id) ?? {};
    const newData = { ...initData };
    const maxKeyValue = idList.length === 0 ? 0 : Math.max(...idList);
    newData.multi_info_id = maxKeyValue + 1;
    newData.sub_func_id = id;
    newData.category = func_info.category;
    newData.func_name = func_info.func_name;
    newData.tab_name = list.map((obj) => obj.sub_func_id).includes(id)
      ? `${func_info.func_name}_${list
          .map((obj) => obj.sub_func_id)
          .reduce((arr, e) => arr + (id === e), 0)}`
      : func_info.func_name;
    updateFuncInfo({
      ...funcStepInfo,
      list:
        funcStepInfo?.list ?? false
          ? [...funcStepInfo.list, newData]
          : [newData],
    });
    setSelected(maxKeyValue + 1);
  };

  const deleteHandler = (id) => {
    console.log('deleteHandler', id);
    const dInfo = funcStepInfo.list.find((obj) => obj.multi_info_id === id);
    updateFuncInfo({
      ...funcStepInfo,
      list: funcStepInfo.list.filter((obj) => obj.multi_info_id !== id),
    });
    if (dInfo.source_type === MSG_LOCAL) {
      onChange({
        src_file: data?.src_file?.filter((o) => o.multi_info_id !== id) ?? [],
      });
    }
    if (selected === id) {
      setSelected(0);
    }
  };
  //============================================================================

  useEffect(() => {
    setFuncList(
      MenuInfo.body
        ?.filter(
          (obj1) =>
            obj1?.func.length > 0 &&
            obj1.func.filter((o) => o.info.Source !== 'multi').length > 0,
        )
        .map((category) => {
          return {
            title: category.title,
            value: `category_${category.category_id}`,
            key: `category_${category.category_id}`,
            children: category.func
              ?.filter((o) => o.info.Source !== 'multi')
              .map((func) => {
                return {
                  title: func.title,
                  value: func.func_id,
                  key: func.func_id,
                };
              }),
          };
        }),
    );
    const tmpStepInfo = { ...funcStepInfo };

    if (func_id ?? false) {
      console.log('func_id', func_id);
      if (funcStepInfo.list === undefined) {
        //편집시 데이터 첫 로딩시 설정 자리
        const step2 = ruleStepConfig.find((step) => step.step === E_STEP_2)
          .config.data;
        const stepForm = step2.form;

        tmpStepInfo.list = step2.formList.map((o) => {
          const formKey = o['key'];
          const obj = Object.keys(initData).reduce(
            (acc, keys) =>
              o?.[keys] !== undefined ? { ...acc, [keys]: o[keys] } : acc,
            { key: o['key'] },
          );
          const info = getFormObject(stepForm[formKey], obj.source_type);
          return {
            form: step2.form[o.key],
            ...obj,
            info: info,
            rid: o.rid,
            fid: Array.isArray(o?.fid ?? []) ? o?.fid ?? [] : [+o?.fid],
            status: 'completed',
          };
        });
        console.log('tmpStepInfo', tmpStepInfo);
        tmpStepInfo.use_org_analysis = step2.use_org_analysis;
      }
    } else {
      tmpStepInfo.use_org_analysis = false;
    }
    tmpStepInfo.source_type = MSG_MULTI;
    updateFuncInfo(tmpStepInfo);
    setSelected(tmpStepInfo?.list?.[0]?.multi_info_id ?? 0);
    return () => {
      console.log('contents components unmount');
    };
  }, []);
  console.log('FuncInfo:', FuncInfo);
  //============================================================================

  return (
    <div
      css={{
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'center',
      }}
    >
      <div css={FormWrapper}>
        <div>
          <FormCard
            title={'1. Select Function'}
            formStyle={{ maxHeight: '110px' }}
          >
            <div>
              <InputForm.selectOption
                formName={'function'}
                changeFunc={addHandler}
                disabled={!!funcStepInfo?.currentJob ?? false}
                treeData={funcList}
              />
            </div>
          </FormCard>
          <Divider
            orientation={'left'}
            style={{ margin: '0px', background: 'rgb(240 245 255)' }}
          >
            <Text code style={{ fontSize: '13px' }}>
              Function List
            </Text>
          </Divider>
          <FormCard
            titleStyle={{ fontWeight: '400' }}
            formStyle={FunctionListWrapper}
          >
            <List
              itemLayout="horizontal"
              dataSource={funcStepInfo?.list ?? []}
              css={{ maxHeight: '300px', overflowY: 'auto' }}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Avatar icon={<PaperClipOutlined />} />}
                    title={`${
                      item?.key ??
                      item?.category.concat(
                        `/${item.func_name}/Tab name: ${item.tab_name}`,
                      )
                    }`}
                    description={
                      <div>
                        <span css={{ textIndent: '4px', display: 'block' }}>
                          {item?.source_type ?? ''
                            ? `Source: ${item.source_type}`
                            : ''}
                        </span>
                        <span
                          css={{
                            textIndent: '4px',
                            display: 'block',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {item?.info?.log_name ?? ''
                            ? `log_name: ${item.info.log_name}`
                            : ''}
                        </span>
                      </div>
                    }
                  />
                  <div className="status-tag-wrapper">
                    <div style={{ width: '80px' }}>
                      {item.status === 'success' ? (
                        <StatusTag status={'success'} />
                      ) : item?.status === 'error' ? (
                        <StatusTag status={'error'} />
                      ) : item.multi_info_id === funcStepInfo?.currentJob ? (
                        <StatusTag status={'processing'} />
                      ) : item?.rid ?? false ? (
                        <StatusTag
                          status={'waiting'}
                          color={'warning'}
                          icon={<ClockCircleOutlined />}
                        />
                      ) : (
                        <></>
                      )}
                    </div>
                  </div>
                  <div className="button-wrapper">
                    <Button
                      type="dashed"
                      icon={<EditOutlined />}
                      disabled={!!funcStepInfo?.currentJob ?? false}
                      onClick={() => setSelected(item.multi_info_id)}
                    />
                    <DeleteButton
                      disabled={!!funcStepInfo?.currentJob ?? false}
                      deleteHandler={() => deleteHandler(item.multi_info_id)}
                    />
                  </div>
                </List.Item>
              )}
            />
          </FormCard>
        </div>
        <div>
          <Divider
            orientation={'left'}
            style={{ margin: '0px', background: 'rgb(240 245 255)' }}
          />
          <FormCard
            title={'2. Use Original Analysis'}
            formStyle={{ maxHeight: '125px' }}
          >
            <div>
              <InputForm.switch
                formLabel={''}
                formName={'use_org_analysis'}
                changeFunc={ChangeFunc}
                custom={customSwitch}
              />
            </div>
          </FormCard>
        </div>
      </div>
      <div css={FormWrapper}>
        <div
          css={{
            backgroundColor: '#0F73BB',
            height: '55px',
            color: '#FFFFFF',
            padding: '16px 24px',
          }}
        >
          {FuncInfo?.key ??
            FuncInfo?.category.concat(`/${FuncInfo.func_name}`) ??
            ''}
        </div>
        {FuncInfo?.form?.map((item, idx) => (
          <div key={idx}>
            <FormCard title={item.title} titleStyle={{ fontWeight: '400' }}>
              <div>
                {item.items.map((idx2, i) => (
                  <StepInputForm
                    key={i}
                    data={
                      FuncInfo?.source_type === MSG_LOCAL ?? true
                        ? {
                            ...FuncInfo,
                            file_name: data?.src_file?.find(
                              (o) => o.multi_info_id === FuncInfo.multi_info_id,
                            )?.value,
                          }
                        : FuncInfo
                    }
                    item={item.items[i]}
                    changeFunc={ChangeFunc}
                  />
                ))}
              </div>
            </FormCard>
          </div>
        )) ?? (selected !== 0 ? <Spin tip=" Data Loading..." /> : <></>)}
        <div css={{ backgroundColor: '#0F73BB', height: '55px' }} />
      </div>
    </div>
  );
};
ContentsForm.propTypes = {
  onChange: PropTypes.func,
  data: PropTypes.object,
};
const { TabPane } = Tabs;
const PreviewForm = ({ data, type }) => {
  const [tabSetting, setTabSetting] = useState({ list: [], selected: '' });
  if (data == null) return <></>;
  const { log_header, log_data } = data;
  const TabChangeEvent = (e) => {
    setTabSetting((prev) => {
      return { ...prev, selected: e };
    });
  };

  useEffect(() => {
    if (type === E_MULTI_TYPE) {
      const keyList = Object.keys(log_header ?? {});
      setTabSetting({ list: keyList ?? [], selected: keyList[0] });
    }
  }, [log_header]);

  if (log_header === undefined || log_data === undefined) return <></>;
  if (type === E_SINGLE_TYPE) return <></>;

  return (
    <div css={{ display: 'inline-grid', width: '100%' }}>
      <Tabs
        type="card"
        onChange={TabChangeEvent}
        activeKey={tabSetting.selected}
        css={TabWrapper}
      >
        {tabSetting.list.map((tab) => (
          <>
            <TabPane tab={tab} key={tab}>
              <div css={tableWrapper}>
                <Table
                  bordered
                  pagination={false}
                  columns={log_header?.[tab] ?? []}
                  dataSource={log_data?.[tab] ?? []}
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
  );
};
PreviewForm.propTypes = {
  data: PropTypes.object,
  type: PropTypes.string,
};
const Step2_Multi_Setting = ({ children }) => {
  return <div>{children}</div>;
};

Step2_Multi_Setting.propTypes = {
  children: PropTypes.node,
};

Step2_Multi_Setting.btn_next = NextButtonEvent;
Step2_Multi_Setting.btn_previous = PreviousButtonEvent;
Step2_Multi_Setting.btn_preview = PreviewButtonEvent;
Step2_Multi_Setting.check_next = EnableCheck;
Step2_Multi_Setting.check_preview = EnableCheck;
Step2_Multi_Setting.view_contents = ContentsForm;
Step2_Multi_Setting.view_preview = PreviewForm;

export default Step2_Multi_Setting;
