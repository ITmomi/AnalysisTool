import React from 'react';
import { Button, Popconfirm } from 'antd';
import PropTypes from 'prop-types';
import { DeleteOutlined } from '@ant-design/icons';
import { MSG_CONFIRM_DELETE } from '../../../../lib/api/Define/Message';

const DeleteButton = ({ deleteHandler, title, icon, disabled }) => {
  return (
    <>
      <Popconfirm
        title={title}
        onConfirm={deleteHandler}
        disabled={disabled ?? false}
      >
        <Button type="dashed" icon={icon} disabled={disabled ?? false} />
      </Popconfirm>
    </>
  );
};

DeleteButton.propTypes = {
  type: PropTypes.string,
  title: PropTypes.string,
  deleteHandler: PropTypes.func,
  icon: PropTypes.node,
  disabled: PropTypes.bool,
};

DeleteButton.defaultProps = {
  title: MSG_CONFIRM_DELETE,
  icon: <DeleteOutlined />,
  disabled: false,
};

export default DeleteButton;
