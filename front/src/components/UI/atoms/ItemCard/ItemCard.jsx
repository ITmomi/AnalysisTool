import React from 'react';
import PropTypes from 'prop-types';
import { css } from '@emotion/react';

const ItemCard = ({ children, style, width, height }) => {
  return <div css={[wrapperStyle, style, { width, height }]}>{children}</div>;
};

ItemCard.displayName = 'ItemCard';
ItemCard.propTypes = {
  children: PropTypes.node.isRequired,
  style: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  width: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  height: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
};
ItemCard.defaultProps = {
  children: <p>some contents here</p>,
  width: '250px',
  height: '250px',
};

const wrapperStyle = css`
  font-family: Saira, 'Nurito Sans';
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);
  border-radius: 0.5rem;
  background: white;
  padding: 1rem 0;
  position: relative;
`;

export default ItemCard;
