export const getParseData = (obj) => {
  const item = getParseJsonData(obj);
  return item[0];
};

export const getParseJsonData = (obj) => {
  let item = {};
  if (obj)
    item = Object.entries(obj).map(([key, val]) => ({
      id: key,
      value: val,
    }));
  return item;
};

export const arrayShift = (arr) => {
  const cPath = arr.slice();
  console.log('[arr]', cPath.shift());
  return cPath;
};

export const arrayUnshift = (arr, item) => {
  const cPath = arr.slice();
  console.log('[arr]', cPath.unshift(item));
  return cPath;
};

export const arrayRemove = (arr, item) => {
  const cIndex = arr.indexOf(item);
  const cPath = arr.slice(cIndex);
  console.log('[arr]', cPath);
  return cPath;
};

export const sortArrayOfObjects = (arr, key) => {
  return arr.sort((a, b) => {
    return a[key] - b[key];
  });
};

export const getFileName = (items) => {
  if (items === null) return null;
  for (const values of items.values()) {
    return values.name;
  }
};
export const getFileType = (items) => {
  if (items === null) return null;
  for (const values of items.values()) {
    return values.type;
  }
};

export const getFormdataFiles = (items) => {
  if (items === null) return null;

  for (let value of items.values()) {
    console.log(value);
  }
  return items.get('files');
};

export const getArray = (list, col_idx, disp_order) => {
  console.log('getArray', list);
  console.log('col_idx', col_idx);
  return list.map((obj, idx) => {
    const tmp = Object.assign(
      {},
      obj,
      col_idx
        ? disp_order
          ? { disp_order: idx, col_index: idx + 1 }
          : { index: idx, col_index: idx + 1 }
        : disp_order
        ? { disp_order: idx }
        : { index: idx },
    );
    delete tmp['key'];
    delete tmp['rec_type'];
    delete tmp['output_column_val'];
    return tmp;
  });
};

//For StepSetting's Preview
export const getTableForm = ({ info, max_row }) => {
  const { disp_order, row } = info;
  const header_data = disp_order.map((item) => ({
    ['title']: item,
    ['dataIndex']: `data_${item}`,
    ['key']: `data_${item}`,
  }));
  const row_data = Object.entries(row ?? [])
    .map((item, i) => {
      const obj = { ['key']: `${i}` };
      Object.entries(item[1]).map(([idx, value]) => {
        Object.assign(obj, { [`data_${idx}`]: value });
      });
      return obj;
    })
    .filter((_, idx) => (max_row === undefined ? true : idx < max_row));
  return { columns: header_data, dataSource: row_data };
};

export const getFindData = (stepData, target, value) => {
  const data = stepData
    ?.map((obj) => {
      return obj.items
        .map((obj2) => {
          return obj2?.subItem?.target === target
            ? obj2?.subItem?.selected ?? undefined
            : obj2?.target === target
            ? obj2?.selected ??
              obj2?.content ??
              obj2.value ??
              obj2?.[value ?? obj2.target] ??
              undefined
            : undefined;
        })
        .filter((obj) => obj !== undefined);
    })
    .filter((obj) => obj.length > 0);
  return Array.isArray(data)
    ? Array.isArray(data?.[0])
      ? data?.[0][0]
      : data?.[0]
    : data ?? undefined;
};

export const characterRange = (size, startChar) => {
  const range = (size, start) =>
    [...Array(size).keys()].map((key) => key + start);
  return String.fromCharCode(...range(size, startChar.charCodeAt(0)));
};
export const rand = (min, max) => {
  return Math.floor(Math.random() * (max - min)) + min;
};
