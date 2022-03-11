import { useDispatch, useSelector } from 'react-redux';
import {
  getAdcMeasurementSetting,
  getCorrectionSetting,
  initialOverlay,
  UpdateAdcMeasurementInfoReducer,
  UpdateCorrectionInfoReducer,
} from '../reducers/slices/OverlayInfo';
import { useCallback } from 'react';
import {
  OVERLAY_ADC_CATEGORY,
  OVERLAY_CORRECTION_CATEGORY,
} from '../lib/api/Define/etc';
import useOverlayResultInfo from './useOverlayResultInfo';
import { CPVS_MODE } from '../lib/api/Define/OverlayDefault';
import { createPostData } from '../components/pages/Overlay/Fragments/SelectTarget/functionGroup';

const useOverlayInfo = () => {
  const dispatch = useDispatch();
  const correctionSet = useSelector(getCorrectionSetting);
  const adcMeasurementSet = useSelector(getAdcMeasurementSetting);
  const {
    updateMapSetting,
    updateCorrectionMapSetting,
    updateAdcCommonInfo,
    updateCorrectionCommonInfo,
  } = useOverlayResultInfo();
  const initialOverlayInfo = useCallback(() => {
    dispatch(initialOverlay());
  }, [dispatch]);

  const updateAdcMeasurementSetting = useCallback(
    (value) => {
      dispatch(UpdateAdcMeasurementInfoReducer(value));
    },
    [dispatch],
  );
  const updateCorrectionSetting = useCallback(
    (value) => {
      dispatch(UpdateCorrectionInfoReducer(value));
    },
    [dispatch],
  );
  const getCorrectionCpVsDefault = (defaultV, shot) => {
    return getCorrectionCpVsSetting(defaultV, undefined, shot);
  };

  const getCorrectionCpVsSetting = (defaultV, Value, shot) => {
    const data = Value?.[shot[0]] ?? defaultV;
    const key_list = Object.keys(data).filter(
      (o) => !o.includes('chk') && !o.includes('mode'),
    );
    return {
      cp: shot?.map((shotN) =>
        key_list
          .filter((o) => o.includes('cp'))
          .reduce(
            (acc, o) => ({
              ...acc,
              [o]: {
                value: (defaultV ?? Value?.[shotN])?.[o],
                checked: (defaultV ?? Value?.[shotN])?.[`${o}_chk`] ?? false,
              },
            }),
            {
              shot: {
                id: shotN,
                mode: (Value?.[shotN] ?? defaultV)?.['cpmode'] ?? 'auto',
              },
            },
          ),
      ),
      vs: shot?.map((shotN) =>
        key_list
          .filter((o) => o.includes('vs'))
          .reduce(
            (acc, o) => ({
              ...acc,
              [o]: {
                value: (defaultV ?? Value?.[shotN])?.[o],
                checked: (defaultV ?? Value?.[shotN])?.[`${o}_chk`] ?? false,
              },
            }),
            {
              shot: {
                id: shotN,
                mode: (Value?.[shotN] ?? defaultV)?.['vsmode'] ?? 'auto',
              },
            },
          ),
      ),
    };
  };
  const updateOriginDataSetting = useCallback(
    (data, mode) => {
      console.log('updateOriginDataSetting START', mode);
      const lot_data = Object.values(
        mode === OVERLAY_ADC_CATEGORY ? data.data : data.data.map,
      )[0];
      const plate = Object.keys(lot_data.plate);
      const plate_data = Object.values(lot_data.plate)[0];
      const shot =
        mode === OVERLAY_ADC_CATEGORY
          ? Object.keys(plate_data.shot).map(Number)
          : data?.cp_vs?.correction?.shot ??
            data?.cp_vs?.adc_measurement?.shot ??
            Object.keys(plate_data.shot).map(Number);
      const adc_measurement_shot =
        data?.cp_vs ?? false
          ? shot.reduce(
              (acc, o) =>
                Object.assign(acc, {
                  [o]: data?.cp_vs?.adc_measurement?.default,
                }),
              {},
            )
          : {};
      if ([OVERLAY_ADC_CATEGORY, OVERLAY_CORRECTION_CATEGORY].includes(mode)) {
        //origin data  & update
        if (mode === OVERLAY_ADC_CATEGORY) {
          console.log('OVERLAY_ADC_CATEGORY START');

          //shot & plate information
          updateMapSetting(
            data?.cp_vs ?? false
              ? {
                  ...adcMeasurementSet.graph.map,
                  ...data.etc, //div, plate_size, column_num, display_map
                  offset: {
                    mode: 'auto',
                    info: data?.offset ?? {},
                    default: data?.offset,
                  },
                  cp_vs: {
                    mode:
                      data?.cp_vs?.adc_measurement?.included === true
                        ? CPVS_MODE.FROM_LOG
                        : CPVS_MODE.EACH,
                    shots: adc_measurement_shot,
                    preset: data?.cp_vs?.adc_measurement?.preset,
                  },
                }
              : {
                  ...adcMeasurementSet.graph.map,
                  offset: {
                    ...adcMeasurementSet.graph.map.offset,
                    info:
                      adcMeasurementSet.graph.map.offset.mode === 'auto'
                        ? data?.offset
                        : adcMeasurementSet.graph.map.offset.info,
                    default: data?.offset,
                  },
                },
          );
          updateAdcCommonInfo({
            shot: shot,
            plate: plate,
            origin:
              data?.cp_vs ?? false
                ? data
                : { ...adcMeasurementSet.info.origin, ...data },
          });
        } else if (mode === OVERLAY_CORRECTION_CATEGORY) {
          console.log('OVERLAY_CORRECTION_CATEGORY START');

          const correction_data = data?.cp_vs?.correction;
          const correction_cpvs =
            data?.cp_vs ?? false
              ? getCorrectionCpVsDefault(correction_data?.default, shot)
              : {};
          console.log('OVERLAY_CORRECTION_CATEGORY 1');
          updateCorrectionMapSetting(
            data?.cp_vs ?? false
              ? {
                  ...correctionSet.graph.image,
                  ...data.etc, //div, plate_size, column_num, display_map
                  offset: {
                    mode: 'auto',
                    info: data?.offset ?? {},
                    default: data?.offset,
                  },
                  cp_vs: {
                    adc_measurement: {
                      mode:
                        data?.cp_vs?.adc_measurement?.included === true
                          ? CPVS_MODE.FROM_LOG
                          : CPVS_MODE.EACH,
                      shots: adc_measurement_shot,
                      preset: data?.cp_vs?.adc_measurement?.preset,
                    },
                    correction: {
                      mode: CPVS_MODE.EACH,
                      preset: correction_data?.preset ?? {},
                      shots: correction_cpvs,
                    },
                  },
                }
              : {
                  ...correctionSet.graph,
                  offset: {
                    ...correctionSet.graph.offset,
                    info:
                      correctionSet.graph.offset.mode === 'auto'
                        ? data?.offset
                        : correctionSet.graph.offset.info,
                    default: data?.offset,
                  },
                },
          );
          updateCorrectionCommonInfo({
            shot: shot,
            plate: plate,
            origin:
              data?.cp_vs ?? false
                ? data
                : { ...correctionSet.info.origin, ...data },
          });
        }
      }
      console.log('updateOriginDataSetting END');
    },
    [
      adcMeasurementSet.graph.map,
      correctionSet.graph,
      adcMeasurementSet.info,
      correctionSet.info,
    ],
  );

  const getReAnalysisParameter = (mode, data) => {
    let postData = createPostData(data, mode);
    const adc_cp_vs_list = (cp_vs) => {
      const shots = Object.keys(cp_vs.shots);
      const shots_value = Object.values(cp_vs.shots);
      return Object.keys(shots_value[0]).reduce(
        (acc, cp) => ({
          ...acc,
          [cp]:
            cp_vs.mode === CPVS_MODE.SAME
              ? shots_value.reduce(
                  (acc2, _, i) => ({
                    ...acc2,
                    [shots[i]]: shots_value[0][cp],
                  }),
                  {},
                )
              : shots_value.reduce(
                  (acc2, o2, i) => ({ ...acc2, [shots[i]]: o2[cp] }),
                  {},
                ),
        }),
        {},
      );
    };
    const correction_cp_vs_list = (cp_vs, mode) => {
      const cpVS = Object.keys(cp_vs);
      const getCpVsValue = (cp_vs, key) => {
        return mode === CPVS_MODE.SAME
          ? {
              [key]: cp_vs.reduce(
                (acc, o) => ({ ...acc, [o.shot.id]: cp_vs[0][key].value }),
                {},
              ),
            }
          : {
              [key]: cp_vs.reduce(
                (acc, o) => ({ ...acc, [o.shot.id]: o[key].value }),
                {},
              ),
            };
      };
      return cpVS.reduce((acc, cp) => {
        const key_list = Object.keys(cp_vs?.[cp]?.[0]).filter(
          (o) => o !== 'shot',
        ); //cp1, cp12d.....
        return Object.assign(
          acc,
          key_list.reduce(
            (acc2, key2) => ({
              ...acc2,
              ...getCpVsValue(cp_vs[cp], key2, mode),
            }),
            {},
          ),
        );
      }, {});
    };
    return {
      ...postData,
      cp_vs:
        mode === OVERLAY_ADC_CATEGORY
          ? {
              use_from_log:
                data?.graph?.map?.cp_vs?.mode === CPVS_MODE.FROM_LOG,
              adc_measurement: adc_cp_vs_list(data.graph.map.cp_vs),
            }
          : {
              use_from_log:
                data?.graph?.cp_vs?.adc_measurement.mode === CPVS_MODE.FROM_LOG,
              adc_measurement: adc_cp_vs_list(
                data?.graph?.cp_vs?.adc_measurement,
              ),
              correction: correction_cp_vs_list(
                data?.graph?.cp_vs?.correction.shots,
                data?.graph?.cp_vs?.correction.mode,
              ),
            },
    };
  };
  return {
    adcMeasurementSet,
    correctionSet,
    initialOverlayInfo,
    updateAdcMeasurementSetting,
    updateCorrectionSetting,
    adcCommonInfo: adcMeasurementSet.info,
    correctionCommonInfo: correctionSet.info,
    updateOriginDataSetting,
    getCorrectionCpVsDefault,
    getCorrectionCpVsSetting,
    getReAnalysisParameter,
  };
};
export default useOverlayInfo;
