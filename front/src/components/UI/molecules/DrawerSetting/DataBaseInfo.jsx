import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import {
  Badge,
  Descriptions,
  Modal,
  Popconfirm,
  Spin,
  Table,
  Button as Button2,
} from 'antd';
import DescriptionsItem from 'antd/lib/descriptions/Item';
import InputForm from '../../atoms/Input/InputForm';
import Button from '../../atoms/Button';
import {
  MSG_ADD_DATABASE,
  MSG_APPLY,
  MSG_CANCEL,
  MSG_SAVE,
  MSG_CONFIRM_DELETE,
  MSG_DBCONNECTION_TEST,
  MSG_RESET,
} from '../../../../lib/api/Define/Message';
import { getParseData } from '../../../../lib/util/Util';
import { useMutation, useQueries, useQuery, useQueryClient } from 'react-query';

import {
  DeleteOutlined,
  EditOutlined,
  LoadingOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { QUERY_KEY } from '../../../../lib/api/Define/QueryKey';
import { css } from '@emotion/react';
import {
  addDBInfo,
  dbConnectionCheck,
  deleteDBInfo,
  getDBStatus,
  getRemoteDBInfo,
  updateDBInfo,
} from '../../../../lib/api/axios/useMgmtRequest';
import useMgmtInfo, { dbSettingItems } from '../../../../hooks/useMgmtInfo';
import { NotificationBox } from '../NotificationBox';
import StatusTag from '../../atoms/StatusTag/StatusTag';

const { Column } = Table;
const footerStyle = css`
  display: flex;
  justify-content: flex-end;
  align-items: center;
`;
const EXIST_PASSWORD = '*******';
const VIEW_MODE = 'list';
const ADD_MODE = 'add';
const MODIFY_MODE = 'modify';

const ModalFooter = ({ close, apply }) => {
  useEffect(() => {
    return close;
  }, []);
  return (
    <div css={footerStyle}>
      <Button
        theme={'white'}
        onClick={close}
        style={{ marginLeft: '8px', fontWeight: 400 }}
      >
        {MSG_CANCEL}
      </Button>
      <Button onClick={apply} style={{ marginLeft: '8px', fontWeight: 400 }}>
        {MSG_SAVE}
      </Button>
    </div>
  );
};
ModalFooter.propTypes = {
  apply: PropTypes.func,
  close: PropTypes.func,
};
const ModalForm = ({ title, applyFunc, closeModal, mode, data, visible }) => {
  const [applyPress, setApplyPress] = useState(false);
  useEffect(() => {
    if (applyPress && mode === VIEW_MODE) {
      setApplyPress(false);
    }
  }, [mode]);
  const FormApply = (obj) => {
    obj === null ? setApplyPress(false) : applyFunc(obj);
  };
  return (
    <Modal
      width={600}
      style={{ top: 20 }}
      maskClosable={false}
      destroyOnClose
      visible={visible}
      title={<div css={{ fontWeight: 700, color: '#0e72cf' }}>{title}</div>}
      onCancel={closeModal}
      footer={
        <ModalFooter apply={() => setApplyPress(true)} close={closeModal} />
      }
    >
      <AddEditForm
        data={data}
        applyFunc={FormApply}
        isApply={applyPress}
        visible={visible}
      />
    </Modal>
  );
};
ModalForm.propTypes = {
  mode: PropTypes.string,
  data: PropTypes.array,
  title: PropTypes.string,
  applyFunc: PropTypes.func,
  closeModal: PropTypes.func,
  visible: PropTypes.bool,
};

const ListForm = ({ title, url, db_type }) => {
  const { ManagementInfo, DbList, setDbList } = useMgmtInfo();
  const [mode, setMode] = useState(VIEW_MODE);
  const [refreshFlag, setRefreshFlag] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectId, setSelectId] = useState(undefined);
  const [modifyObj, setModifyObj] = useState(undefined);
  const [tableData, setTableData] = useState([]);
  const queryClient = useQueryClient();

  useQuery(
    [QUERY_KEY.MGMT_REMOTE_DB_DETAIL],
    () => getRemoteDBInfo({ db_id: selectId }),
    {
      enabled: Boolean(selectId) && mode === MODIFY_MODE,
      onSuccess: (info) => {
        setModifyObj(
          dbSettingItems.items.map((obj) => {
            return { ...obj, content: info[obj.target] };
          }),
        );
        setModalVisible(true);
      },
    },
  );

  const remoteStatus = useQueries(
    DbList.map((object) => {
      return {
        queryKey: [QUERY_KEY.MGMT_REMOTE_DB_STATUS, object.id],
        onError: (err) => {
          setTableData(
            tableData.map((obj) => {
              return obj.id === object.id ? { ...obj, sts: 'error' } : obj;
            }),
          );
          NotificationBox('ERROR', err.message, 0);
        },
        queryFn: () => getDBStatus({ url: url, db_id: object.id }),
        enabled: refreshFlag,
        onSuccess: ({ id, info }) => {
          setTableData(
            tableData.map((obj) => {
              return obj.id === id ? { ...obj, sts: info.sts } : obj;
            }),
          );
        },
      };
    }),
  );
  useEffect(() => {
    const isProcessing = remoteStatus.find((obj) => obj.isLoading === true);
    if (refreshFlag && isProcessing === undefined) setRefreshFlag(false);
  }, [remoteStatus]);

  const deleteMutation = useMutation(
    [QUERY_KEY.MGMT_DB_DELETE],
    (db_id) => deleteDBInfo({ url: url, db_id: db_id }),
    {
      onSuccess: () => {
        setSelectId(undefined);
        queryClient
          .invalidateQueries([QUERY_KEY.MGMT_REMOTE_DB])
          .then((_) => _);
      },
    },
  );
  const addMutation = useMutation([QUERY_KEY.MGMT_DB_ADD], addDBInfo, {
    onSuccess: () => {
      queryClient.invalidateQueries([QUERY_KEY.MGMT_REMOTE_DB]).then((_) => _);
    },
  });
  const updateMutation = useMutation([QUERY_KEY.MGMT_DB_UPDATE], updateDBInfo, {
    onSuccess: () => {
      queryClient.invalidateQueries([QUERY_KEY.MGMT_REMOTE_DB]).then((_) => _);
    },
  });

  const refreshHandler = () => {
    setTableData(
      tableData.map((obj) => {
        return { ...obj, sts: 'processing' };
      }),
    );
    setRefreshFlag(true);
  };
  const addHandler = (items) => {
    addMutation.mutate({ url: url, items: items });
  };
  const modifyHandler = (items, id) => {
    updateMutation.mutate({ url: `${url}/${id}`, items: items });
  };
  const editHandler = (id) => {
    setSelectId(id);
    setMode(MODIFY_MODE);
    queryClient
      .invalidateQueries([QUERY_KEY.MGMT_REMOTE_DB_DETAIL, id])
      .then((_) => _);
  };
  const deleteHandler = (id) => {
    setSelectId(id);
    deleteMutation.mutate(id);
  };

  const setModalVisibleClose = () => {
    setModalVisible(false);
    setSelectId(undefined);
    setMode(VIEW_MODE);
  };

  useEffect(() => {
    setTableData(
      DbList.map((obj, idx) => {
        return Object.assign({}, { key: idx, no: idx + 1 }, obj);
      }),
    );
  }, [DbList]);

  useEffect(() => {
    const itemList = ManagementInfo.find((obj) => obj.target === db_type).items;
    if (itemList.length !== DbList.length) {
      setDbList(ManagementInfo.find((obj) => obj.target === db_type).items);
    }
  }, [ManagementInfo]);

  const remotetablestyle = css`
    width: 100%;
    & .ant-spin-container {
      max-width:100%
    }
    & .ant-table-content {
      & table > thead > tr {
        & th {
          font-weight: bold;
          &:first-of-type {
            width: 45px;
          }
          &:nth-of-type(3){
            width: 0px;
          }
          &:last-of-type {
            width: 101px;
          }
          } 
        }
      & table > tbody > tr {
        & > td {
          &:first-of-type{
            text-align: center;
            }          
          }
        }
    }
    & table > tbody > tr {
      & > td {
        &:nth-of-type(3) {
          & > span {
            background-color: white;
            border-style: dashed;
            & > span:first-of-type {
              position: relative;
              top: 1px;
              & > svg {
                width: 13px;
                height: 13px;
              }
            }
            & > span + span {
              margin-left: 0.5rem;
            }
          }
        }
        &:last-of-type {
          text-align: center;
          & svg {
          margin-right: 0;
          position: relative;
          }
          & button + button {
            margin-left: 0rem;
          }
        }
    }    
  `;
  if (queryClient.getQueryData([QUERY_KEY.MGMT_REMOTE_DB]).isLoading)
    return <>Waiting...</>;
  return (
    <>
      <ModalForm
        title={`${
          mode === MODIFY_MODE ? 'MODIFY' : 'ADD'
        } ${db_type.toUpperCase()} DATABASE`}
        applyFunc={(items) =>
          mode === MODIFY_MODE
            ? modifyHandler(items, selectId)
            : addHandler(items)
        }
        data={mode === MODIFY_MODE ? modifyObj : undefined}
        mode={mode}
        visible={modalVisible}
        closeModal={setModalVisibleClose}
        db_type={db_type}
        db_id={selectId}
      />
      <Descriptions
        title={title}
        column={2}
        layout="vertical"
        extra={
          <div css={{ display: 'inline-flex' }}>
            <Button
              onClick={() => {
                setMode(ADD_MODE);
                setModalVisible(true);
              }}
              style={{ marginLeft: '8px', fontWeight: 400 }}
            >
              {MSG_ADD_DATABASE}
            </Button>
            <Button
              style={{
                marginLeft: '8px',
                fontWeight: 400,
                width: '32px',
                paddingRight: '0px',
              }}
              onClick={() => refreshHandler()}
              disabled={DbList.length === 0}
            >
              {<ReloadOutlined />}
            </Button>
          </div>
        }
      >
        <Spin
          tip="Loading..."
          spinning={deleteMutation.isLoading || addMutation.isLoading}
        >
          {deleteMutation.error || addMutation.error ? (
            <NotificationBox
              title={'DB UPDATE ERROR'}
              message={
                deleteMutation?.error?.message ?? addMutation.error.message
              }
            />
          ) : (
            <></>
          )}
          <Descriptions.Item>
            {DbList.length !== 0 ? (
              <div css={remotetablestyle}>
                <Table
                  bordered
                  pagination={false}
                  dataSource={tableData}
                  size="middle"
                  rowKey="key"
                >
                  <Column key="no" title="No." dataIndex="no" />
                  <Column key="name" title="DB@Host" dataIndex="name" />
                  <Column
                    key="sts"
                    title="status"
                    dataIndex="sts"
                    render={(_, record) => <StatusTag status={record.sts} />}
                  />
                  <Column
                    title={'Edit/Delete'}
                    dataIndex="delete"
                    key="delete"
                    render={(_, record) => (
                      <div>
                        <Button2
                          type="dashed"
                          icon={<EditOutlined />}
                          onClick={() => editHandler(record.id)}
                          style={{ marginRight: '4px' }}
                        />
                        <Popconfirm
                          title={MSG_CONFIRM_DELETE}
                          onConfirm={() => deleteHandler(record.id)}
                        >
                          <Button2 type="dashed" icon={<DeleteOutlined />} />
                        </Popconfirm>
                      </div>
                    )}
                  />
                </Table>
              </div>
            ) : (
              <></>
            )}
          </Descriptions.Item>
        </Spin>
      </Descriptions>
    </>
  );
};
ListForm.propTypes = {
  data: PropTypes.array,
  title: PropTypes.string,
  applyFunc: PropTypes.func,
  url: PropTypes.string,
  db_type: PropTypes.string,
};
const ViewForm = ({ data, title, extra }) => {
  return (
    <Descriptions
      title={title}
      bordered
      column={6}
      layout={'vertical'}
      extra={extra}
    >
      {data.map((obj, i) => {
        if (obj.type === 'text' || obj.type === 'password') {
          return (
            <DescriptionsItem
              label={obj.title}
              key={i}
              span={obj.target === 'host' || obj.target === 'port' ? 3 : 2}
            >
              {obj.type === 'text'
                ? obj.content
                : obj.content !== undefined && obj.content.length > 0
                ? EXIST_PASSWORD
                : ''}
            </DescriptionsItem>
          );
        }
      })}
    </Descriptions>
  );
};
ViewForm.propTypes = {
  data: PropTypes.array,
  title: PropTypes.string,
  extra: PropTypes.node,
};

