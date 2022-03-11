import { css } from '@emotion/react';

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
  & .ant-form-item-label {
    width: 77px;
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
      min-height: 650px;
      & > div {
        &:first-of-type {
          & > form {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
          }
          & .ant-form-item-label > label,
          & .ant-select-selection-item-content,
          & .ant-select-selection-item,
          & input {
            font-size: 12px;
          }
          & .ant-row.ant-form-item {
            &:first-of-type {
              margin-bottom: 3rem;
            }
            &:first-of-type,
            &:nth-of-type(3) {
              & .ant-select-selector {
                cursor: pointer;
              }
              & .ant-select-selection-overflow-item-suffix {
                display: none;
              }
            }
            &:last-of-type {
              margin-bottom: 0;
            }
            & .multi-input {
              display: flex;
              & > input[type='text'] + input[type='text'] {
                margin-left: 1rem;
              }
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
                &::after {
                  width: 6px;
                  height: 6px;
                }
              }
            }
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
          & > div:first-of-type {
            white-space: break-spaces;
            text-align: center;
          }
        }
      }
    }
  }
`;
