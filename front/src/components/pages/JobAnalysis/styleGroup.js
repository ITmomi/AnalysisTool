import { css, keyframes } from '@emotion/react';

export const bounce = keyframes`
  50% {
    transform: scale(1.2);
  }
  75% {
    transform: scale(.9);
  }
  100% {
    transform: scale(1);
  }
`;

export const mainWrapper = css`
  position: relative;
  overflow: hidden;
  background: white;
  min-height: 675px;
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgba(60, 64, 67, 0.3),
    0 2px 6px 2px rgba(60, 64, 67, 0.15);
  & .ant-tabs-tab-active {
    font-weight: bold;
  }
  & .ant-empty {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 300px;
    line-height: 0;
  }
  & .ant-spin-nested-loading > div > .ant-spin {
    background: white;
    min-height: 510px;
    max-height: 100%;
  }
  &.loading {
    height: 675px;
    & .ant-spin-nested-loading > div > .ant-spin {
      height: 600px;
    }
  }
`;

export const buttonWrapper = css`
  position: absolute;
  right: 17px;
  top: 94px;
  z-index: 1;
  & > button + button {
    margin-left: 1rem;
  }
`;

export const exportModalWrapper = css`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  column-gap: 1rem;
  & input[type='checkbox'] {
    display: none;
    &:checked + label {
      transform: translate(0em, 0.75em);
      &::before {
        box-shadow: 0 0 0 2px #cacaca, 0 0 #cacaca;
        transform: translate3d(0, 0, -1em);
      }
      & > svg:first-of-type {
        animation: ${bounce} 0.4s linear forwards;
      }
    }
  }
  & > label {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: white;
    border: 2px solid #828282;
    border-radius: 0.75em;
    transform-style: preserve-3d;
    transition: transform 0.15s cubic-bezier(0, 0, 0.58, 1),
      background 0.15s cubic-bezier(0, 0, 0.58, 1);
    height: 70px;
    cursor: pointer;
    user-select: none;
    &::before {
      position: absolute;
      content: '';
      width: 100%;
      height: 100%;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: #cacaca;
      border-radius: 0.75em;
      box-shadow: 0 0 0 2px #cacaca;
      transform: translate3d(0, 0.75em, -1em);
      transition: transform 0.15s cubic-bezier(0, 0, 0.58, 1),
        box-shadow 0.15s cubic-bezier(0, 0, 0.58, 1);
    }
    & > svg:first-of-type {
      display: block;
      pointer-events: none;
      fill: none;
      stroke-width: 4px;
      stroke-linecap: round;
      stroke-linejoin: round;
      stroke: #1890ff;
      position: absolute;
      top: 6px;
      left: 8px;
      width: 32px;
      height: 32px;
      transform: scale(0) translateZ(0);
    }
    & > span {
      font-size: 14px;
      font-weight: bold;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
  }
`;

export const breadcrumbWrapper = css`
  margin-bottom: 1rem;
  padding: 1rem 0.5rem;
  border-radius: 8px;
  background: aliceblue;
  box-shadow: 0 2px 4px 2px #d7e4ef;
`;

export const tableWrapper = css`
  position: relative;
  & > div + div {
    margin-top: 1rem;
  }
`;

/*
export const spinWrapper = css`
  min-height: 510px;
  display: flex;
  justify-content: center;
  align-items: center;
`;
 */
