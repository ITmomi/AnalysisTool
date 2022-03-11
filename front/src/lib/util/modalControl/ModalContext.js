import { createContext } from 'react';

export const ModalDispatchContext = createContext({
  open: () => {},
  close: () => {},
});

export const ModalStateContext = createContext([]);
