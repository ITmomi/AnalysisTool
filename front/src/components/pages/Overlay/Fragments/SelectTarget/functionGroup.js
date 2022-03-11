import dayjs from 'dayjs';
import { OVERLAY_CORRECTION_CATEGORY } from '../../../../../lib/api/Define/etc';
import ProcessingModal from '../ProcessingModal/ProcessingModal';
import { post_Overlay_Analysis } from '../../../../../lib/api/axios/useOverlayRequest';
import { displayNotification } from '../../../JobAnalysis/functionGroup';

export const createTreeSelectData = (data, key, type) => {
  if (Object.keys(data).length === 0 || key === '') return [];

  const findOrgData = key === 'all' ? data : data[key];
  let tmpData = [
    {
      title: 'ALL',
      value: '0',
      key: '0',
      children: [],
    },
  ];

  const createArrayType = (obj) => {
    return Object.keys(obj).filter(
      (v) =>
        (Array.isArray(obj[v]) && obj[v].length > 0) || !Array.isArray(obj[v]),
    );
  };

  Object.keys(findOrgData).forEach((v) => {
    if (
      (type === 'adc' && v !== 'selected') ||
      (type === 'lot' && findOrgData[v].length > 0) ||
      type === 'stage'
    ) {
      tmpData[0].children.push(
        type === 'lot'
          ? {
              title: v,
              value: `0-${v}`,
              key: `0-${v}`,
              children: findOrgData[v].map((x) => {
                return {
                  title: x,
                  value: `0-${v}-${x}`,
                  key: `0-${v}-${x}`,
                };
              }),
            }
          : type === 'adc'
          ? {
              title: v,
              value: `0-${v}`,
              key: `0-${v}`,
            }
          : {
              title: v,
              value: `0-${v}`,
              key: `0-${v}`,
              children:
                createArrayType(findOrgData[v]).length > 0
                  ? createArrayType(findOrgData[v]).map((x) => {
                      return {
                        title: x,
                        value: `0-${v}-${x}`,
                        key: `0-${v}-${x}`,
                        children:
                          createArrayType(findOrgData[v][x]).length > 0
                            ? createArrayType(findOrgData[v][x]).map((y) => {
                                return {
                                  title: y,
                                  value: `0-${v}-${x}-${y}`,
                                  key: `0-${v}-${x}-${y}`,
                                };
                              })
                            : [],
                      };
                    })
                  : [],
            },
      );
    }
  });

  return tmpData;
};

export const createInitTreeValues = (data, type, key) => {
  const selectValues = [];

  if (Object.keys(data).length > 0) {
    Object.keys(data).forEach((v) => {
      let initValue = '0';
      if (type !== 'adc_correction') {
        Object.keys(data[v]).forEach((x) => {
          if (data[v][x]) {
            selectValues.push(`${initValue}-${v}-${x}`);
          }
        });
      } else {
        if (key === v) {
          Object.keys(data[v]).forEach((z) => {
            const isSelected = Object.keys(data[v]).find((w) => data[v][w]);
            if (isSelected && data[v][z] && z !== 'selected') {
              selectValues.push(`${initValue}-${z}`);
            }
          });
        }
      }
    });
  }

  return selectValues;
};

export const createPostData = (data, category) => {
  let result = {
    category: category,
    rid: data.source_info.files_rid,
    fab_nm: data.targetInfo.fab_name,
    period: data.targetInfo.selected.join('~'),
    job: data.targetInfo.job,
    lot_id: data.targetInfo.lot_id.map((v) => {
      if (v.match(/LOTID/)) {
        return v.substr(v.indexOf('LOTID'));
      } else {
        const splitStr = v.split('-');
        return splitStr[splitStr.length - 1];
      }
    }),
    mean_dev_diff:
      data.targetInfo.mean_dev_diff.length > 0
        ? data.targetInfo.mean_dev_diff.map((v) => Number(v))
        : [],
    ae_correction: data.targetInfo.ae_correction,
  };

  const createCorrectionComponent = (options, selected, i, key) => {
    let result = {};

    Object.keys(options).forEach((v) => {
      let tmpObj = {};

      if (key) {
        tmpObj['selected'] = key === v;
      }

      Object.keys(options[v]).forEach((x) => {
        const findKey = selected.find((y) => y.split('-')[i] === x);

        if (x !== 'selected') {
          tmpObj[x] =
            key === undefined
              ? findKey !== undefined
              : tmpObj['selected'] && findKey !== undefined;
        }
      });

      result = {
        ...result,
        [v]: tmpObj,
      };
    });

    return result;
  };

  if (category === OVERLAY_CORRECTION_CATEGORY) {
    result = {
      ...result,
      correction_component: {
        stage_correction: createCorrectionComponent(
          data.targetInfo.stage_correction_list,
          data.targetInfo.stage_correction,
          2,
          undefined,
        ),
        adc_correction: data.targetInfo.adc_correction_list,
      },
    };
  }

  return result;
};

export const disabledDate = (date, v) => {
  return date[0] === ''
    ? false
    : v &&
        (dayjs(v).isBefore(dayjs(date[0]), 'd') ||
          dayjs(v).isAfter(dayjs(date[1]), 'd'));
};

export const initStageAdcInfo = (adc, stage) => {
  let findKey = undefined;

  if (adc) {
    Object.keys(adc).forEach((v) => {
      if (Object.keys(adc[v]).find((x) => (x === 'selected') === adc[v][x])) {
        findKey = v;
      }
    });
  }

  return {
    radio: findKey,
    adc: adc ? createInitTreeValues(adc, 'adc_correction', findKey) : undefined,
    stage: stage
      ? createInitTreeValues(stage, 'stage_correction', undefined)
      : undefined,
  };
};

export const startDisableCheck = (cat, data) => {
  if (data.fab_name === '') {
    return true;
  }

  if (data.selected[0] === '') {
    return true;
  }

  if (data.job === '') {
    return true;
  }

  return data.lot_id.length === 0;
};

export const process_Overlay_Start = async ({
  postData,
  openModal,
  updateOriginDataSetting,
  closeModal,
  mode,
}) => {
  let isError = undefined;

  openModal(ProcessingModal, {
    title: 'Analysing',
    message: 'Analysing data',
  });

  await post_Overlay_Analysis(postData)
    .then((data) => {
      updateOriginDataSetting(data.info, mode);
    })
    .catch((e) => {
      isError = e.response.data.msg;
    })
    .finally(() => {
      closeModal(ProcessingModal);
      displayNotification({
        message: isError ? 'Error occurred' : 'Analysis Success',
        description: isError ?? 'The analysis was successful.',
        duration: 3,
        style: isError
          ? { borderLeft: '5px solid red' }
          : { borderLeft: '5px solid green' },
      });
    });
};

export const displayError = (msg) => {
  displayNotification({
    message: 'Error occurred',
    description: msg,
    duration: 3,
    style: { borderLeft: '5px solid red' },
  });
};
