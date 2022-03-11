import React from 'react';
import PropTypes from 'prop-types';
import { css } from '@emotion/react';

const radioGroupStyle = css`
  & > label {
    display: inline-block;
    & + label {
      margin-left: 1rem;
    }
    & > input[type='radio'] {
      display: none;
      &:checked {
        & + .button {
          background-color: #f5f5f5;
          &::after {
            opacity: 1;
          }
        }
      }
    }
    & > .button {
      position: relative;
      z-index: 1;
      padding: 0.5rem 1rem;
      border-radius: 8px;
      cursor: pointer;
      font-size: 16px;
      transition: background-color 0.3s ease-in-out;
      &::after {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        content: '';
        opacity: 0;
        border-radius: 8px;
        box-shadow: 0px 2px 4px 1px rgba(0, 0, 0, 0.2);
        transition: opacity 0.3s ease-in-out;
      }
      & svg {
        margin-right: 0.3rem;
      }
    }
  }
`;

const CustomRadioGroup = ({
  options,
  name,
  className,
  changeFunc,
  currentChecked,
}) => {
  return (
    <div css={radioGroupStyle}>
      {options?.map((v, i) => {
        return (
          <label htmlFor={v.id} key={i} className={className}>
            <input
              type="radio"
              name={name}
              id={v.id}
              checked={v.id === currentChecked}
              onChange={() => changeFunc(v.id)}
            />
            <div className={`button ${className}`}>
              {v.icon ? v.icon : ''}
              {v.title}
            </div>
          </label>
        );
      }) ?? <></>}
    </div>
  );
};
CustomRadioGroup.propTypes = {
  options: PropTypes.array.isRequired,
  name: PropTypes.string.isRequired,
  className: PropTypes.string,
  changeFunc: PropTypes.func.isRequired,
  currentChecked: PropTypes.string.isRequired,
};

export default CustomRadioGroup;
