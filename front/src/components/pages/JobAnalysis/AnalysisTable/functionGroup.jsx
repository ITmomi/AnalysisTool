import React from 'react';
import { Select } from 'antd';
import dayjs from 'dayjs';

export const createDataSource = (data, idx) => {
  if (data.length === 0 || Object.keys(data).length === 0) return undefined;

  const tmpArr = [];
  const dataObj =
    idx === 999999
      ? data
      : typeof idx === 'number'
      ? Object.values(data)[idx]
      : data[idx];

  Object.keys(dataObj).reduce((acc, k, i) => {
    const tmpObj = Object.assign({}, dataObj[k]);
    tmpObj['key'] = i;
    acc.push(tmpObj);
    return acc;
  }, tmpArr);

  return tmpArr;
};

export const createColumns = (data, idx) => {
  if (data.length === 0 || Object.keys(data).length === 0) return undefined;

  const tmpData = Array.isArray(data)
    ? data
    : typeof idx === 'number'
    ? Object.values(data)[idx]
    : data[idx];
  const tmpArr = [];

  tmpData.reduce((acc, v) => {
    acc.push({
      Header: v,
      accessor: (value) => (v === 'No.' ? value['No.'] : value[v]),
    });
    return acc;
  }, tmpArr);

  return tmpArr.length > 0 ? tmpArr : undefined;
};

export const initFilterValue = (arr) => {
  const tmpObj = {};
  if (Array.isArray(arr)) {
    arr.reduce((acc, v) => {
      acc[v.target] =
        v.mode === 'plural'
          ? (Array.isArray(v.selected) && v.selected[0] === null) ||
            v.selected === null
            ? undefined
            : v.selected
          : Array.isArray(v.selected)
          ? v.selected[0]
          : v.selected;
      return acc;
    }, tmpObj);
  }
  return tmpObj;
};

export const filteringData = (orgData, filter) => {
  const tmpArr = [];

  if (orgData === undefined) {
    return tmpArr;
  }

  orgData.reduce((acc, v) => {
    let isValid = true;

    Object.keys(filter).forEach((i) => {
      if (isValid) {
        if (Array.isArray(filter[i])) {
          if (filter[i].findIndex((j) => v[i] === j) === -1) {
            isValid = false;
          }
        } else {
          if (filter[i] !== v[i]) {
            isValid = false;
          }
        }
      }
    });

    if (isValid) {
      acc.push(v);
    }
    return acc;
  }, tmpArr);

  return tmpArr;
};

export const createGraphData = (obj, filter, isMulti) => {
  let tmpObj = {};

  const createData = (data) => {
    const buf = {};
    let i = 0;

    Object.keys(data).reduce((acc, v) => {
      let isValid = true;

      Object.keys(filter).forEach((j) => {
        if (isValid) {
          if (Array.isArray(filter[j])) {
            if (filter[j].findIndex((k) => data[v][j] === k) === -1) {
              isValid = false;
            }
          } else {
            if (filter[j] !== data[v][j]) {
              isValid = false;
            }
          }
        }
      });

      if (isValid) {
        acc[i] = data[v];
        i++;
      }
      return acc;
    }, buf);

    return buf;
  };

  if (isMulti) {
    Object.keys(obj).forEach((v) => {
      tmpObj[v] = createData(obj[v]);
    });
  } else {
    tmpObj = createData(obj);
  }

  return tmpObj;
};

export const initPeriod = (period) => {
  return period.selected !== undefined && period.selected.length > 0
    ? [
        period.selected[0].length > 0 ? dayjs(period.selected[0]) : '',
        period.selected[1].length > 0 ? dayjs(period.selected[1]) : '',
      ]
    : ['', ''];
};

export const initAggregation = (aggregation) => {
  return aggregation === undefined
    ? {}
    : {
        main: Object.keys(aggregation).length > 0 ? aggregation.selected : '',
        sub:
          Object.keys(aggregation).length > 0
            ? aggregation.selected.toLowerCase().indexOf('all') === -1 &&
              aggregation.selected.length > 0
              ? aggregation.subItem[aggregation.selected].selected
              : ''
            : '',
      };
};

export const initColumnData = (col) => {
  return createColumns(col).map((v) => ({
    ...v,
    onHeaderCell: (c) => {
      return {
        style: {
          minWidth: c.width,
        },
      };
    },
  }));
};

export const RenderSelectOptions = (v) => {
  return (
    <Select.Option value={v} key={v}>
      {v}
    </Select.Option>
  );
};
