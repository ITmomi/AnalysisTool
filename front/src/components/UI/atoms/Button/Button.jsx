import React from 'react';
import PropTypes from 'prop-types';
import { css, keyframes } from '@emotion/react';

const Button = ({
  children,
  onClick,
  theme,
  size,
  disabled,
  width,
  iconOnly,
  style,
}) => {
  return (
    <button
      css={[
        defaultStyle,
        themes[theme],
        sizes[size],
        { width },
        iconOnly && [iconOnlyStyle, iconOnlySizes[size]],
        style,
      ]}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

Button.displayName = 'Button';
Button.propTypes = {
  children: PropTypes.node.isRequired,
  onClick: PropTypes.func,
  theme: PropTypes.oneOf(['blue', 'green', 'orange', 'white', 'antd']),
  size: PropTypes.oneOf(['sm', 'md', 'lg']),
  disabled: PropTypes.bool,
  width: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  iconOnly: PropTypes.bool,
  style: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
};
Button.defaultProps = {
  theme: 'blue',
  size: 'sm',
  disabled: false,
};

const blink = keyframes`
  0% {
    transform: scale(1.2);
  }
  25%, 50% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: scale(1.4);
  }
`;

const defaultStyle = css`
  outline: none;
  border: none;
  color: white;
  box-sizing: border-box;
  border-radius: 0.5rem;
  height: 2rem;
  font-family: Saira, 'Nunito Sans';
  font-size: 0.875rem;
  padding: 0 1rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0px 3px 3px rgba(0, 0, 0, 0.25);
  &:active:not(:disabled) {
    transform: translateY(2px);
    box-shadow: none;
  }
  &:hover:not(:disabled) {
    cursor: pointer;
  }
  &:disabled {
    cursor: not-allowed;
  }
  svg {
    fill: currentColor;
    width: 1em;
    margin-right: 14px;
  }
`;

const themes = {
  blue: css`
    background: rgb(24, 144, 255);
    &:hover:not(:disabled) {
      background: rgba(24, 144, 255, 0.8);
    }
    &:disabled {
      background: rgba(24, 144, 255, 0.4);
    }
  `,
  green: css`
    background: rgb(60, 191, 100);
    &:hover:not(:disabled) {
      background: rgba(60, 191, 100, 0.8);
    }
    &:disabled {
      background: rgba(60, 191, 100, 0.4);
    }
  `,
  orange: css`
    background: rgb(232, 92, 25);
    &:hover:not(:disabled) {
      background: rgba(232, 92, 25, 0.8);
    }
    &:disabled {
      background: rgba(232, 92, 25, 0.4);
    }
  `,
  white: css`
    background: white;
    color: rgba(0, 0, 0, 0.85);
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: 0px 3px 3px rgba(0, 0, 0, 0.1);
    &:hover:not(:disabled) {
      background: rgba(0, 0, 0, 0.05);
    }
    &:disabled {
      color: rgba(0, 0, 0, 0.2);
      background: rgba(0, 0, 0, 0.04);
    }
  `,
  antd: css`
    position: relative;
    background: white;
    color: rgba(0, 0, 0, 0.85);
    border: 1px dashed #d9d9d9;
    box-shadow: none;
    transition: all 0.3s cubic-bezier(0.645, 0.045, 0.355, 1);
    &:after {
      position: absolute;
      content: '';
      width: 100%;
      height: 100%;
      border-radius: 50%;
      opacity: 0;
      background: transparent;
      border: 2px solid rgba(24, 144, 255, 0.15);
    }
    &:hover:not(:disabled) {
      color: #1890ff;
      border-color: #1890ff;
    }
    &:active:not(:disabled) {
      transform: none;
      &:after {
        animation: ${blink} 0.3s forwards;
      }
    }
    &:disabled {
      color: rgba(0, 0, 0, 0.2);
      background: rgba(0, 0, 0, 0.04);
    }
  `,
};

const sizes = {
  sm: css`
    height: 1.75rem;
    font-size: 0.75rem;
    padding: 0 0.875rem;
  `,
  md: css`
    height: 2.5rem;
    font-size: 1rem;
    padding: 0 1rem;
  `,
  lg: css`
    height: 3rem;
    font-size: 1.125rem;
    padding: 0 1.5rem;
  `,
};

const iconOnlyStyle = css`
  padding: 0;
  border-radius: 50%;
  svg {
    margin: 0;
  }
`;

const iconOnlySizes = {
  sm: css`
    width: 1.75rem;
  `,
  md: css`
    width: 2.5rem;
  `,
  lg: css`
    width: 3rem;
  `,
};

export default Button;
