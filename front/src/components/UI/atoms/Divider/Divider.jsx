import React from 'react';
import PropTypes from 'prop-types';
import { css } from '@emotion/react';

const Divider = ({ color, type, width, height, style }) => {
  return (
    <hr
      css={[
        { width: width || '100%', borderWidth: height || '1px' },
        colors[color],
        types[type],
        style,
      ]}
    />
  );
};

Divider.displayName = 'Divider';
Divider.propTypes = {
  color: PropTypes.oneOf(['gray', 'black']),
  type: PropTypes.oneOf(['dot', 'dash', 'solid']),
  width: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  height: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  style: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
};
Divider.defaultProps = {
  color: 'gray',
  type: 'dash',
};

const colors = {
  gray: css`
    border-color: rgba(0, 0, 0, 0.1);
  `,
  black: css`
    border-color: black;
  `,
};

const types = {
  dot: css`
    border-style: dotted;
  `,
  dash: css`
    border-style: dashed;
  `,
  solid: css`
    border-style: solid;
  `,
};

export default Divider;
