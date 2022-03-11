import { useRef, useEffect } from 'react';
import Plotly from 'plotly.js-dist';

const filterAxisData = (rows, keys, isMulti) => {
  let tmpX = {};
  let result = {
    x: {},
    y: {},
    z: [],
  };

  if (
    (isMulti &&
      Object.keys(rows).every((v) => Object.values(rows[v]).length === 0)) ||
    Object.keys(rows).length === 0
  )
    return result;

  const checkData = (d, k) => {
    return (
      (d['No.'] === undefined || d['No.'] !== 'ALL') &&
      (d['period'] === undefined || d['period'] !== 'NaT') &&
      (d['log_time'] === undefined || d['log_time'] !== 'NaT') &&
      d[k]
    );
  };

  Object.keys(rows).forEach((v) => {
    if (isMulti) {
      if (keys.x !== '' && keys.x !== '0' && keys.x !== null) {
        let isValid = false;

        if (keys.y.length > 0) {
          let i = 0;
          while (i < keys.y.length) {
            if (keys.y[i][0] === v) {
              isValid = true;
              break;
            }
            i++;
          }
        }

        if (
          !isValid &&
          keys.z !== '' &&
          keys.z !== '0' &&
          keys.z !== null &&
          keys.z.length > 1 &&
          keys.z[0] === v
        ) {
          isValid = true;
        }

        if (isValid) {
          Object.values(rows[v]).reduce((acc, x, i) => {
            acc[i] = {
              ...acc[i],
              [v]: x,
            };
            return acc;
          }, tmpX);
        }
      } else {
        Object.values(rows[v]).forEach((x) => {
          if (keys.y.length > 0) {
            keys.y.forEach((z) => {
              if (v === z[0] && checkData(x, z[1])) {
                const currentArr = result.y[z.join('_')] ?? [];
                result = {
                  ...result,
                  y: {
                    ...result.y,
                    [z.join('_')]: [...currentArr, x[z[1]]],
                  },
                };
              }
            });
          }

          if (keys.z.length > 1) {
            if (v === keys.z[0] && checkData(x, keys.z[1])) {
              result = {
                ...result,
                z: [...result.z, x[keys.z[1]]],
              };
            }
          }
        });
      }
    } else {
      const checkZ =
        keys.z !== '' && keys.z !== '0' && keys.z !== null
          ? checkData(rows[v], keys.z)
          : false;

      if (keys.y.length > 0) {
        keys.y.forEach((x) => {
          if (checkData(rows[v], x)) {
            const currentYarr = result.y[x] ?? [];
            const currentXarr = result.x[x] ?? [];
            result =
              keys.x !== '' && keys.x !== '0' && keys.x !== null
                ? {
                    ...result,
                    x: {
                      ...result.x,
                      [x]: [...currentXarr, rows[v][keys.x]],
                    },
                    y: {
                      ...result.y,
                      [x]: [...currentYarr, rows[v][x]],
                    },
                  }
                : {
                    ...result,
                    y: {
                      ...result.y,
                      [x]: [...currentYarr, rows[v][x]],
                    },
                  };
          }
        });
      }

      if (checkZ) {
        result = {
          ...result,
          z: [...result.z, rows[v][keys.z]],
        };
      }
    }
  });

  Object.keys(tmpX).forEach((v) => {
    if (keys.y.length > 0) {
      keys.y.forEach((x) => {
        const currentData = tmpX[v][x[0]];
        if (currentData !== undefined && checkData(currentData, x[1])) {
          const currentYarr = result.y[x.join('_')] ?? [];
          const currentXarr = result.x[x.join('_')] ?? [];
          result =
            keys.x !== '' && keys.x !== '0' && keys.x !== null
              ? {
                  ...result,
                  x: {
                    ...result.x,
                    [x.join('_')]: [...currentXarr, currentData[keys.x]],
                  },
                  y: {
                    ...result.y,
                    [x.join('_')]: [...currentYarr, currentData[x[1]]],
                  },
                }
              : {
                  ...result,
                  y: {
                    ...result.y,
                    [x.join('_')]: [...currentYarr, currentData[x[1]]],
                  },
                };
        }
      });
    }

    if (
      keys.z !== '' &&
      keys.z !== '0' &&
      keys.z !== null &&
      keys.z.length > 1
    ) {
      const currentData = tmpX[v][keys.z[0]];
      if (currentData !== undefined && checkData(currentData, keys.z[1])) {
        result = {
          ...result,
          z: [...result.z, currentData[keys.z[1]]],
        };
      }
    }
  });
  return result;
};

export const createAxisData = (rows, keys, type, isMulti) => {
  let newRows = {};

  if (type === 'step' && isMulti) {
    rows.forEach((v) => {
      const newKey = Object.keys(v)[0];
      newRows[newKey] = v[newKey];
    });
  } else {
    newRows = rows;
  }

  if (Object.keys(newRows).length === 0) {
    return {
      xaxisData: [],
      yaxisData: {},
      zaxisData: [],
    };
  }

  const { x, y, z } = filterAxisData(newRows, keys, isMulti);

  return {
    xaxisData: x,
    yaxisData: y,
    zaxisData: z,
  };
};

export const drawGraph = (rows, item, ref, type, index) => {
  const currentInfo = ref.graph_list.find((v) => v.name === item.type[0]);
  const currentScript = ref.function_graph_type.find((x) => {
    return currentInfo.type === 'user'
      ? x.name === currentInfo.name
      : x.type === currentInfo.type;
  }).script;
  const newFunc = new Function('return ' + currentScript)();
  const { xaxisData, yaxisData, zaxisData } = createAxisData(
    rows,
    {
      x: item.x_axis,
      y: item.y_axis,
      z: item.z_axis,
    },
    type,
    Array.isArray(item.y_axis[0]),
  );

  const params = {
    type: item.type,
    x: xaxisData,
    y: yaxisData,
    z: zaxisData,
    title: item.title,
    range: {
      x: item.x_range_min !== '' ? [item.x_range_min, item.x_range_max] : [],
      y: item.y_range_min !== '' ? [item.y_range_min, item.y_range_max] : [],
      z: item.z_range_min !== '' ? [item.z_range_min, item.z_range_max] : [],
    },
  };
  newFunc(Plotly, document.getElementById(`${type}_graph_${index}`), params);
};

export const usePrevious = (v) => {
  const ref = useRef();

  useEffect(() => {
    ref.current = v;
  });

  return ref.current;
};
