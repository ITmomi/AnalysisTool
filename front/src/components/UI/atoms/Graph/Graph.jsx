import React, { useEffect } from 'react';
import PropTypes from 'prop-types';
import { css } from '@emotion/react';
import Plot from 'react-plotly.js';

const graphWrapper = css`
  display: flex;
  justify-content: center;
  align-items: center;
`;

const Graph = React.memo(({ plotProps, wrapperStyle }) => {
  useEffect(() => {
    return () => {
      return null;
    };
  }, []);
  return (
    <div css={[graphWrapper, wrapperStyle]}>
      <Plot {...plotProps} />
    </div>
  );
});

Graph.displayName = 'Graph';
Graph.propTypes = {
  plotProps: PropTypes.object.isRequired,
  wrapperStyle: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
};

export default Graph;
