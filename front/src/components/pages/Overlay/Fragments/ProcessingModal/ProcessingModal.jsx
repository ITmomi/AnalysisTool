import React from 'react';
import PropTypes from 'prop-types';
import { Modal } from 'antd';
import { Contents, Spinner } from './styleGroup';

const ProcessingModal = ({ title, message }) => {
  return (
    <Modal
      visible
      centered
      title={title}
      width={400}
      footer={null}
      closable={false}
    >
      <Contents>
        <Spinner>
          <div className="spinner-item" />
          <div className="spinner-item" />
          <div className="spinner-item" />
          <div className="spinner-item" />
          <div className="spinner-item" />
        </Spinner>
        <div className="message">
          {message}
          <span>.</span>
          <span>.</span>
          <span>.</span>
        </div>
      </Contents>
    </Modal>
  );
};

export default ProcessingModal;

ProcessingModal.propTypes = {
  title: PropTypes.string.isRequired,
  message: PropTypes.string.isRequired,
};
