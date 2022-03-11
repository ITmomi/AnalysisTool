import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Select, Empty } from 'antd';
import HeaderSetting from './Fragments/HeaderSetting';
import AnalysisTableComponent from './Fragments/TableComponent';
import * as sg from './styleGroup';
import * as fn from './functionGroup';

const AnalysisTable = ({
  period,
  filter,
  aggregation,
  tableOrder,
  tableData,
  type,
  onLoad,
  useUpdate,
  detailType,
}) => {
  const [currentColumn, setCurrentColumn] = useState(undefined);
  const [currentRow, setCurrentRow] = useState(undefined);
  const [currentTable, setCurrentTable] = useState(undefined);

  const changeTable = (v) => {
    setCurrentTable(v);
    setCurrentColumn(fn.createColumns(tableOrder, v));
    setCurrentRow(fn.createDataSource(tableData, v));
  };

  useEffect(() => {
    setCurrentColumn(fn.createColumns(tableOrder, 0));
    setCurrentRow(
      type === 'analysis' || useUpdate
        ? fn.createDataSource(
            tableData,
            !Array.isArray(tableOrder) ? 0 : 999999,
          )
        : fn.filteringData(
            fn.createDataSource(
              tableData,
              !Array.isArray(tableOrder) ? 0 : 999999,
            ),
            fn.initFilterValue(filter),
          ),
    );
    if (!Array.isArray(tableOrder) && currentTable === undefined) {
      setCurrentTable(Object.keys(tableOrder)[0]);
    }
  }, [tableOrder, tableData]);

  return (
    <div css={sg.mainWrapper}>
      {filter !== undefined &&
      filter.length === 0 &&
      aggregation !== undefined &&
      Object.keys(aggregation).length === 0 &&
      period.start === null &&
      period.end === null &&
      period.select.length === 0 ? (
        ''
      ) : (
        <HeaderSetting
          period={period}
          filter={filter}
          aggregation={aggregation}
          type={type}
          loadingSet={onLoad}
          useUpdate={useUpdate}
        />
      )}
      {currentColumn ? (
        <div className="table-wrapper">
          <div>{type === 'analysis' ? 'Analysis Result' : 'Original Data'}</div>
          <div>
            {!Array.isArray(tableOrder) ? (
              <div className="select-wrapper">
                <span>Current table:</span>
                <Select
                  value={currentTable}
                  style={{ width: '300px', marginLeft: '0.5rem' }}
                  onChange={changeTable}
                >
                  {Object.keys(tableOrder).map(fn.RenderSelectOptions)}
                </Select>
              </div>
            ) : (
              ''
            )}
            {currentRow.length > 0 ? (
              <AnalysisTableComponent
                tableData={currentRow}
                tableOrder={currentColumn}
                selectRow={
                  type === 'analysis' && detailType.match(/setting/) !== null
                }
              />
            ) : (
              <div css={sg.emptyWrapper}>
                <Empty />
              </div>
            )}
          </div>
        </div>
      ) : (
        <div css={sg.emptyWrapper}>
          <Empty />
        </div>
      )}
    </div>
  );
};

AnalysisTable.displayName = 'AnalysisTable';
AnalysisTable.propTypes = {
  period: PropTypes.object.isRequired,
  filter: PropTypes.array.isRequired,
  aggregation: PropTypes.object,
  tableOrder: PropTypes.oneOfType([PropTypes.array, PropTypes.object])
    .isRequired,
  tableData: PropTypes.object.isRequired,
  type: PropTypes.string.isRequired,
  onLoad: PropTypes.func,
  useUpdate: PropTypes.bool.isRequired,
  detailType: PropTypes.string,
};

export default AnalysisTable;
