import React from 'react';
import { css } from '@emotion/react';
import PropTypes from 'prop-types';
import { Layout as AntdLayout } from 'antd';

const {
  Header: AntdHeader,
  Content: AntdContent,
  Footer: AntdFooter,
} = AntdLayout;

/*****************************************************************************
 *               Main Layout
 *****************************************************************************/

const style = css`
  position: relative;
  width: 1920px;
  margin: 0 auto;
  min-height: 100vh;
`;

const AppLayout = ({ children }) => {
  return <AntdLayout css={style}>{children}</AntdLayout>;
};

AppLayout.propTypes = {
  children: PropTypes.node,
};

/*****************************************************************************
 *               Header
 *****************************************************************************/

const headerStyle = css`
  width: 100%;
  position: sticky;
  z-index: 300;
  height: 140px;
  background: white;
  left: 0;
  top: 0;
  right: 0;
  text-align: center;
`;

const Header = ({ children }) => {
  return <AntdHeader css={headerStyle}>{children}</AntdHeader>;
};

Header.propTypes = {
  children: PropTypes.node,
};

/*****************************************************************************
 *               Contents
 *****************************************************************************/

const contentStyle = css`
  width: 100%;
  position: relative;
  padding: 3rem 50px 1rem;
  & .category-wrapper + .category-wrapper {
    margin-top: 3rem;
  }
`;

const Contents = ({ children }) => {
  return <AntdContent css={contentStyle}>{children}</AntdContent>;
};

Contents.propTypes = {
  children: PropTypes.node,
};

/*****************************************************************************
 *               Footer
 *****************************************************************************/

const footerStyle = css`
  width: 100%;
  position: relative;
  height: 100px;
  background: white;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
  & button {
    color: #1890ff;
  }
`;
const Footer = ({ children }) => {
  return <AntdFooter css={footerStyle}>{children}</AntdFooter>;
};

Footer.propTypes = {
  children: PropTypes.node,
};

AppLayout.Header = Header;
AppLayout.Content = Contents;
AppLayout.Footer = Footer;

export default AppLayout;
