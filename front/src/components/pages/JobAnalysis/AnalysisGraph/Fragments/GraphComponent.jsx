import React from 'react';
import PropTypes from 'prop-types';
import { graphWrapper } from '../styleGroup';
import { Button, Popconfirm } from 'antd';
import { CloseCircleFilled, SettingFilled } from '@ant-design/icons';

const GraphComponent = React.memo(({ index, editFunc, deleteFunc, type }) => {
  return (
    <div css={graphWrapper}>
      <div>
        <Button
          type="dashed"
          shape="round"
          icon={<SettingFilled />}
          onClick={() => editFunc(index, 'edit')}
        >
          Edit
        </Button>
        <Popconfirm
          title="Are you sure you want to delete this graph?"
          onConfirm={() => deleteFunc(index)}
        >
          <Button type="dashed" shape="round" icon={<CloseCircleFilled />}>
            Delete
          </Button>
        </Popconfirm>
      </div>
      <div id={`${type}_graph_${index}`} />
    </div>
  );
});

GraphComponent.propTypes = {
  index: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  editFunc: PropTypes.func,
  deleteFunc: PropTypes.func,
  type: PropTypes.string,
};
GraphComponent.displayName = 'GraphComponent';

export default GraphComponent;
