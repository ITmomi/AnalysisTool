import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import { Table } from 'antd';
import { css } from '@emotion/react';
import useOverlayResultInfo from '../../../../../hooks/useOverlayResultInfo';
const tableWrapper = css`
  display: contents;
`;
const AnovaTable = ({ origin, selected }) => {
  const { getAnovaTableFuc } = useOverlayResultInfo();

  const tableData = useMemo(() => getAnovaTableFuc(origin?.[selected] ?? {}), [
    [selected, origin, getAnovaTableFuc],
  ]);

  return (
    <>
      <div css={tableWrapper}>
        <Table
          bordered
          pagination={false}
          columns={tableData.columns ?? []}
          dataSource={tableData.dataSource ?? []}
          size="middle"
          rowKey="key"
          scroll={{ x: 'max-content' }}
        />
      </div>
    </>
  );
};
AnovaTable.propTypes = {
  origin: PropTypes.object,
  selected: PropTypes.string,
};

export default AnovaTable;
