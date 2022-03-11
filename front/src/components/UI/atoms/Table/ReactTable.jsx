import React, { useEffect } from 'react';
import styled from '@emotion/styled';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faTable,
  faCaretSquareUp,
  faCaretSquareDown,
} from '@fortawesome/free-solid-svg-icons';
import { Input, Button, Select, Checkbox } from 'antd';
import {
  LeftOutlined,
  RightOutlined,
  DoubleLeftOutlined,
  DoubleRightOutlined,
} from '@ant-design/icons';
import {
  useTable,
  usePagination,
  useSortBy,
  useGlobalFilter,
  useRowSelect,
} from 'react-table';
import PropTypes from 'prop-types';
import useResultInfo from '../../../../hooks/useResultInfo';

const { Option } = Select;

const Styles = styled.div`
  & .number-wrapper {
    display: flex;
    align-items: center;
    column-gap: 0.3rem;
    & > span {
      width: 75px;
    }
  }
  & .pagination {
    margin-top: 0.5rem;
    text-align: center;
    & > button + button {
      margin-left: 0.5rem;
    }
  }
  & .table-wrapper {
    overflow: auto;
  }
  & .count-wrapper {
    & > svg {
      margin-right: 0.3rem;
    }
    font-weight: bold;
  }
  & .control-wrapper {
    display: flex;
    align-items: center;
    column-gap: 1rem;
    & input {
      height: 32px;
    }
    & form {
      display: flex;
      column-gap: 0.3rem;
    }
  }
  & .header-wrapper {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    min-height: 32px;
  }
  & table {
    font-size: 12px;
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    text-align: center;
    & th,
    td {
      padding: 1rem 0.5rem;
    }
    & th {
      &:not(.select-wrapper) {
        min-width: 150px;
      }
      background-color: aliceblue;
      & svg {
        margin-left: 0.3rem;
      }
    }
    & td {
      border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    }
    & tbody {
      & > tr {
        cursor: pointer;
        transition: background-color 0.2s ease-in-out;
        &:hover {
          background-color: rgba(0, 0, 0, 0.03);
        }
      }
    }
  }
`;

