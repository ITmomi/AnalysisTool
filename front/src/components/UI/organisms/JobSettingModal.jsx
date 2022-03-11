import React, { useEffect, useState } from 'react';
import { FormCard, Modal } from '../../UI/atoms/Modal';
import PropTypes from 'prop-types';
import Button2 from '../../UI/atoms/Button';
import { css } from '@emotion/react';
import InputForm from '../atoms/Input/InputForm';
import { getParseData } from '../../../lib/util/Util';
import { Popconfirm, Select, Spin, Button, Tabs, Collapse } from 'antd';
import { DeleteOutlined, LoadingOutlined } from '@ant-design/icons';
import { Option } from 'antd/es/mentions';
import DAYJS from 'dayjs';
import {
  MSG_FUNCTION,
  MSG_HISTORY,
  MSG_LOCAL,
  MSG_REMOTE,
  MSG_SQL,
} from '../../../lib/api/Define/Message';
import { E_MULTI_TYPE } from '../../../lib/api/Define/etc';
import { useQuery } from 'react-query';
import { QUERY_KEY } from '../../../lib/api/Define/QueryKey';
import { getResource_HistorySetting } from '../../../lib/api/axios/useJobSettingRequest';
import NotificationBox from '../molecules/NotificationBox/Notification';

const footerStyle = css`
  display: flex;
  justify-content: flex-end;
  align-items: center;
`;
const directoryStyle = css`
  & .ant-upload-list {
    max-height: 150px;
    overflow-y: auto;
  }
`;
const historyStyle = css`
  max-height: 750px;
  overflow: auto;
  & .ant-spin-spinning {
    display: flex;
    height: 300px;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    row-gap: 0.5rem;
    margin-top: 1rem;
  }
  & .ant-collapse {
    margin-top: 1rem;
  }
`;
const ModalFooter = ({ startFunc, closeFunc, checkFunc }) => {
  return (
    <div css={footerStyle}>
      <Button2
        theme={'white'}
        onClick={() => startFunc({ type: 'event' })}
        style={{ marginLeft: '8px', fontWeight: 400 }}
        disabled={checkFunc() === false}
      >
        {'Start Analysis'}
      </Button2>
      <Button2
        theme={'blue'}
        onClick={() => closeFunc({ next: undefined })}
        style={{ marginLeft: '8px', fontWeight: 400 }}
      >
        {'Cancel'}
      </Button2>
    </div>
  );
};

ModalFooter.propTypes = {
  startFunc: PropTypes.func.isRequired,
  closeFunc: PropTypes.func.isRequired,
  checkFunc: PropTypes.func,
};

