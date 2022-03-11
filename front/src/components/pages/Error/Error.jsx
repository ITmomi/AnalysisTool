import React from 'react';
import { Button, Result } from 'antd';
import { Link } from 'react-router-dom';
import AppLayout from '../../templates';
import PropTypes from 'prop-types';
import { MAIN } from '../../../lib/api/Define/URL';

const Error = ({ children }) => {
  return <AppLayout>{children}</AppLayout>;
};

Error.propTypes = {
  children: PropTypes.node,
};

const InternalErrorPage = () => {
  return (
    <>
      <Result
        status="500"
        title="500"
        subTitle="Sorry, something went wrong."
        extra={
          <Link to={MAIN}>
            <Button type="primary">Back Home</Button>
          </Link>
        }
      />
    </>
  );
};

const NotFoundPage = () => {
  return (
    <>
      <Result
        status="404"
        title="404"
        subTitle="Sorry, the page you visited does not exist."
        extra={
          <Link to={MAIN}>
            <Button type="primary">Back Home</Button>
          </Link>
        }
      />
    </>
  );
};

Error.notfound = NotFoundPage;
Error.internal = InternalErrorPage;

export default Error;
