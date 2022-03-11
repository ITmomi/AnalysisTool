import { useContext } from 'react';
import { ModalDispatchContext } from './ModalContext';

export default function useModal() {
  const { open, close } = useContext(ModalDispatchContext);

  const openModal = (Component, props) => {
    open(Component, props);
  };

  const closeModal = (Component) => {
    close(Component);
  };

  return {
    openModal,
    closeModal,
  };
}
