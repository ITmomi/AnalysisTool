import React from 'react';
import { notification } from 'antd';
import PropTypes from 'prop-types';
import { WarningOutlined } from '@ant-design/icons';

const NotificationBox = (title, message, time) => {
  notification.open({
    message: title,
    description: message,
    duration: time,
    icon: (
      <React.Fragment>
        <WarningOutlined style={{ color: '#108ee9' }} />
      </React.Fragment>
    ),
  });
};

NotificationBox.propTypes = {
  type: PropTypes.string,
  title: PropTypes.oneOfType([PropTypes.node, PropTypes.string]),
  message: PropTypes.oneOfType([PropTypes.node, PropTypes.string]),
  time: PropTypes.number,
};

NotificationBox.defaultProps = {
  type: 'info',
  title: 'title',
  message: 'message',
  time: 4.5,
};

export default NotificationBox;
