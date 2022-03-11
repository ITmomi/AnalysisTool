import React, { useContext } from 'react';
import { ModalDispatchContext, ModalStateContext } from './ModalContext';

const Modal = () => {
  const openedModal = useContext(ModalStateContext);
  const { close } = useContext(ModalDispatchContext);

  return openedModal.map((modal, idx) => {
    const { Component, props } = modal;
    const { onSubmit, ...restProps } = props;

    const onClose = () => {
      close(Component);
    };

    const handleSubmit = async () => {
      if (typeof onSubmit === 'function') {
        await onSubmit();
      }
      onClose();
    };

    return (
      <Component
        {...restProps}
        key={idx}
        onClose={onClose}
        onSubmit={handleSubmit}
      />
    );
  });
};

export default Modal;
