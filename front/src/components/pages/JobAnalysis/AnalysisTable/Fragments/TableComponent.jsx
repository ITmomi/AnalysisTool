import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import ReactTable from '../../../../UI/atoms/Table/ReactTable';
import useResultInfo from '../../../../../hooks/useResultInfo';
import { searchKey } from '../../functionGroup';

const AnalysisTableComponent = ({ tableOrder, tableData, selectRow }) => {
  const { savedAnalysisAggregation, setSelectedRow } = useResultInfo();
  const columnData = useMemo(() => tableOrder, [JSON.stringify(tableOrder)]);
  const rowData = useMemo(() => tableData, [JSON.stringify(tableData)]);

  const changeSelectedRow = (v) => {
    const key =
      savedAnalysisAggregation.main.toLowerCase() === 'period'
        ? searchKey(tableData[0])
        : savedAnalysisAggregation.main.toLowerCase().indexOf('all') === -1
        ? savedAnalysisAggregation.sub
        : undefined;

    if (key !== undefined) {
      setSelectedRow(
        v.map((i) => tableData[i][key]).filter((j) => j !== 'NaT'),
      );
    } else {
      setSelectedRow(['all']);
    }
  };

  return (
    <ReactTable
      columns={columnData}
      data={rowData}
      disableSelectRows={!selectRow}
      func={changeSelectedRow}
    />
  );
};

AnalysisTableComponent.displayName = 'TableComponent';
AnalysisTableComponent.propTypes = {
  tableOrder: PropTypes.array.isRequired,
  tableData: PropTypes.array.isRequired,
  selectRow: PropTypes.bool.isRequired,
  func: PropTypes.func,
};

export default AnalysisTableComponent;
