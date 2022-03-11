import React from 'react';
import PropTypes from 'prop-types';
import { css } from '@emotion/react';

const FormCard = ({ title, children, formStyle, titleStyle }) => {
  return (
    <div css={[formMainStyle, formStyle]}>
      <div css={[formTitleStyle, titleStyle]}>{title}</div>
      {children}
    </div>
  );
};

FormCard.displayName = 'FormCard';
FormCard.propTypes = {
  title: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
    PropTypes.node,
  ]),
  children: PropTypes.node.isRequired,
  formStyle: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  titleStyle: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
};
FormCard.defaultProps = {
  title: '',
};

const formMainStyle = css`
  padding: 1rem;
  background: #f0f5ff;
`;

const formTitleStyle = css`
  color: #1890ff;
  font-weight: 600;
  margin-bottom: 1em;
`;

export default FormCard;
