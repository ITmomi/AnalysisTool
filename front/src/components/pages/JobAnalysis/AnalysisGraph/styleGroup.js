import { css } from '@emotion/react';

export const mainWrapper = css`
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap;
  border-radius: 8px;
  border: 1px solid #dddddd;
  box-shadow: 0px 2px 2px 0px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
  width: 100%;
  & > div {
    width: 100%;
    padding: 1rem;
    &:first-of-type {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #dddddd;
      background-color: #f5f5f5;
      border-radius: 8px 8px 0 0;
    }
    &:last-of-type {
      border-radius: 0 0 8px 8px;
      & > .ant-table-wrapper {
        border: 1px solid #dddddd;
      }
    }
  }
`;

export const graphBodyStyle = css`
  display: grid;
  position: relative;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: auto;
  gap: 1rem;
`;

export const emptyWrapper = css`
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  & > div {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
  }
`;

export const graphWrapper = css`
  position: relative;
  &:hover > div:first-of-type {
    opacity: 1;
  }
  & > div {
    &:first-of-type {
      position: absolute;
      opacity: 0;
      transition: all 0.3s;
      z-index: 1;
      & > button + button {
        margin-left: 1rem;
      }
    }
    &:last-of-type {
      display: flex;
      justify-content: center;
      align-items: center;
    }
  }
`;
