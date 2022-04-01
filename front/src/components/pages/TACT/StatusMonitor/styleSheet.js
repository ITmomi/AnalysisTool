import { css, keyframes } from '@emotion/react';

/*
#=========================================#
| TactStatusMonitor CSS                   |
#=========================================#
*/

export const sectionStyle = css`
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  width: 100%;
  padding: 1rem;
`;

const moveLeft = keyframes`
  25% {
    transform: translateX(-25px);
  }
  50% {
    transform: translateX(0);
  }
`;

export const componentStyle = css`
  position: relative;
  padding: 1rem;
  min-height: 300px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0px 0px 8px 2px rgba(0, 0, 0, 0.15);
  &.stretch {
    align-self: stretch;
  }
  &.span {
    display: flex;
    flex-direction: column;
    row-gap: 2rem;
    grid-column: 1 / span 2;
  }
  & .source-button-wrapper {
    position: absolute;
    bottom: 16px;
    right: 16px;
  }
  & > .ant-spin {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    row-gap: 0.5rem;
    background-color: white;
    border-radius: 4px;
    &.ant-spin-spinning {
      z-index: 1200;
    }
  }
  & .foreground {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border-radius: 4px;
    display: none;
    justify-content: center;
    align-items: center;
    background-color: white;
    &.active {
      display: flex;
      z-index: 5;
      & > div {
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        row-gap: 1rem;
        & > svg {
          position: relative;
          animation: ${moveLeft} 1.5s ease-in-out infinite;
        }
        & > p {
          font-size: 20px;
          font-weight: bold;
        }
      }
    }
  }
`;

export const componentTitleStyle = css`
  font-size: 24px;
  color: #1890ff;
`;

export const contentWrapperStyle = css`
  position: relative;
  margin-top: 3rem;
  min-height: 300px;
  &.mg-bottom {
    margin-bottom: 13px;
  }
  &.ts-source-button-wrapper {
    position: relative;
    text-align-last: center;
    right: -477px;
  }
`;

export const contentStyle = css`
  margin: 0 auto;
  width: 60%;
  &.full-width {
    width: 100%;
  }
  & > div + div {
    margin-top: 2rem;
  }
`;

export const contentItemStyle = css`
  display: grid;
  column-gap: 1rem;
  align-items: center;
  &.column-2 {
    grid-template-columns: 0.4fr 1fr;
  }
  &.column-3 {
    grid-template-columns: 0.4fr 1fr 1fr;
  }
  &.etc {
    display: flex;
    justify-content: space-between;
  }
  & > span {
    position: relative;
    &:first-of-type {
      position: relative;
      &.label {
        &::before {
          display: inline-block;
          color: red;
          font-size: 16px;
          content: '*';
          margin-right: 0.3rem;
        }
        &::after {
          display: inline-block;
          content: ':';
        }
      }
    }
  }
  &.upload {
    & > span {
      &:first-of-type {
        align-self: start;
      }
      &:last-of-type {
        width: 100%;
        max-width: 471.9px;
        & .ant-upload-list-text {
          margin-top: 0.5rem;
          overflow: auto;
          height: 120px;
          &::-webkit-scrollbar {
            width: 8px;
          }
          &::-webkit-scrollbar-track {
            background-color: transparent;
          }
          &::-webkit-scrollbar-thumb {
            border-radius: 4px;
            background-color: rgba(0, 0, 0, 0.2);
          }
          &::-webkit-scrollbar-button {
            width: 0;
            height: 0;
          }
        }
      }
    }
    & .full-width {
      & > .ant-upload-select-text,
      & button {
        width: 100%;
      }
    }
  }
  & > .title {
    width: 100%;
    text-align: center;
    font-size: 20px;
  }
  & > .preset-setting {
    display: flex;
    column-gap: 1rem;
  }
  & .radio-cp-vs {
    display: grid;
    grid-template-columns: repeat(3, 18rem);
    column-gap: 1rem;
    grid-column: span 2;
  }
  & .margin-lr {
    margin: 0 1rem;
  }
  & .margin-r {
    margin-right: 1rem;
  }
  & .tx-right {
    text-align: right;
  }
  & ~ div {
    margin-top: 2rem;
    &.table-wrapper {
      margin-top: 1rem;
    }
  }
  .ant-form-item {
    width: 289px;
    margin-bottom: 0px;
  }
  .ant-form-item-explain-connected {
    min-height: 0px;
  }
  .ant-col-16 {
    max-width: 100%;
  }
`;

export const customButtonStyle = css`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background-color: white;
  border: none;
  & > span {
    &:first-of-type {
      font-size: 26px;
      color: #1890ff;
    }
    &:last-of-type {
      font-size: 8px;
      font-weight: 600;
    }
  }
  &.absolute {
    position: absolute;
    bottom: -5px;
    right: 50px;
    & > span:first-of-type {
      color: #52c41a;
    }
  }
  &:disabled {
    cursor: not-allowed;
    opacity: 0.5;
    & > span:first-of-type {
      color: #c9c9c9;
    }
  }
`;

export const tableStyle = css`
  margin: 0 auto;
  border: 1px solid #d9d9d9;
  border-collapse: collapse;
  table-layout: auto;
  text-align: center;
  & th,
  td {
    border: 1px solid #d9d9d9;
    padding: 0.5rem;
  }
  & th {
    background-color: #fafafa;
  }
`;

