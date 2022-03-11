import { css } from '@emotion/react';

export const backgroundStyle = css`
  position: fixed;
  z-index: 1000;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.1);
  width: 100%;
  outline: none;
`;

export const mainStyle = css`
  position: fixed;
  z-index: 1001;
  top: 50%;
  left: 50%;
  min-width: 1200px;
  background: white;
  transform: translate(-50%, -50%);
  border-radius: 0.5rem;
  box-shadow: 0px 0px 12px rgba(0, 0, 0, 0.2);
  font-size: 12px;
  & .ant-select-item-option,
  & .ant-select-selection-item-content {
    font-size: 12px;
    font-family: Saira, sans-serif;
  }
  & .ant-form-item-label {
    flex-basis: 20%;
  }
  & > div {
    padding: 1rem;
    &:first-of-type {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 14px;
      font-weight: 600;
      border-bottom: 1px solid rgba(0, 0, 0, 0.1);
      & button {
        font-size: 12px;
      }
      & button + button {
        margin-left: 1rem;
      }
    }
    &:nth-of-type(2) {
      display: grid;
      grid-template-columns: 400px 800px;
      column-gap: 1rem;
      & > div {
        &:first-of-type {
          & .ant-form-item-label > label,
          & .ant-select-selection-item-content,
          & .ant-select-selection-item,
          & input {
            font-size: 12px;
          }
          & .ant-row.ant-form-item {
            &:nth-of-type(4) {
              & .ant-select-selector {
                cursor: pointer;
              }
              & .ant-select-selection-overflow-item-suffix {
                display: none;
              }
            }
            &:last-of-type {
              margin-bottom: 0;
              border: 1px dashed rgba(0, 0, 0, 0.1);
            }
          }
          & .ant-form-item-control .ant-radio-wrapper {
            & > span:last-of-type {
              font-size: 12px;
            }
            & > .ant-radio {
              top: 0.3em;
              & > .ant-radio-inner {
                width: 14px;
                height: 14px;
              }
            }
          }
          & .ace_bracket {
            display: none;
          }
        }
        &:last-of-type {
          position: relative;
          display: flex;
          justify-content: center;
          align-items: center;
          overflow: auto;
          border: 1px dashed rgba(0, 0, 0, 0.1);
          & > button {
            position: absolute;
            font-size: 12px;
            top: 10px;
            left: 10px;
          }
          & > div {
            &:first-of-type {
              white-space: break-spaces;
              text-align: center;
            }
          }
        }
      }
    }
  }
`;

export const popconfirmWrapper = css`
  & > p {
    margin-bottom: 0;
  }
`;
