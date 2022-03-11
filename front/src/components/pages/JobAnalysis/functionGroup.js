import { notification } from 'antd';
import { jsonToCSV } from '../../../lib/util/plotly-test';
import Plotly from 'plotly.js';
import { GraphDateRegex } from '../../../lib/util/RegExp';

const getTableData = (row, column) => {
  const jsonArr = [];
  Object.keys(row).reduce((accMain, v) => {
    const tmpObj = {};
    column.reduce((accSub, i) => {
      Object.assign(accSub, { [i]: row[v][i] });
      return accSub;
    }, tmpObj);
    accMain.push(tmpObj);
    return accMain;
  }, jsonArr);
  return jsonToCSV(jsonArr);
};

export const createExportTableData = (rows, columns, key, form) => {
  if (Array.isArray(columns)) {
    form.append(
      'files',
      new File([getTableData(rows, columns)], `${key}.table.csv`),
    );
  } else {
    Object.keys(rows).forEach((v) => {
      if (Object.keys(rows[v]).length > 0) {
        form.append(
          'files',
          new File(
            [getTableData(rows[v], columns[v])],
            `${key}.${v}_table.csv`,
          ),
        );
      }
    });
  }
};

export const createGraphImage = async () => {
  const imgArr = [];
  const components = document.querySelectorAll('div[class^="js-plotly-plot"]');

  for (let i = 0; i < components.length; i++) {
    const data = components[i];
    const title = components[i].querySelector('text[class^="gtitle"]')
      .innerHTML;
    const nameHeader = components[i].id.split('_')[0];

    await Plotly.toImage(data, {
      format: 'png',
      filename: `graph_${title}_${i}`,
    }).then((url) => {
      imgArr.push({
        url: url,
        filename: `${nameHeader}.${title}_${i}.png`,
      });
    });
  }

  return imgArr;
};

export const displayNotification = (args) => {
  notification.open(args);
};

export const createGraphItems = (data) => {
  const newItems = [];

  if (data.items.length > 0) {
    data.items.reduce((acc, v) => {
      let newData = { ...v };
      if (newData.y_axis[0].match(/[/]/)) {
        newData.y_axis = [...newData.y_axis.map((x) => x.split('/'))];
      }
      acc.push(newData);
      return acc;
    }, newItems);
  }

  return newItems;
};

const checkInnerData = (data) => {
  let i = 0,
    isSingle = false;

  while (i < Object.values(data).length) {
    if (Array.isArray(Object.values(data)[i])) {
      isSingle = true;
      break;
    }
    i++;
  }
  return isSingle;
};

export const createAnalysisData = (type, data, key) => {
  if (data === undefined || Object.keys(data).length === 0) return {};

  if (type.match(/multi/)) {
    const tmpData = {};

    if (!checkInnerData(data)) {
      Object.keys(data).forEach((v) => {
        tmpData[v] = data[v][key];
      });
      return tmpData;
    }
  }
  return data[key];
};

export const searchKey = (data) => {
  let tmpKey = Object.keys(data).find((v) => v === 'period')
    ? 'period'
    : undefined;

  if (tmpKey === undefined) {
    Object.keys(data).forEach((x) => {
      if (GraphDateRegex.test(data[x])) {
        tmpKey = x;
      }
    });
  }
  return tmpKey;
};

export const createHistoryInfo = (data) => {
  let result = data.list
    ? data.list
    : {
        rid: data.job_id,
      };

  if (data.list === undefined) {
    switch (data.job_type) {
      case 'remote':
        result = {
          ...result,
          equipment_name: data.equipment_name,
          db_id: data.db_id,
        };
        break;

      case 'sql':
        result = {
          ...result,
          db_id: data.db_id,
          sql: data.sql,
        };
        break;

      case 'script':
        result = {
          ...result,
          db_id: data.db_id,
          equipment_name: data.equipment_name,
          sql: data.sql,
        };
        break;

      default:
        break;
    }
  }

  return result;
};
