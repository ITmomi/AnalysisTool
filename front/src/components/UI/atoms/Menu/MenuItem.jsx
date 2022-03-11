import React from 'react';
import PropTypes from 'prop-types';
import { Menu } from 'antd';
import css from '@emotion/css';

const itemStyle = css`
  width: px;
  height: 64px;
`;

const MenuItem = ({ key, item }) => {
  return (
    <div css={itemStyle}>
      <Menu.Item key={key}>{item}</Menu.Item>
    </div>
  );
};

MenuItem.propTypes = {
  key: PropTypes.string,
  item: PropTypes.string,
};

export default MenuItem;
