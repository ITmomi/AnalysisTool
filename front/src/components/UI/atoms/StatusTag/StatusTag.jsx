import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import { Tag } from 'antd';
import React from 'react';
import PropTypes from 'prop-types';

const E_SUCCESS = 'success';
const E_PROCESS = 'processing';
const E_DEFAULT = 'default';
const E_ERROR = 'error';

const StatusTag = ({ status, icon, color }) => {
  icon =
    icon ?? status.toLowerCase() === E_SUCCESS ? (
      <CheckCircleOutlined />
    ) : status.toLowerCase() === E_PROCESS ? (
      <SyncOutlined spin={true} />
    ) : status.toLowerCase() === E_ERROR ? (
      <CloseCircleOutlined />
    ) : (
      <></>
    );

  return (
    <>
      <Tag
        icon={icon}
        color={color ?? (status === '' ? E_DEFAULT : status.toLowerCase())}
      >
        {status}
      </Tag>
    </>
  );
};
StatusTag.propTypes = {
  icon: PropTypes.node,
  status: PropTypes.string,
  color: PropTypes.string,
};

export default StatusTag;
