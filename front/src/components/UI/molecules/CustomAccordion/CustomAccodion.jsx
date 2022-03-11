import React, { useState } from 'react';
import { DownOutlined } from '@ant-design/icons';
import PropTypes from 'prop-types';
import { css } from '@emotion/react';

const accordionStyle = css`
  position: relative;
  width: 100%;
  & > div {
    width: 100%;
    &:first-of-type {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem;
      background-color: #f5f5f5;
      cursor: pointer;
      & > .title {
        font-size: 18px;
      }
      & svg {
        transition: all 0.5s;
      }
    }
    &:last-of-type {
      max-height: 800px;
      transition: all 0.7s;
      overflow: hidden;
      & > .contents {
        padding: 1rem;
      }
    }
  }
  &.collapsed {
    & > div {
      &:first-of-type {
        & svg {
          transform: rotate(180deg);
        }
      }
      &:last-of-type {
        max-height: 0;
      }
    }
  }
`;

const CustomAccordion = ({ title, children, defaultValue }) => {
  const [isCollapsed, setIsCollapsed] = useState(defaultValue);

  return (
    <div css={accordionStyle} className={isCollapsed ? 'collapsed' : ''}>
      <div
        onClick={() => setIsCollapsed(!isCollapsed)}
        onKeyDown={undefined}
        role="button"
        tabIndex="-1"
      >
        <span className="title">{title}</span>
        <DownOutlined />
      </div>
      <div>
        <div className="contents">{children}</div>
      </div>
    </div>
  );
};
CustomAccordion.displayName = 'OverlaySettingAccordion';
CustomAccordion.propTypes = {
  title: PropTypes.string,
  children: PropTypes.node.isRequired,
  defaultValue: PropTypes.bool,
};
CustomAccordion.defaultProps = {
  defaultValue: true,
};

export default CustomAccordion;
