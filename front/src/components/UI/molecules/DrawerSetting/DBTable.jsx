import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { Badge, Descriptions, Spin, Upload, Table, message } from 'antd';
import Button from '../../atoms/Button';
import { CloudUploadOutlined } from '@ant-design/icons/lib/icons';
import { LoadingOutlined } from '@ant-design/icons';
import { exportFile } from '../../../../lib/api/axios/requests';
import {
  MSG_APPLY,
  MSG_CANCEL,
  MSG_EXPORT,
  MSG_IMPORT,
  MSG_UPLOAD_EXCEL_ONLY,
} from '../../../../lib/api/Define/Message';
import { URL_EXPORT_DBTABLE } from '../../../../lib/api/Define/URL';
import { css } from '@emotion/react';
import { useQuery, useQueryClient } from 'react-query';
import { QUERY_KEY } from '../../../../lib/api/Define/QueryKey';
import { importDBInfo } from '../../../../lib/api/axios/useMgmtRequest';

const columns = [
  {
    title: 'No.',
    dataIndex: 'no',
    key: 'no',
  },
  {
    title: 'Table name',
    dataIndex: 'table_name',
    key: 'table_name',
    width: 350,
  },
];
const IMPORT_FUNC = 'import';
const EXPORT_FUNC = 'export';
const DEFAULT_FUNC = EXPORT_FUNC;
const EXCEL_TYPE =
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
const init_data = {
  file: undefined,
  status: undefined,
  message: undefined,
};
const DBTable = ({ info }) => {
  const [isMode, setMode] = useState(DEFAULT_FUNC);
  const [uploadFile, setUploadFile] = useState(init_data);
  const [isLoading, setLoading] = useState(false);
  const [TableData, setTableData] = useState(null);
  const queryClient = useQueryClient();
  useEffect(() => {
    console.log('DBTable update', info);
    if (info)
      setTableData(
        info.items.map((obj, idx) => {
          return { key: idx, no: idx + 1, table_name: obj };
        }),
      );
    return () => {
      console.log('DBTable unmount');
      setLoading(false);
    };
  }, []);

  const setImportfile = (file) => {
    setUploadFile((prevState) => ({
      ...prevState,
      file: file,
    }));
  };

  const importStatus = useQuery(
    [QUERY_KEY.MGMT_RULES_IMPORT, uploadFile.file],
    () => importDBInfo(uploadFile.file),
    {
      enabled: !!isLoading && (!!uploadFile?.file ?? false),
      onSuccess: () => {
        queryClient.invalidateQueries([QUERY_KEY.MGMT_TABLE_DB]).then((_) => _);
        setUploadFile(init_data);
        setLoading(false);
        setMode(DEFAULT_FUNC);
      },
    },
  );

  const eventClick = (mode) => {
    setMode(mode);
    if (mode === EXPORT_FUNC)
      exportFile(URL_EXPORT_DBTABLE, 'file.xlsx').then((_) => _);
  };
  const exceptType = (type) => {
    console.log('exceptType: ', type);
    return Boolean(type === EXCEL_TYPE);
  };
  const ZipUploadProps = {
    name: 'files',
    beforeUpload: (file) => {
      if (exceptType(file.type) === false) {
        message.error(`${file.name} is not a excel file`);
        return Upload.LIST_IGNORE;
      } else {
        const formData = new FormData();
        formData.append('files', file);
        setImportfile(formData);
        return false;
      }
    },
    onRemove: (file) => {
      console.log('onRemove', file);
      setImportfile(undefined);
    },
  };
  const onClickCancel = () => {
    setUploadFile(init_data);
    setMode(DEFAULT_FUNC);
  };
  if (info == null) return <>{'DB Table empty'}</>;

  const TablelistStyle = css`
    height: 0px;
    position: relative;
    top: -54px;
    text-align: right;
    left: 1px;
    & button {
      position: relative;
      background: white;
      &:first-of-type {
        background: rgb(24, 144, 255);
      }
      &:last-of-type {
        color: black;
        top: -1px;
      }
    }
  `;

  const SettingstablelistStyle = css`
    position: relative;
    top: -17px;
    width: 100%;
    & table > thead > tr {
      & th {
        font-weight: bold;
      }
    }
    & table > thead > tr {
      & th {
        width: 32px;
      }
    }
    & table > tbody > tr {
      & td {
        &:first-of-type {
          text-align: center;
        }
      }
    }
  `;

  const TablelistimportbuttonStyle = css`
    height: 0px;
    position: relative;
    float: right;
    top: -54px;
    & button {
      &:first-of-type {
        position: relative;
        color: withe;
        background: rgb(24, 144, 255);
      }
      &:last-of-type {
        position: relative;
        background: white;
        color: black;
      }
    }
    & table > tbody {
      & > tr {
        &:last-of-type {
          & > td {
            & .anticon > svg {
              width: 0px;
              height: 0px;
            }
          }
        }
      }
    }
  `;

  const TablelistimportStyle = css`
    & button {
      position: relative;
      top: -17px;
    }
    & .ant-upload-list-item-info {
      position: relative;
      max-width: 230px;
      top: -15px;
      left: 14px;
    }
    & .ant-upload-text-icon {
      display: contents;
      & span {
        margin-left: 5px;
      }
    }
    & .ant-upload-list-item-card-actions {
      & button {
        position: relative;
        top: 0px;
        & svg {
          margin-right: 0px;
        }
      }
    }
  `;

  console.log('uploadFile', uploadFile);
  return (
    <>
      {isMode === DEFAULT_FUNC ? (
        <>
          <div css={TablelistStyle}>
            <Button
              onClick={() => setMode(IMPORT_FUNC)}
              style={{ marginLeft: '8px', fontWeight: 400 }}
            >
              {MSG_IMPORT}
            </Button>
            <Button
              theme={'white'}
              onClick={() => eventClick(EXPORT_FUNC)}
              style={{ marginLeft: '8px', fontWeight: 400 }}
            >
              {MSG_EXPORT}
            </Button>
          </div>
          <Descriptions
            // title={info.title}
            column={2}
            layout="vertical"
          >
            <Descriptions.Item>
              <div css={SettingstablelistStyle}>
                <Table
                  bordered
                  pagination={false}
                  columns={columns}
                  dataSource={TableData}
                  size="middle"
                  rowKey="key"
                />
              </div>
            </Descriptions.Item>
          </Descriptions>
        </>
      ) : (
        <>
          <div css={TablelistimportbuttonStyle}>
            <Button
              onClick={() => onClickCancel()}
              style={{ marginLeft: '8px', fontWeight: 400 }}
            >
              {MSG_CANCEL}
            </Button>
            <Button
              theme={'white'}
              disabled={uploadFile.file === undefined}
              onClick={() => setLoading(true)}
              style={{ marginLeft: '8px', fontWeight: 400 }}
            >
              {MSG_APPLY}
            </Button>
          </div>
          <Descriptions
            // title={info.title}
            layout="vertical"
          >
            <Descriptions.Item>
              <div css={TablelistimportStyle}>
                <Upload {...ZipUploadProps} maxCount={1}>
                  <div css={{ display: 'flex', alignItems: 'center' }}>
                    <Button
                      style={{
                        marginLeft: '8px',
                        marginRight: '10px',
                        fontWeight: 400,
                      }}
                      theme="white"
                    >
                      <CloudUploadOutlined />
                      {MSG_UPLOAD_EXCEL_ONLY}
                    </Button>
                    {importStatus.isError === true ? (
                      <div
                        css={{
                          display: 'flex',
                          fontWeight: 700,
                          color: '#00a1ff',
                          position: 'relative',
                          top: '50px',
                          left: '38px',
                        }}
                      >
                        <Badge
                          status="error"
                          text={'Error'}
                          style={{ left: '10px' }}
                        />
                        <div css={{ fontsize: '12px', paddingLeft: '24px' }}>
                          {importStatus?.error?.message ?? 'undefined'}
                        </div>
                      </div>
                    ) : (
                      <></>
                    )}
                  </div>
                </Upload>
              </div>
              {!!uploadFile.file ?? false ? (
                <>
                  {importStatus.isLoading ? (
                    <Spin
                      style={{ left: '10px' }}
                      indicator={
                        <LoadingOutlined style={{ fontSize: 24 }} spin />
                      }
                    />
                  ) : (
                    <></>
                  )}
                </>
              ) : (
                <></>
              )}
            </Descriptions.Item>
          </Descriptions>
        </>
      )}
    </>
  );
};

DBTable.propTypes = {
  info: PropTypes.object,
};

export default DBTable;
