import React, { useCallback, useMemo } from 'react';
import PropTypes from 'prop-types';
import { Table } from 'antd';
import { css } from '@emotion/react';
import { getTableForm } from '../../../../../lib/util/Util';
import { MSG_MAX, MSG_MIN } from '../../../../../lib/api/Define/Message';
const tableWrapper = css`
  display: contents;
`;

const MapLotTable = ({ origin, lot_id, lot_idx }) => {
  const lot_title = `LOT ${lot_idx}`;
  const getTableFuc = useCallback((data) => {
    const range = data.extra_info.range;
    const data_value = Object.values(range);
    const disp_order = Object.keys(range ?? {});
    const row = [MSG_MIN, MSG_MAX].map((key, i) => {
      return data_value.reduce(
        (acc, o, j) => ({ ...acc, [disp_order[j]]: o[i] }),
        {
          [lot_title]: key,
        },
      );
    });
    return getTableForm({
      info: { disp_order: [lot_title].concat(disp_order), row: row } ?? {},
    });
  }, []);
  const tableData = useMemo(() => getTableFuc(origin?.[lot_id]), [
    [lot_id, origin, getTableFuc],
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
MapLotTable.propTypes = {
  origin: PropTypes.object,
  lot_id: PropTypes.string,
  lot_idx: PropTypes.number,
};

export default MapLotTable;
