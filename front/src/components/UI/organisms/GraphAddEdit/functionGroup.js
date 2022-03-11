import { getParseData } from '../../../../lib/util/Util';
import { GraphDateRegex } from '../../../../lib/util/RegExp';

export const compareErrorCheck = (min, max) => {
  if (min.toString().length === 0 && max.toString().length === 0) return false;
  const parseMin =
    typeof min === 'number'
      ? min
      : min.indexOf('.') !== -1
      ? parseFloat(min)
      : parseInt(min);
  const parseMax =
    typeof max === 'number'
      ? max
      : max.indexOf('.') !== -1
      ? parseFloat(max)
      : parseInt(max);

  return isNaN(parseMin) || isNaN(parseMax) ? true : parseMax <= parseMin;
};

export const createSampleData = (type, data, isSingle) => {
  let tmpData;
  if (type === 'step') {
    if (data?.row ?? false) {
      tmpData = Array.isArray(data.row)
        ? data.row.map((o) => getParseData(o).value?.[0] ?? {})
        : Object.values(data.row)[0];
    }
  } else {
    if (type !== 'analysis' || isSingle) {
      tmpData = Object.values(data)[0];
    } else {
      const mergeObj = {};

      Object.keys(data).forEach((v) => {
        mergeObj[v] = data[v][0] ? data[v][0] : {};
      });

      tmpData = mergeObj;
    }
  }
  return tmpData;
};

export const boxPlotExceptionCheck = (type, sampleData, key) => {
  if (type === 'step') {
    const checkData = Array.isArray(sampleData)
      ? sampleData[0][key]
      : sampleData[key];
    return GraphDateRegex.test(checkData);
  } else {
    if (type !== 'analysis' || Array.isArray(sampleData)) {
      return GraphDateRegex.test(sampleData[key]);
    } else {
      let isValid = true,
        i = 0;

      while (i < Object.keys(sampleData).length) {
        if (!GraphDateRegex.test(Object.values(sampleData)[i][key])) {
          isValid = false;
          break;
        }
        i++;
      }
      return isValid;
    }
  }
};

export const createYvalue = (data, type, selectedList) => {
  if (!Array.isArray(selectedList[0])) return selectedList;

  const result = [];

  selectedList.reduce((acc, v) => {
    if (v.length > 1) {
      acc.push(v);
    } else {
      const dispGraph =
        type === 'step'
          ? data.find((x) => Object.keys(x)[0] === v[0])[v[0]].disp_graph
          : data[v[0]];
      dispGraph.forEach((y) => {
        acc.push([v[0], y]);
      });
    }

    return acc;
  }, result);

  return result;
};

export const createYZoptionList = (data) => {
  if (Array.isArray(data)) {
    return data;
  } else {
    const optionList = [];

    Object.keys(data).reduce((acc, v) => {
      acc.push({
        value: v,
        label: v,
        children: Object.values(data[v]).map((val) => {
          return {
            value: val,
            label: val,
          };
        }),
      });
      return acc;
    }, optionList);

    return optionList;
  }
};