export const antdButtonStyle = css`
  position: relative;
  padding: 0.5rem 1rem;
  border-radius: 14px;
  box-shadow: 0px 2px 4px 1px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  white-space: pre;
  &.white {
    background-color: white;
    border: 1px dashed #d9d9d9;
    &:disabled {
      background-color: #d9d9d9;
      color: transparent;
      &::before {
        position: absolute;
        width: 100%;
        top: 5px;
        left: 0;
        content: 'X';
        color: white;
        font-weight: bold;
        font-size: 20px;
      }
    }
  }
  &.blue {
    color: white;
    background-color: #1890ff;
    border: 1px solid #1890ff;
  }
  &:disabled {
    cursor: not-allowed;
  }
  &:active {
    box-shadow: none;
    transform: translateY(2px);
  }
`;

export const controlStyle = css`
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
`;

export const settingStyle = css`
  position: relative;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0px 0px 8px 2px rgba(0, 0, 0, 0.15);
  & > .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem;
    & > span {
      font-size: 18px;
    }
    & > div > button + button {
      margin-left: 1rem;
    }
  }
  & > .main {
    & > div + div {
      margin-top: 0.1rem;
    }
  }
`;

export const resultStyle = css`
  position: relative;
  min-height: 300px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0px 0px 8px 2px rgba(0, 0, 0, 0.15);
  padding: 1rem;
`;

export const radioGroupStyle = css`
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

export const componentRadioStyle = css`
  font-size: 20px;
  color: #1890ff;
  border: none;
  cursor: pointer;
`;

export const subTitleStyle = css`
	font-size: larger;
`;

export const tsStartButtonStyle = css`
	position: relative;
	margin-top: 10px;
`;

export const tactGraphSettingStyle = css`
	margin: 0 auto;
    width: 45%;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    & > div {
        display: flex;
        & > span {
            display: flex;
            align-items: center;
            width: 150px;
        }
    }
	`;

export const tactGraphColorButtonStyle = css`
	background: #FFFFFF;
    border-radius: 10px;
    border: none;
    box-shadow: none;
    margin-right: 30px;
    font-weight: 600;
	font-size: 16px;
	line-height: 24px;
	color: #595959;
    :hover {
        background: #1890FF;
		border: 1px solid #1890FF;
		box-sizing: border-box;
		box-shadow: 0px 0px 4px rgba(24, 144, 255, 0.5);
		border-radius: 10px;
		color: #ffffff;
        border-color: #1890FF;
    }
`;

export const tactGraphColorSettingStyle = css`
	margin: 0 auto;
    width: 60%;
    display: flex;
`;

export const tactColorBoxStyle = css`
    width: 400px;
	& .rc-color-picker-trigger {
		width: 40px;
		height: 40px;
		border-radius: 10px;
        border: none;
	}
`;

/*
#=========================================#
| TactTSMemoryDump CSS                    |
#=========================================#
*/

export const tsComponentStyle = css`
  position: relative;
  padding: 1rem;
  min-height: 300px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0px 0px 8px 2px rgba(0, 0, 0, 0.15);
  &.stretch {
    align-self: stretch;
  }
  &.span {
    display: flex;
    flex-direction: column;
    row-gap: 2rem;
  }
`;

export const tsMemoryDumpSectionStyle = css`
  display: grid;
  position: relative;
  width: 100%;
  padding: 1rem;
  row-gap: 1rem;
`;

export const tsMemoryDumpContentItemStyle = css`
  display: grid;
  column-gap: 1rem;
  align-items: center;
  margin: 0 auto;
  width: 50%;
  &.column-2 {
    grid-template-columns: 0.4fr 1fr;
  }
  &.column-3 {
    grid-template-columns: 0.4fr 1fr 1fr;
  }
  & > span {
    position: relative;
    &:first-of-type {
      position: relative;
      &.label {
        &::before {
          display: inline-block;
          color: red;
          font-size: 16px;
          content: '*';
          margin-right: 0.3rem;
        }
        &::after {
          display: inline-block;
          content: ':';
        }
      }
    }
  }
  &.upload {
    & > span {
      &:first-of-type {
        align-self: start;
      }
      &:last-of-type {
        width: 100%;
        & .ant-upload-list-text {
          margin-top: 0.5rem;
          overflow: auto;
          height: 60px;
          &::-webkit-scrollbar {
            width: 8px;
          }
          &::-webkit-scrollbar-track {
            background-color: transparent;
          }
          &::-webkit-scrollbar-thumb {
            border-radius: 4px;
            background-color: rgba(0, 0, 0, 0.2);
          }
          &::-webkit-scrollbar-button {
            width: 0;
            height: 0;
          }
        }
      }
    }
    & .full-width {
      & > .ant-upload-select-text,
      & button {
        width: 100%;
      }
    }
  }
	& .radioStyle {
		display: flex;
        justify-content: space-between;
	}
`;

export const tsTableStyle = css`
	padding : 1rem;
	& .ant-table-thead > tr > th {
	font-weight: 900;
    text-align: center;
	}
	& .ant-table-tbody > tr {
		& td:nth-child(n+3):nth-child(-n+5) {
			text-align: center;
		} 
	}
	.ant-tag {
		margin-right : 50px;
	}
	& ul {
		display: none;
	}

`;
export const lineStyle = css`
	border: 1px solid #D9D9D9;
	`;