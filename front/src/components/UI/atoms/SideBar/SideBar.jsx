import React from 'react';
import PropTypes from 'prop-types';
import { css } from '@emotion/react';
import { Layout } from 'antd';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faChevronRight,
  faChevronLeft,
} from '@fortawesome/free-solid-svg-icons';

const { Sider } = Layout;

const SideBar = React.memo(
  ({
    collapsible,
    collapsed,
    sideBarStyle,
    triggerStyle,
    triggerFunc,
    children,
  }) => {
    return (
      <div css={wrapperStyle}>
        <Sider
          trigger={null}
          collapsible={collapsible}
          collapsed={collapsed}
          style={sideBarStyle}
          theme="light"
        >
          {children}
          {collapsible ? (
            <div
              className="sidebar-trigger"
              css={[defaultTriggerStyle, triggerStyle]}
              onClick={triggerFunc}
              onKeyDown={triggerFunc}
              role="button"
              tabIndex={0}
            >
              {collapsed ? (
                <FontAwesomeIcon icon={faChevronRight} />
              ) : (
                <FontAwesomeIcon icon={faChevronLeft} />
              )}
            </div>
          ) : (
            ''
          )}
        </Sider>
      </div>
    );
  },
);

SideBar.displayName = 'SideBar';
SideBar.propTypes = {
  collapsible: PropTypes.bool,
  collapsed: PropTypes.bool,
  sideBarStyle: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  triggerStyle: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  triggerFunc: PropTypes.func,
  children: PropTypes.node.isRequired,
};
SideBar.defaultProps = {
  collapsible: false,
  collapsed: false,
};

const wrapperStyle = css`
  position: relative;
  background: white;
  min-height: 56vh;
  &:hover .sidebar-trigger {
    display: block;
  }
`;

const defaultTriggerStyle = css`
  position: absolute;
  display: none;
  top: 50%;
  right: -15px;
  width: 15px;
  height: 60px;
  text-align: center;
  line-height: 4.3;
  border-radius: 0 4px 4px 0;
  background: sandybrown;
  cursor: pointer;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
`;

export default SideBar;