const start_analysis_style = css`
  & .ant-form-item-label {
    text-align: left;
  }
  & .ant-form-item {
    margin-bottom: 10px;
  }
  & .ant-upload.ant-upload-drag {
    width: 324px;
  }
`;
const Contents = ({ options, target, defaultV, actionFunc }) => {
  const [deleteLoading, setDeleteLoading] = useState(false);
  const onClickEvent = (value, type) => {
    actionFunc({ [type]: value });
    if (type === 'DELETE_HISTORY') {
      setDeleteLoading(true);
    }
  };
  useEffect(() => {
    if (deleteLoading) setDeleteLoading(false);
  }, [options]);
  if (options.length === 0) return <></>;
  return (
    <>
      <Spin
        tip="Deleting..."
        indicator={<LoadingOutlined style={{ fontSize: 24 }} spin />}
        spinning={deleteLoading}
      >
        <Select
          value={defaultV ?? '0'}
          onChange={(e) => onClickEvent(e, target)}
        >
          {options.map((item, idx) => {
            return (
              <Option key={idx} value={item}>
                {
                  <>
                    {''}
                    {item}
                    {item === MSG_REMOTE ||
                    item === MSG_LOCAL ||
                    item === MSG_SQL ? (
                      <></>
                    ) : (
                      <Popconfirm
                        title={`Are you sure to delete [${item}]?`}
                        onConfirm={(e) => {
                          e.stopPropagation();
                          onClickEvent(item, 'DELETE_HISTORY');
                        }}
                      >
                        <Button
                          type="text"
                          icon={<DeleteOutlined />}
                          style={{ float: 'right' }}
                          onClick={(e) => e.stopPropagation()}
                        />
                      </Popconfirm>
                    )}
                  </>
                }
              </Option>
            );
          })}
        </Select>
      </Spin>
    </>
  );
};
Contents.propTypes = {
  options: PropTypes.array,
  defaultV: PropTypes.string,
  actionFunc: PropTypes.func,
  target: PropTypes.string,
};
export const JobSettingInputForm = ({ item, changefunc, info }) => {
  const { title, type, mode, options } = item;
  const period = { start: '', end: '' };
  const selected = { start: '', end: '' };
  if (type.toLowerCase() === 'datepicker') {
    selected.start =
      info.job_type === MSG_HISTORY
        ? item?.selected?.start ?? options?.[0].start ?? 0
        : info?.selected?.start ??
          item?.selected?.start ??
          options?.[0].start ??
          0;
    selected.end =
      info.job_type === MSG_HISTORY
        ? item?.selected?.end ?? options?.[0].end ?? 0
        : info?.selected?.end ?? item?.selected?.end ?? options?.[0].end ?? 0;
    period.start =
      info.job_type === MSG_HISTORY
        ? item?.selected?.start ?? options?.[0].start ?? 0
        : info?.period?.start ?? item?.period?.start ?? options?.[0].start ?? 0;
    period.end =
      info.job_type === MSG_HISTORY
        ? item?.selected?.end ?? options?.[0].end ?? 0
        : info?.period?.end ?? item?.period?.end ?? options?.[0].end ?? 0;
  }
  const changeEvent = (e) => {
    const update = changefunc(e);
    if (update !== undefined) {
      console.log(update);
    }
  };

  return (
    <div css={start_analysis_style}>
      {type === 'select' ? (
        mode === 'singular' ? (
          item.target === 'source' ? (
            <InputForm.select
              formLabel={title}
              formName={item.target}
              options={item.options}
              optionNode={
                <Contents
                  options={item.options}
                  defaultV={info?.[item.target] ?? ''}
                  actionFunc={changeEvent}
                  target={item.target}
                />
              }
              changeFunc={changeEvent}
              defaultV={info?.[item.target] ?? ''}
            />
          ) : (
            <InputForm.select
              formLabel={title}
              formName={item.target}
              options={item.options}
              changeFunc={changeEvent}
              defaultV={info?.[item.target] ?? ''}
            />
          )
        ) : mode === 'subItem' ? (
          <>
            <InputForm.subItem
              formLabel={title}
              formName={item.target}
              options={info?.info?.[item.target] ?? item.options}
              subItem={{
                ...item.subItem,
                options:
                  info?.info?.[item.subItem.target] ?? item.subItem.options,
                selected:
                  info?.[item.subItem.target] ?? item?.subItem.selected ?? '',
              }}
              defaultV={info?.[item.target] ?? item?.selected ?? ''}
              changeFunc={changeEvent}
            />
          </>
        ) : (
          <></>
        )
      ) : type.toLowerCase() === 'datepicker' ? (
        <InputForm.datePicker
          formLabel={title}
          formName={item.target}
          start={
            selected.start === ''
              ? selected.start
              : DAYJS(selected.start).format('YYYY-MM-DD')
          }
          end={
            selected.end === ''
              ? selected.end
              : DAYJS(selected.end).format('YYYY-MM-DD')
          }
          period={{
            start:
              period.start === ''
                ? period.start
                : DAYJS(period.start).format('YYYY-MM-DD'),
            end:
              period.end === ''
                ? period.end
                : DAYJS(period.end).format('YYYY-MM-DD'),
          }}
          changeFunc={changeEvent}
          disabled={item?.enable === false ?? false}
        />
      ) : type === 'directory' ? (
        <InputForm.directory
          formLabel={title}
          formName={item.target}
          changeFunc={changeEvent}
        />
      ) : type === 'files' ? (
        <InputForm.files
          formLabel={title}
          formName={item.target}
          changeFunc={changefunc}
          files={
            info?.file_name !== undefined
              ? info?.file_name?.getAll('files').map((o) => o) ?? undefined
              : item?.file_name?.length > 0 ?? false
              ? item.file_name.map((obj, i) => {
                  return {
                    uid: i + 1,
                    name: obj,
                    status: 'done',
                  };
                })
              : undefined
          }
          defaultFiles={
            item?.file_name?.length > 0 ?? false
              ? item.file_name.map((obj, i) => {
                  return {
                    uid: i + 1,
                    name: obj,
                    status: 'done',
                  };
                })
              : undefined
          }
          enable={item.enable}
        />
      ) : type === 'file' ? (
        <InputForm.file
          formLabel={title}
          formName={item.target}
          changeFunc={changefunc}
        />
      ) : type === 'text' ? (
        <InputForm.text
          formLabel={title}
          formName={item.target}
          changeFunc={changefunc}
          value={item?.content ?? info?.[item.target]}
        />
      ) : type === 'textarea' ? (
        <InputForm.textarea
          formName={item.target}
          changeFunc={changeEvent}
          value={info?.[item.target] ?? item?.content ?? ''}
          disabled={(item?.enable ?? true) === false}
        />
      ) : (
        <div>{title}</div>
      )}
    </div>
  );
};

