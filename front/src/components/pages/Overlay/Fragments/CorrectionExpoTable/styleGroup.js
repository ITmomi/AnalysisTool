import { css, keyframes } from '@emotion/react';

const bounce = keyframes`
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

export const controlTableStyle = css`
  margin: 0 auto;
  border-top: 1px solid #d9d9d9;
  table-layout: auto;
  border-collapse: collapse;
  & input[type='checkbox'] {
    display: none;
  }
  & label.only-checkbox {
    cursor: pointer;
    text-align: center;
    & > input[type='checkbox'] {
      &:checked ~ .mode-slider-wrapper > .slider {
        transform: translateY(-17px);
      }
    }
    & > .mode-slider-wrapper {
      overflow: hidden;
      height: 17px;
      font-weight: normal;
      text-transform: uppercase;
      & > .slider {
        display: flex;
        flex-direction: column;
        align-items: center;
        transition: transform 0.3s ease-in-out;
        row-gap: 2px;
        & > span {
          display: inline-block;
          font-size: 10px;
          border-radius: 4px;
          width: fit-content;
          padding: 0 0.2rem;
          color: white;
          &:first-of-type {
            background-color: red;
          }
          &:last-of-type {
            background-color: #1890ff;
          }
        }
      }
    }
  }
  & svg {
    display: block;
    pointer-events: none;
    fill: none;
    stroke-width: 2px;
    stroke-linecap: round;
    stroke-linejoin: round;
    stroke: #1890ff;
    position: absolute;
    transform: scale(0) translateZ(0);
  }
  & th {
    position: relative;
    padding: 0.5rem;
    border-bottom: 1px solid #d9d9d9;
    background-color: #f0f5ff;
    text-transform: uppercase;
    font-size: 12px;
    line-height: initial;
    & svg {
      top: 10px !important;
      left: 40px !important;
      width: 24px !important;
      height: 24px !important;
    }
  }
  & td {
    position: relative;
    border: none;
    border-bottom: 1px solid #d9d9d9;
    font-size: 12px;
    color: rgba(0, 0, 0, 0.8);
    line-height: initial;
    & > .text-checkbox {
      position: relative;
      & > input[type='text'] {
        font-family: Saira, sans-serif;
        border: none;
        outline: none !important;
        font-size: 12px;
        max-width: 125px;
        padding: 0.7rem 2rem 0.7rem 0.7rem;
        transition: background-color 0.3s ease-in-out;
        &:read-only {
          background-color: #f5f5f5;
        }
      }
      & > label {
        cursor: pointer;
        & > input[type='checkbox'] {
          &:checked ~ {
            & .svg-wrapper > svg {
              animation: ${bounce} 0.4s linear forwards;
            }
          }
        }
        & > .svg-wrapper {
          position: absolute;
          top: 6px;
          right: 3px;
          width: 24px;
          height: 24px;
          padding: 1px;
          border-radius: 4px;
          border: 1px solid #dadada;
          background-color: white;
        }
      }
    }
  }
`;
