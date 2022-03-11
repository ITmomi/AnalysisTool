import React, { useState } from 'react';
import AboutPage from '../../../pages/Info';
import Button from '../Button';
import PropTypes from 'prop-types';

const VersionInfo = ({ footer, info }) => {
  const [visible, setVisible] = useState(false);

  const showDrawer = () => {
    setVisible(true);
  };
  const onClose = () => {
    setVisible(false);
  };

  const { about, version, copyright } = footer;

  return (
    <>
      <p style={{ marginBottom: '0' }}>
        {copyright} <br />
        {version}
      </p>
      <Button
        theme={'white'}
        onClick={showDrawer}
        style={{
          textDecorationLine: 'underline',
          border: 'none',
          boxShadow: 'none',
          fontWeight: 400,
        }}
      >
        {about}
      </Button>
      <AboutPage show={visible} closeFunc={onClose} info={info} />
    </>
  );
};

VersionInfo.propTypes = {
  footer: PropTypes.shape({
    about: PropTypes.string,
    version: PropTypes.string,
    copyright: PropTypes.string,
  }),
  info: PropTypes.object,
};

export default VersionInfo;
