export const createOptionData = (data) => {
  let result;

  if (Array.isArray(data.data)) {
    const yzList = createMultiData(data, 'disp_graph');
    result = {
      x: data.visualization.common_axis_x,
      y: yzList,
      z: yzList,
    };
  } else {
    result = {
      x: data?.disp_order ?? [],
      y: data?.disp_graph ?? [],
      z: data?.disp_graph ?? [],
    };
  }

  return result;
};

export const createMultiData = (data, key) => {
  if (!Array.isArray(data.data)) return data[key];

  let result = {};

  data.data.reduce((acc, v) => {
    const innerKey = Object.keys(v)[0];
    Object.assign(acc, {
      [innerKey]: v[innerKey][key],
    });
    return acc;
  }, result);

  return result;
};