const ReactTable = React.memo(
  ({
    columns,
    data,
    disableFilter,
    disableSort,
    disablePagination,
    disableSelectRows,
    func,
  }) => {
    const { selectedRow } = useResultInfo();
    const {
      getTableProps,
      getTableBodyProps,
      headerGroups,
      prepareRow,
      rows,
      page,
      setGlobalFilter,
      canPreviousPage,
      canNextPage,
      pageOptions,
      pageCount,
      gotoPage,
      nextPage,
      previousPage,
      setPageSize,
      selectedFlatRows,
      state: { pageIndex, pageSize },
    } = useTable(
      { columns, data },
      useGlobalFilter,
      useSortBy,
      usePagination,
      useRowSelect,
      // eslint-disable-next-line
      hooks => {
        if (!disableSelectRows) {
          hooks.visibleColumns.push((columns) => [
            {
              id: 'selection',
              // eslint-disable-next-line react/display-name,react/prop-types
              Header: ({ getToggleAllRowsSelectedProps }) => (
                <>
                  <SelectRowCheckBox {...getToggleAllRowsSelectedProps()} />
                </>
              ),
              // eslint-disable-next-line react/prop-types,react/display-name
              Cell: ({ row }) => {
                // eslint-disable-next-line
                return row.original['No.'] === undefined || row.original['No.'] !== 'ALL' ? (
                  <>
                    {/* eslint-disable-next-line react/prop-types */}
                    <SelectRowCheckBox {...row.getToggleRowSelectedProps()} />
                  </>
                ) : (
                  ''
                );
              },
            },
            ...columns,
          ]);
        }
      },
    );

    useEffect(() => {
      if (!disableSelectRows) {
        const tmpArr = [],
          savedSelectedRow = Object.assign([], selectedRow);
        selectedFlatRows.reduce((acc, v) => {
          acc.push(v.original.key);
          return acc;
        }, tmpArr);
        if (
          JSON.stringify(savedSelectedRow.sort()) !==
          JSON.stringify(tmpArr.sort())
        ) {
          func(tmpArr);
        }
      }
    }, [
      JSON.stringify(Object.values(selectedFlatRows).map((v) => v.original)),
    ]);

    return (
      <Styles>
        <div className="header-wrapper">
          {!disablePagination ? (
            <div className="count-wrapper">
              <FontAwesomeIcon icon={faTable} size="lg" />
              Page {pageIndex + 1} of {pageOptions.length}
            </div>
          ) : (
            ''
          )}
          <div className="control-wrapper">
            {!disablePagination ? (
              <>
                <div className="number-wrapper">
                  <span>Go to page:</span>
                  <Input
                    type="number"
                    value={pageIndex + 1}
                    onChange={(e) => {
                      const page = e.target.value
                        ? Number(e.target.value) - 1
                        : 0;
                      gotoPage(page);
                    }}
                    style={{ width: '100px' }}
                    min="1"
                    max={pageOptions.length}
                  />
                </div>
                <div>
                  <Select
                    value={pageSize}
                    onChange={(v) => {
                      setPageSize(Number(v));
                    }}
                  >
                    {[10, 20, 30, 40, 50].map((pageSize) => (
                      <Option key={pageSize} value={pageSize}>
                        Show {pageSize}
                      </Option>
                    ))}
                  </Select>
                </div>
              </>
            ) : (
              ''
            )}
            {!disableFilter ? (
              <div>
                <Search onSubmit={setGlobalFilter} />
              </div>
            ) : (
              ''
            )}
          </div>
        </div>
        <div className="table-wrapper">
          <table {...getTableProps()}>
            <thead>
              {headerGroups.map((headerGroup, i) => (
                <tr {...headerGroup.getHeaderGroupProps()} key={i}>
                  {headerGroup.headers.map((column, j) => {
                    const tmpObj = disableSort
                      ? { ...column.getHeaderProps() }
                      : {
                          ...column.getHeaderProps(
                            column.getSortByToggleProps(),
                          ),
                        };
                    return (
                      <th
                        {...tmpObj}
                        key={j}
                        className={
                          column.id === 'selection' ? 'select-wrapper' : ''
                        }
                      >
                        {column.render('Header')}
                        {!disableSort ? (
                          <span>
                            {column.isSorted ? (
                              column.isSortedDesc ? (
                                <FontAwesomeIcon
                                  icon={faCaretSquareUp}
                                  size="lg"
                                />
                              ) : (
                                <FontAwesomeIcon
                                  icon={faCaretSquareDown}
                                  size="lg"
                                />
                              )
                            ) : (
                              ''
                            )}
                          </span>
                        ) : (
                          ''
                        )}
                      </th>
                    );
                  })}
                </tr>
              ))}
            </thead>
            <tbody {...getTableBodyProps()}>
              {!disablePagination
                ? page.map((row, i) => {
                    prepareRow(row);
                    return (
                      <tr {...row.getRowProps()} key={i}>
                        {row.cells.map((cell, j) => (
                          <td {...cell.getCellProps()} key={j}>
                            {cell.render('Cell')}
                          </td>
                        ))}
                      </tr>
                    );
                  })
                : rows.map((row, i) => {
                    prepareRow(row);
                    return (
                      <tr {...row.getRowProps()} key={i}>
                        {row.cells.map((cell, j) => (
                          <td {...cell.getCellProps()} key={j}>
                            {cell.render('Cell')}
                          </td>
                        ))}
                      </tr>
                    );
                  })}
            </tbody>
          </table>
        </div>
        {!disablePagination ? (
          <div className="pagination">
            <Button
              onClick={() => gotoPage(0)}
              disabled={!canPreviousPage}
              icon={<DoubleLeftOutlined />}
            />
            <Button
              onClick={() => previousPage()}
              disabled={!canPreviousPage}
              icon={<LeftOutlined />}
            />
            <Button
              onClick={() => nextPage()}
              disabled={!canNextPage}
              icon={<RightOutlined />}
            />
            <Button
              onClick={() => gotoPage(pageCount - 1)}
              disabled={!canNextPage}
              icon={<DoubleRightOutlined />}
            />
          </div>
        ) : (
          ''
        )}
      </Styles>
    );
  },
  (prevProps, nextProps) =>
    JSON.stringify(prevProps) === JSON.stringify(nextProps),
);
ReactTable.propTypes = {
  columns: PropTypes.array.isRequired,
  data: PropTypes.array.isRequired,
  disableFilter: PropTypes.bool,
  disableSort: PropTypes.bool,
  disablePagination: PropTypes.bool,
  disableSelectRows: PropTypes.bool,
  func: PropTypes.func,
};
ReactTable.defaultProps = {
  disableFilter: false,
  disableSort: false,
  disablePagination: false,
  disableSelectRows: false,
};

const Search = ({ onSubmit }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(e.target.elements.filter.value);
  };

  return (
    <form onSubmit={handleSubmit}>
      <Input name="filter" type="text" />
      <Button type="primary" htmlType="submit">
        Search
      </Button>
    </form>
  );
};
Search.propTypes = {
  onSubmit: PropTypes.func.isRequired,
};

const SelectRowCheckBox = React.forwardRef(
  ({ indeterminate, ...rest }, ref) => {
    const defaultRef = React.useRef();
    const resolvedRef = ref || defaultRef;

    useEffect(() => {
      resolvedRef.current.indeterminate = indeterminate;
    }, [resolvedRef, indeterminate]);

    return (
      <>
        <Checkbox ref={resolvedRef} {...rest} />
      </>
    );
  },
);
SelectRowCheckBox.propTypes = {
  indeterminate: PropTypes.bool,
};
SelectRowCheckBox.displayName = 'SelectRowCheckBox';

export default ReactTable;
