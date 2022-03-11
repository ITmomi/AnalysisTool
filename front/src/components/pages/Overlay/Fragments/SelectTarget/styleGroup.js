import styled from '@emotion/styled';

export const CustomSelect = styled.div`
  display: flex;
  align-items: center;
  column-gap: 8px;
  padding: 0 8px;

  @keyframes shadow {
    50% {
      box-shadow: none;
      border-color: #d9d9d9;
    }
  }

  & > .input-error {
    animation: shadow 1s ease-in-out infinite;
    box-shadow: 0px 0px 3px 1px red;
    border-color: red;
  }

  & > .button {
    display: flex;
    align-items: center;
    cursor: pointer;
    font-size: 16px;
    padding: 2px;
    & > span {
      transition: all 0.5s;
      & > svg {
        stroke: black;
        stroke-width: 30px;
      }
    }
    &.error {
      cursor: not-allowed;
      & > span {
        transform: rotate(45deg);
        opacity: 0.5;
      }
    }
  }
`;

export const MeanAll = styled.div`
  padding: 8px;
  & input {
    display: none;
    &:checked + .button {
      background-color: #1890ff;
      color: white;
    }
  }
  & .button {
    width: 100%;
    padding: 0.2rem 0;
    cursor: pointer;
    text-align: center;
    border-radius: 4px;
    border: 1px solid #1890ff;
    color: #1890ff;
    background-color: white;
    transition: all 0.2s ease-in-out;
  }
`;
