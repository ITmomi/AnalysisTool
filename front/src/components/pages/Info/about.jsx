import React from 'react';
import { Divider, Drawer } from 'antd';
import PropTypes from 'prop-types';
import ReactMarkdown from 'react-markdown';
import { css } from '@emotion/react';
import gfm from 'remark-gfm';

const ItemDiv = css`
  margin-bottom: 7px;
  color: rgba(0, 0, 0, 0.65);
  font-size: 14px;
  line-height: 1.5715;
`;

const ItemLabel = css`
  display: inline-block;
  margin-right: 8px;
  color: rgba(0, 0, 0, 0.85);
`;

const AboutPage = ({ show, closeFunc, info }) => {
  if (info == null) return <div>Waiting</div>;

  const { title, version, app_mode, copyright, licenses } = info;

  return (
    <>
      <Drawer
        title={title}
        width={600}
        closable={true}
        onClose={closeFunc}
        visible={show}
        placement="right"
      >
        <div css={ItemDiv}>
          <p css={ItemLabel}>{'Version'}:</p>
          {version}
        </div>
        <div css={ItemDiv}>
          <p css={ItemLabel}>{'App Mode'}:</p>
          {app_mode}
        </div>
        <div css={ItemDiv}>
          <p css={ItemLabel}>{'CopyRight'}:</p>
          {copyright}
        </div>
        <Divider />
        <ReactMarkdown remarkPlugins={[gfm]}>{licenses}</ReactMarkdown>
      </Drawer>
    </>
  );
};

AboutPage.propTypes = {
  show: PropTypes.bool,
  closeFunc: PropTypes.func,
  info: PropTypes.shape({
    title: PropTypes.string,
    version: PropTypes.string,
    app_mode: PropTypes.string,
    copyright: PropTypes.string,
    licenses: PropTypes.string,
  }),
};

export default AboutPage;