const AddEditForm = ({ title, data, applyFunc, isApply, visible }) => {
  const [formData, setFormData] = useState(undefined);

  /*  DB connection test : useMutation */
  const {
    mutate: connectionCheckMutate,
    error,
    isLoading,
    data: ConnectionData,
    reset,
  } = useMutation([QUERY_KEY.DB_CONNECTION_CHECK], (data) =>
    dbConnectionCheck(data),
  );
  const updateForm = (e) => {
    const event = getParseData(e);
    setFormData(
      formData.map((obj) =>
        obj.target === event.id ? { ...obj, content: event.value } : obj,
      ),
    );
    reset();
  };
  const resetForm = () => {
    setFormData(
      formData.map((obj) => {
        return { ...obj, content: '' };
      }),
    );
    reset();
  };
  const applyForm = () => {
    if (ConnectionData === undefined) {
      connectionCheckMutate(formData, {
        onError: () => applyFunc(null),
        onSuccess: () => applyFunc(formData),
      });
    } else {
      applyFunc(formData);
    }
  };
  useEffect(() => {
    if (isApply === true) {
      applyForm();
    } else if (visible === false) {
      reset();
    }
  }, [isApply, visible]);

  const tempStyle = css`
    & .ant-descriptions-header {
      margin-bottom: -20px;
    }
    & .ant-form-item-label {
      text-align: left;
    }
    & tr {
      &:first-of-type {
        & > td {
          &:first-of-type {
            width: 300px;
            & .ant-form-item-control-input-content {
              flex: 0 0 260px;
              position: relative;
              left: 5px;
            }
            & .ant-col.ant-col-8.ant-form-item-label {
              flex: 0 0 85px;
            }
          }
          &:last-of-type {
            & .ant-form-item-label {
              position: relative;
              left: 26px;
            }
            & .ant-form-item-control-input-content {
              flex: 0 0 174px;
              position: relative;
              left: 0px;
            }
          }
        }
      }
      &:nth-of-type(2),
      &:nth-of-type(3),
      &:nth-of-type(4) {
        & .ant-col.ant-col-8.ant-form-item-label {
          flex: 0 0 89px;
        }
      }
      & .ant-col.ant-col-16.ant-form-item-control {
        max-width: 100%;
      }
      & .ant-descriptions-item-content {
        display: block;
      }
    }
    & .ant-descriptions {
      margin-top: 20px;
    }
    & .ant-descriptions-extra {
      position: relative;
      top: -74px;
    }
  `;
  const Management_Test_connection_Style = css`
    display: flex;
    align-items: center;
    & span {
      & span:first-of-type {
        position: absolute;
        top: 8px;
        left: -6px;
      }
    }
  `;

  useEffect(() => {
    setFormData(
      (data ?? dbSettingItems.items).map((obj) => {
        return { ...obj, content: obj.content };
      }),
    );
    return () => reset();
  }, []);
  if (formData === undefined) return <></>;
  return (
    <div css={tempStyle}>
      <Descriptions
        title={title}
        column={2}
        extra={
          isApply !== undefined ? (
            <></>
          ) : (
            <>
              <Button
                onClick={() => resetForm()}
                style={{ marginLeft: '8px', fontWeight: 400 }}
              >
                {MSG_RESET}
              </Button>
              <Button
                theme={'white'}
                onClick={() => applyForm()}
                style={{ marginLeft: '8px', fontWeight: 400 }}
              >
                {MSG_APPLY}
              </Button>
            </>
          )
        }
      >
        {formData.map((obj, i) => {
          return obj.type === 'password' ? (
            <DescriptionsItem span={2} key={i}>
              <InputForm.password
                formLabel={obj.title}
                formName={obj.target}
                changeFunc={(e) => updateForm(e)}
                value={formData[i].content}
              />
            </DescriptionsItem>
          ) : obj.type === 'input' || obj.type === 'text' ? (
            <DescriptionsItem
              span={obj.target === 'host' || obj.target === 'port' ? 1 : 2}
              key={i}
            >
              <InputForm.input
                formLabel={obj.title}
                formName={obj.target}
                changeFunc={(e) => updateForm(e)}
                value={formData[i].content}
              />
            </DescriptionsItem>
          ) : (
            <></>
          );
        })}
        <DescriptionsItem span={2} key={10}>
          <div css={Management_Test_connection_Style}>
            <Button
              onClick={() => connectionCheckMutate(formData)}
              style={{ marginLeft: '8px', fontWeight: 400, minWidth: '125px' }}
            >
              {MSG_DBCONNECTION_TEST}
            </Button>
            <div css={{ display: 'flex', fontWeight: 700, color: '#00a1ff' }}>
              {isLoading ? (
                <>
                  <Spin
                    indicator={
                      <LoadingOutlined
                        style={{ fontSize: 24, left: '10px' }}
                        spin
                      />
                    }
                  />
                </>
              ) : error != null ? (
                <div css={{ display: 'block' }}>
                  <Badge
                    status="error"
                    text={'ERROR'}
                    style={{ left: '16px' }}
                  />
                  <div css={{ fontsize: '12px', paddingLeft: '24px' }}>
                    {error?.message ?? 'undefined'}
                  </div>{' '}
                </div>
              ) : ConnectionData !== undefined ? (
                <div css={{ display: 'block' }}>
                  <Badge
                    status="success"
                    text={'SUCCESS'}
                    style={{ left: '16px' }}
                  />
                  <div css={{ fontsize: '12px', paddingLeft: '24px' }}>
                    {ConnectionData ?? 'undefined'}
                  </div>{' '}
                </div>
              ) : (
                <></>
              )}
            </div>
          </div>
        </DescriptionsItem>
      </Descriptions>
    </div>
  );
};
AddEditForm.propTypes = {
  title: PropTypes.string,
  data: PropTypes.array,
  applyFunc: PropTypes.func,
  isApply: PropTypes.bool,
  visible: PropTypes.bool,
};

const DataBaseInfo = ({ children }) => {
  return <>{children}</>;
};
DataBaseInfo.propTypes = {
  children: PropTypes.node,
};
DataBaseInfo.addEdit = AddEditForm;
DataBaseInfo.view = ViewForm;
DataBaseInfo.list = ListForm;

export default DataBaseInfo;
