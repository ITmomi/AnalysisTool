import { css } from '@emotion/react';

export const mainWrapper = css`
  position: relative;
  & .ant-picker-input > input {
    font-size: 12px;
  }
  & > .table-wrapper {
    display: flex;
    flex-direction: column;
    flex-wrap: nowrap;
    border-radius: 8px;
    border: 1px solid #dddddd;
    box-shadow: 0px 2px 2px 0px rgba(0, 0, 0, 0.1);
    margin: 1rem 0;
    & > div {
      &:first-of-type {
        padding: 1rem;
        border-bottom: 1px solid #dddddd;
        background-color: #f5f5f5;
        border-radius: 8px 8px 0 0;
      }
      &:last-of-type {
        margin: 1rem;
        overflow: auto;
      }
    }
    & .select-wrapper {
      margin-bottom: 1rem;
      & > span {
        font-weight: bold;
      }
    }
  }
  & > .header-wrapper {
    position: relative;
    display: flex;
    justify-content: space-between;
    & > .popup-wrapper {
      display: flex;
      align-items: center;
      column-gap: 0.5rem;
      flex-wrap: nowrap;
      & > span {
        font-weight: bold;
      }
      &.ant-picker {
        margin-left: 0.5rem;
        margin-right: 1rem;
      }
      & > .filter-component {
        position: relative;
        display: inline-block;
        & > button:hover + div:first-of-type {
          display: block;
        }
        & > div:first-of-type {
          position: absolute;
          display: none;
          font-size: 12px;
          color: white;
          top: 3px;
          right: -90px;
          padding: 4px;
          border-radius: 2px;
          background: rgba(0, 0, 0, 0.65);
          &::after {
            position: absolute;
            content: '';
            border-style: solid;
            border-color: transparent rgba(0, 0, 0, 0.65) transparent
              transparent;
            border-width: 4px;
            top: 9px;
            left: -8px;
          }
        }
      }
    }
  }
`;

export const popupBackground = css`
  position: fixed;
  display: none;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  width: 100%;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.1);
  outline: none;
`;

export const popupStyle = css`
  position: absolute;
  display: none;
  left: -10px;
  top: 46px;
  z-index: 1000;
  width: 400px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 3px 6px -4px rgba(0, 0, 0, 0.12),
    0 6px 16px 0 rgba(0, 0, 0, 0.12), 0 9px 28px 8px rgba(0, 0, 0, 0.05);
  font-family: Saira;
  &::before {
    position: absolute;
    transform: rotate(-45deg);
    top: -4px;
    left: 21px;
    width: 10px;
    height: 10px;
    content: '';
    border: 5px solid #f0f0f0;
    border-color: #fff #fff transparent transparent;
    box-shadow: 2px -2px 6px rgba(0, 0, 0, 0.06);
  }
  &::after {
    position: absolute;
    top: -10px;
    left: 0;
    width: 100%;
    height: 20px;
    content: '';
    background: transparent;
  }
  & > div {
    width: 100%;
    padding: 0.5rem 1rem;
    &:first-of-type {
      font-weight: bold;
      border-bottom: 1px solid #f0f0f0;
    }
    &:nth-of-type(2) {
      font-size: 12px;
      & > div + div {
        margin-top: 0.5rem;
      }
    }
    &:last-of-type {
      padding-top: 0.3rem;
      text-align: right;
      & > button {
        font-size: 12px;
      }
      & > button + button {
        margin-left: 1rem;
      }
    }
  }
`;

export const selectWrapper = css`
  display: flex;
  align-items: center;
  & > label {
    font-size: 12px;
    margin-left: 0.5rem;
  }
`;

export const aggregationWrapper = css`
  display: flex;
`;

export const aggSingleItemWrapper = css`
  width: 100%;
`;

export const emptyWrapper = css`
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 463px;
`;
