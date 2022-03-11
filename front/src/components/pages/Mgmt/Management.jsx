import React, { useState } from 'react';
import { Drawer, Collapse } from 'antd';
import PropTypes from 'prop-types';
import useMgmtInfo from '../../../hooks/useMgmtInfo';
import { css } from '@emotion/react';
import { DBSetting, DBTable } from '../../UI/molecules/DrawerSetting';
import { useQuery } from 'react-query';
import {
  MSG_MGMT_LOCAL_TITLE,
  MSG_MGMT_MAIN_TITLE,
  MSG_MGMT_REMOTE_TITLE,
  MSG_MGMT_TABLE_TITLE,
} from '../../../lib/api/Define/Message';
import { QUERY_KEY } from '../../../lib/api/Define/QueryKey';
import {
  LOCAL_INFO,
  REMOTE_INFO,
  TABLE_INFO,
} from '../../../lib/api/Define/etc';
import {
  getDBTableInfo,
  getLocalDBInfo,
  getRemoteDBInfo,
} from '../../../lib/api/axios/useMgmtRequest';

const { Panel } = Collapse;

const MainTitleDiv = css`
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 16px 24px;
  color: #f0f0f0;
  background: #000000;
`;
const tempStyle1 = css`
  & > div {
    margin-top: 0px;
  }
  & .ant-drawer-header {
    padding: 0px;
    margin-bottom: 0px;
  }
  & .ant-drawer-body {
    padding: 0;
    & > div > div:last-of-type {
      & .ant-spin-spinning {
        position: relative;
        top: -15px;
        & .anticon > svg {
          width: 1em;
          height: 1em;
        }
      }
    }
    & .ant-collapse-header {
      color: rgb(24, 144, 255);
      text-decoration: underline;
      font-weight: bold;
      & svg {
        color: black;
      }
    }
    & .ant-descriptions-header {
      position: relative;
      float: right;
      margin-bottom: -10px;
    }
    & svg {
      width: 15px;
      height: 15px;
    }
    & button {
      font-weight: 600;
    }
    & table {
      &:first-of-type {
        & tr:first-of-type {
          & td:last-of-type {
            & label.ant-form-item-required {
              left: 0px;
            }
          }
        }
      }
    }
  }
`;
const mgmt = [LOCAL_INFO, REMOTE_INFO, TABLE_INFO];
const MgmtPage = ({ show, closeFunc }) => {
  const [openPanel, setOpenPanel] = useState([
    LOCAL_INFO,
    REMOTE_INFO,
    TABLE_INFO,
  ]);
  const { ManagementInfo, setMgmtInfo } = useMgmtInfo();

  const { error: localError, isLoading: localisLoading } = useQuery(
    [QUERY_KEY.MGMT_LOCAL_DB],
    getLocalDBInfo,
    {
      enabled: !!openPanel.includes(LOCAL_INFO),
      onError: () => {
        setMgmtInfo({
          target: LOCAL_INFO,
          title: MSG_MGMT_LOCAL_TITLE,
          items: [],
        });
      },
      onSuccess: (info) => {
        setMgmtInfo({
          target: LOCAL_INFO,
          title: MSG_MGMT_LOCAL_TITLE,
          items: info.items,
        });
      },
    },
  );
  const { error: remoteError, isLoading: remoteisLoading } = useQuery(
    [QUERY_KEY.MGMT_REMOTE_DB],
    getRemoteDBInfo,
    {
      enabled: !!openPanel.includes(REMOTE_INFO),
      onError: () => {
        setMgmtInfo({
          target: REMOTE_INFO,
          title: MSG_MGMT_REMOTE_TITLE,
          items: [],
        });
      },
      onSuccess: (info) => {
        setMgmtInfo({
          target: REMOTE_INFO,
          title: MSG_MGMT_REMOTE_TITLE,
          items: info.items,
        });
      },
    },
  );

  const { error: rulesError, isLoading: rulesIsLoading } = useQuery(
    [QUERY_KEY.MGMT_TABLE_DB],
    getDBTableInfo,
    {
      enabled: !!openPanel.includes(TABLE_INFO),
      onError: () => {
        setMgmtInfo({
          target: TABLE_INFO,
          title: MSG_MGMT_TABLE_TITLE,
          items: [],
        });
      },
      onSuccess: (info) => {
        setMgmtInfo({
          target: TABLE_INFO,
          title: MSG_MGMT_TABLE_TITLE,
          items: info,
        });
      },
    },
  );
  const CollapseContents = () => {
    return (
      <Collapse onChange={(e) => setOpenPanel(e)} defaultActiveKey={openPanel}>
        {mgmt.map((info) => {
          const obj = ManagementInfo.find((obj2) => obj2.target === info);
          return obj === undefined ? (
            <></>
          ) : (
            <Panel header={obj.title} key={obj.target}>
              {obj.target === TABLE_INFO ? (
                <DBTable info={obj} />
              ) : obj.target === LOCAL_INFO ? (
                <DBSetting info={obj} db_type={LOCAL_INFO} />
              ) : (
                <DBSetting info={obj} db_type={REMOTE_INFO} />
              )}
            </Panel>
          );
        })}
      </Collapse>
    );
  };
  if (show === false && (ManagementInfo ?? true)) return <></>;
  if (localisLoading || remoteisLoading || rulesIsLoading)
    return <div> Waiting... </div>;
  if (localError || remoteError || rulesError) {
    return (
      <span>
        Error:{' '}
        {localError?.message ??
          remoteError?.message ??
          rulesError?.message ??
          'undefined Error'}
      </span>
    );
  }
  return (
    <>
      <Drawer
        title={<div css={MainTitleDiv}>{MSG_MGMT_MAIN_TITLE}</div>}
        width={600}
        closable={false}
        onClose={closeFunc}
        visible={show}
        placement="right"
        css={tempStyle1}
      >
        <CollapseContents />
      </Drawer>
    </>
  );
};

MgmtPage.propTypes = {
  show: PropTypes.bool,
  closeFunc: PropTypes.func,
};

export default MgmtPage;