JobSettingInputForm.propTypes = {
  item: PropTypes.object.isRequired,
  changefunc: PropTypes.func.isRequired,
  info: PropTypes.object,
};

const title_style = css`
  font-weight: 400;
`;
const ModalContents = ({ form, changeFunc, info }) => {
  const [source, setSource] = useState(info?.source ?? undefined);

  useEffect(() => {
    if (source !== info?.source) {
      setSource(info?.source);
    }
  }, [info?.source]);

  if (form === null || info === null) return <></>;

  return (
    form?.[source]?.map((item, idx) => (
      <div key={idx}>
        <FormCard title={item.title} titleStyle={title_style}>
          {item.items.map((idx2, i) => (
            <JobSettingInputForm
              key={i}
              item={item.items[i]}
              changefunc={changeFunc}
              info={info}
            />
          ))}
        </FormCard>
      </div>
    )) ?? <></>
  );
};

ModalContents.propTypes = {
  form: PropTypes.object.isRequired,
  changeFunc: PropTypes.func,
  info: PropTypes.object,
};

const { TabPane } = Tabs;
const { Panel } = Collapse;

const MultiJobModalContents = ({
  info,
  changeFunc,
  resource,
  select,
  history,
}) => {
  const [source, setSource] = useState(select ?? undefined);
  const [jobList, setjobList] = useState({ function: [], history: [] });
  const { info: multiHistory, setfunc: setMultiHistory } = history;
  const HistoryInfo = multiHistory.resource.find(
    (o) => o.id === multiHistory.id,
  )?.info;

  useQuery(
    [QUERY_KEY.JOBSETTING_INIT, multiHistory?.id],
    () => getResource_HistorySetting({ history_id: multiHistory.id }),
    {
      enabled: !!multiHistory?.id && HistoryInfo === undefined,
      onError: (error) => {
        NotificationBox('ERROR', error.message, 4.5);
      },
      onSuccess: ({ id, info }) => {
        console.log('id', id);
        console.log('info', info);
        const isExist = multiHistory.resource
          .filter((o) => !!o?.info)
          .map((o) => o.id)
          .includes(multiHistory.id);
        console.log('isExist', isExist);
        if (isExist === false) {
          setMultiHistory((prevState) => ({
            ...prevState,
            resource: [...prevState.resource, { id: prevState.id, info: info }],
          }));
        }
      },
    },
  );

  const TabChange = (event) => {
    const item = getParseData(event);
    if (item.id === 'source' && source !== item.value) {
      setSource(item.value);
    }
    changeFunc({ MULTI_TAB: item.value });
  };
  const ListChange = ({ target, type }) => {
    if (type === MSG_FUNCTION) {
      changeFunc({ source: target });
      if (target !== source) {
        setSource(target);
      }
    } else if (type === MSG_HISTORY) {
      setMultiHistory((prevState) => ({ ...prevState, id: target }));
      changeFunc({ HISTORY: target });
    }
  };
  useEffect(() => {
    const funcList = resource.formList.filter(
      (o) => (o?.source_type ?? o?.type) !== 'history',
    );
    setjobList({
      function: funcList,
      history: resource.formList.filter(
        (o) => (o?.source_type ?? o?.type) === 'history',
      ),
    });
    const target = funcList?.[0]?.key ?? undefined;
    setSource(target);
    changeFunc({ source: target });
  }, [resource]);
  return (
    <>
      <Tabs
        defaultActiveKey="function"
        size={'small'}
        type={'card'}
        onChange={(key) => TabChange({ tab: key })}
      >
        <>
          <TabPane tab="Function" key="function">
            <div>
              <Select
                onChange={(e) => ListChange({ target: e, type: 'function' })}
                style={{ minWidth: '100%' }}
                value={source ?? ''}
              >
                {jobList.function.map((item, idx) => {
                  return (
                    <Option key={idx} value={item?.key ?? item}>
                      {item?.key ?? item}
                    </Option>
                  );
                })}
              </Select>
            </div>
            <ModalContents
              form={resource?.form}
              changeFunc={changeFunc}
              info={info?.find((o) => o.source === source) ?? null}
            />
          </TabPane>
          <TabPane tab="History" key="history">
            <div>
              <Select
                onChange={(e) => ListChange({ target: e, type: MSG_HISTORY })}
                style={{ minWidth: '100%' }}
                value={multiHistory?.id ?? ''}
              >
                {jobList.history.map((item, idx) => {
                  return (
                    <Option key={idx} value={item?.history_id ?? item}>
                      {item?.title ?? item}
                    </Option>
                  );
                })}
              </Select>
            </div>
            <div css={historyStyle}>
              {HistoryInfo !== undefined ? (
                <Collapse>
                  {Object.keys(HistoryInfo.form).map((historyForm, index) => {
                    return (
                      <>
                        <Panel header={historyForm} key={`history_${index}`}>
                          <ModalContents
                            form={HistoryInfo.form}
                            info={{ source: historyForm }}
                          />
                        </Panel>
                      </>
                    );
                  })}
                </Collapse>
              ) : multiHistory?.id ?? false ? (
                <Spin tip=" Data Loading..." spinning={true} />
              ) : (
                <></>
              )}
            </div>
          </TabPane>
        </>
      </Tabs>
    </>
  );
};

