import styled from '@emotion/styled';

export const Contents = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  row-gap: 1rem;

  @keyframes blink {
    25% {
      opacity: 0.5;
    }
    50% {
      opacity: 0;
    }
  }

  & .message {
    font-size: 16px;
    & > span {
      --animation-delay: 1500ms;
      animation: blink var(--animation-delay) ease-in-out infinite;
      &:nth-of-type(2) {
        animation-delay: calc(var(--animation-delay) / 5);
      }
      &:nth-of-type(3) {
        animation-delay: calc(var(--animation-delay) / 5 * 2);
      }
    }
  }
`;

export const Spinner = styled.div`
  --animation-delay: 1000ms;
  --frame-width: 120px;
  display: flex;
  width: var(--frame-width);
  height: 100px;
  justify-content: center;
  align-items: center;
  gap: 10px;

  @keyframes spinner {
    25% {
      transform: scaleY(2);
    }
    50% {
      transform: scaleY(1);
    }
  }

  & > .spinner-item {
    height: 50%;
    background-color: var(--spinner-color);
    width: calc(var(--frame-width) / 5);
    animation: spinner var(--animation-delay) ease-in-out infinite;
    border-radius: 6px;
    &:nth-of-type(1) {
      --spinner-color: rgba(24, 144, 255, 0.2);
    }
    &:nth-of-type(2) {
      --spinner-color: rgba(24, 144, 255, 0.4);
      animation-delay: calc(var(--animation-delay) / 10);
    }
    &:nth-of-type(3) {
      --spinner-color: rgba(24, 144, 255, 0.6);
      animation-delay: calc(var(--animation-delay) / 10 * 2);
    }
    &:nth-of-type(4) {
      --spinner-color: rgba(24, 144, 255, 0.8);
      animation-delay: calc(var(--animation-delay) / 10 * 3);
    }
    &:nth-of-type(5) {
      --spinner-color: #1890ff;
      animation-delay: calc(var(--animation-delay) / 10 * 4);
    }
  }
`;