MultiJobModalContents.propTypes = {
  info: PropTypes.array,
  changeFunc: PropTypes.func.isRequired,
  resource: PropTypes.object,
  select: PropTypes.string,
  history: PropTypes.object,
};

const JobSettingModal = ({
  isOpen,
  info,
  closeFunc,
  startFunc,
  changeFunc,
  resource,
  enableCheckFunc,
  history,
}) => {
  if (resource === null || info === undefined) return <></>;
  console.log('info', info);
  return (
    <>
      <Modal
        width={'550px'}
        isOpen={isOpen}
        header={resource?.title ?? info?.title ?? 'loading.....'}
        content={
          <>
            {info.source_type === E_MULTI_TYPE ? (
              <MultiJobModalContents
                form={resource?.form ?? null}
                changeFunc={changeFunc}
                resource={resource}
                select={info?.source ?? undefined}
                info={info?.list ?? []}
                history={history}
              />
            ) : (
              <ModalContents
                form={resource?.form ?? null}
                changeFunc={changeFunc}
                info={info}
              />
            )}
          </>
        }
        footer={
          <ModalFooter
            startFunc={startFunc}
            closeFunc={closeFunc}
            checkFunc={enableCheckFunc}
          />
        }
        closeIcon={false}
        style={directoryStyle}
      />
    </>
  );
};

JobSettingModal.propTypes = {
  isOpen: PropTypes.bool,
  startFunc: PropTypes.func,
  closeFunc: PropTypes.func,
  changeFunc: PropTypes.func,
  info: PropTypes.object,
  enableCheckFunc: PropTypes.func,
  history: PropTypes.object,
  resource: PropTypes.shape({
    title: PropTypes.string,
    formList: PropTypes.array,
    form: PropTypes.object,
  }),
};
export default JobSettingModal;
