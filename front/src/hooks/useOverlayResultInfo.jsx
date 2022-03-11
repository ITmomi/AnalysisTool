import { useCallback, useMemo, useState } from 'react';
import {
  E_CPVS_ADC_MEASUREMENT,
  E_CPVS_CORRECTION,
  E_OVERLAY_COMPONENT,
  E_OVERLAY_IMAGE,
  E_OVERLAY_MAP,
  OVERLAY_ADC_CATEGORY,
} from '../lib/api/Define/etc';
import {
  CP_VS_DISPLAY_OPTION,
  OVERLAY_ADC_TYPE_LIST,
  OVERLAY_CORRECTION_TYPE_LIST,
  OVERLAY_IMAGE_MAP,
  OVERLAY_OFFSET_RESET,
} from '../lib/api/Define/OverlayDefault';
import { useDispatch, useSelector } from 'react-redux';
import {
  getAdcMeasurementSetting,
  UpdateAdcMeasurementCommonInfoReducer,
  UpdateAnovaGraphSettingReducer,
  UpdateCorrectionCommonInfoReducer,
  UpdateReproducibilityGraphSettingReducer,
  UpdateVariationGraphSettingReducer,
  UpdateMapGraphSettingReducer,
  getCorrectionSetting,
  UpdateCorrectionMapGraphSettingReducer,
} from '../reducers/slices/OverlayInfo';
import { useMutation } from 'react-query';
import { QUERY_KEY } from '../lib/api/Define/QueryKey';
import {
  post_Overlay_job_FilesUpload,
  put_Overlay_etc_setting,
} from '../lib/api/axios/useOverlayRequest';
import NotificationBox from '../components/UI/molecules/NotificationBox/Notification';
import { getParseData, getTableForm } from '../lib/util/Util';

const useOverlayResult = () => {
  const [type, setType] = useState({ selected: undefined, list: [] });
  const [mode, setMode] = useState(undefined);
  const [isEtcUpdating, updateEtcSetting] = useState(false);
  const [updateDisplay, setUpdateDisplay] = useState(undefined);

  const dispatch = useDispatch();
  //------AdcMeasurement------------------------------------------------------
  const gAdcMeasurementFabName = useSelector(getAdcMeasurementSetting)
    .targetInfo.fab_name;
  const gReproducibility = useSelector(getAdcMeasurementSetting).graph
    .reproducibility;
  const gVariation = useSelector(getAdcMeasurementSetting).graph.variation;
  const gMap = useSelector(getAdcMeasurementSetting).graph.map; //
  const gAdcMeasurementInfo = useSelector(getAdcMeasurementSetting).info;
  const gAdcMeasurementData = useSelector(getAdcMeasurementSetting).info.origin;
  const gAnova = useSelector(getAdcMeasurementSetting).graph.anova;
  const gAdcMeasurementCPVS = gAdcMeasurementData?.cp_vs?.adc_measurement ?? {}; //

  //------Correction--- ---------------------------------------------------
  const gCorrectionTargetInfo = useSelector(getCorrectionSetting).targetInfo;
  const gCorrectionInfo = useSelector(getCorrectionSetting).info;
  const gCorrectionData = useSelector(getCorrectionSetting).info.origin;
  const gCorrectionMap = useSelector(getCorrectionSetting).graph;
  const gCorrectionFabName = useSelector(getCorrectionSetting).targetInfo
    .fab_name;
  const gCorrectionCPVS = gCorrectionData?.cp_vs ?? {}; //

  //-----------REDUX---FUNC UPDATE-------------------------------------------------------

  const updateReproducibilitySetting = useCallback(
    (value) => {
      dispatch(UpdateReproducibilityGraphSettingReducer(value));
    },
    [dispatch],
  );
  const updateMapSetting = useCallback(
    (value) => {
      dispatch(UpdateMapGraphSettingReducer(value));
    },
    [dispatch],
  );
  const updateVariationSetting = useCallback(
    (value) => {
      dispatch(UpdateVariationGraphSettingReducer(value));
    },
    [dispatch],
  );

  const updateAnovaSetting = useCallback(
    (value) => {
      dispatch(UpdateAnovaGraphSettingReducer(value));
    },
    [dispatch],
  );

  const updateAdcCommonInfo = useCallback(
    (data) => {
      dispatch(UpdateAdcMeasurementCommonInfoReducer(data));
    },
    [dispatch],
  );

  const updateCorrectionMapSetting = useCallback(
    (value) => {
      dispatch(UpdateCorrectionMapGraphSettingReducer(value));
    },
    [dispatch],
  );

  const updateCorrectionCommonInfo = useCallback(
    (data) => {
      dispatch(UpdateCorrectionCommonInfoReducer(data));
    },
    [dispatch],
  );
  //-----------------HOOK------------------------------------------------
  const updateResultType = useCallback(
    (e) => {
      setType({
        list:
          (e ?? mode) === OVERLAY_ADC_CATEGORY
            ? OVERLAY_ADC_TYPE_LIST
            : OVERLAY_CORRECTION_TYPE_LIST,
        selected:
          (e ?? mode) === OVERLAY_ADC_CATEGORY
            ? OVERLAY_ADC_TYPE_LIST[0]
            : OVERLAY_CORRECTION_TYPE_LIST[0],
      });
    },
    [mode],
  );

  const changeMode = (e) => {
    setMode(e);
    updateResultType(e);
  };

  const changeGraphType = (e) => {
    const findType = type.list.find((o) => o.id === e);
    if (findType !== undefined) {
      setType((prevState) => ({ ...prevState, selected: findType }));
    } else {
      console.log('not support graph type : ', e);
    }
  };

  //--------------------------------
  const stage_correction_tooltip = useMemo(() => {
    //['[DR]', 'bdc x', '', '[MY]', 'bdc y']
    const setting = gCorrectionTargetInfo.stage_correction_list;
    return Object.keys(setting).reduce((acc, key) => {
      const arr = [];
      Object.keys(setting[key]).map((key2) => {
        setting[key][key2] === true ? arr.push(key2) : '';
      });
      return [...acc, `[${key}]`, ...arr, ''];
    }, []);
  }, [gCorrectionData]);

  const adc_correction_tooltip = useMemo(() => {
    //['[ADC Measurement + Offset]' ]
    const setting = gCorrectionTargetInfo.adc_correction_list;
    const selectedKey = Object.keys(setting).find((o) => setting[o].selected);
    return selectedKey !== undefined
      ? [
          `[${selectedKey}]`,
          ...Object.keys(setting[selectedKey]).filter((o) => {
            return o !== 'selected' && setting[selectedKey][o] ? o : false;
          }),
        ]
      : [];
  }, [gCorrectionData]);

  const disp_option_cpvs = useCallback(
    (mode) => {
      const shots =
        mode === OVERLAY_ADC_CATEGORY
          ? gMap.cp_vs?.shots
          : gCorrectionMap.cp_vs?.adc_measurement?.shots ?? {};
      const shots_list = Object.keys(shots);
      return shots_list.map(
        (shotN) => CP_VS_DISPLAY_OPTION[shots[shotN].display],
      );
    },
    [gMap.cp_vs?.shots, gCorrectionMap.cp_vs?.adc_measurement?.shots],
  );

  const disp_option_correction = useMemo(() => {
    const getItems = (shots, keys, shot_num) => {
      if (shots ?? false) {
        const obj = shots?.[keys].find((o) => o.shot.id === shot_num);
        return Object.keys(obj ?? {})
          .filter((o) => o !== 'shot')
          .reduce((acc2, o) => ({ ...acc2, [o]: obj[o].checked }), {});
      }
      return {};
    };
    return gCorrectionMap.cp_vs?.correction?.shots ?? false
      ? gCorrectionInfo?.shot?.reduce((acc, shotN) => {
          const cpShot = getItems(
            gCorrectionMap.cp_vs.correction.shots,
            'cp',
            shotN,
          );
          const vsShot = getItems(
            gCorrectionMap.cp_vs.correction.shots,
            'vs',
            shotN,
          );
          return { ...acc, [shotN]: { CP: cpShot, VS: vsShot } };
        }, {}) ?? {}
      : {};
  }, [gCorrectionMap.cp_vs?.correction?.shots, gCorrectionInfo?.shot]);

  //--------------------------------
  const jobFileUpload = async (shot_list, mode, formdata) => {
    await post_Overlay_job_FilesUpload(formdata).then(({ cp_vs }) => {
      if (mode === OVERLAY_ADC_CATEGORY) {
        updateMapSetting({
          ...gMap,
          cp_vs: {
            ...gMap.cp_vs,
            shots: shot_list.reduce(
              (acc, o) =>
                Object.assign(acc, {
                  [o]: { ...gMap.cp_vs.shots[o], ...cp_vs },
                }),
              {},
            ),
          },
        });
      } else {
        updateCorrectionMapSetting({
          ...gCorrectionMap,
          cp_vs: {
            ...gCorrectionMap.cp_vs,
            adc_measurement: {
              ...gCorrectionMap.cp_vs.adc_measurement,
              shots: shot_list.reduce(
                (acc, o) =>
                  Object.assign(acc, {
                    [o]: {
                      ...gCorrectionMap.cp_vs.adc_measurement.shots[o],
                      ...cp_vs,
                    },
                  }),
                {},
              ),
            },
          },
        });
      }
    });
  };
  const BasicCPVSChangeFunc = useCallback(
    (info, type, tab) => {
      type === E_OVERLAY_MAP
        ? updateMapSetting({
            ...gMap,
            cp_vs: {
              ...gMap.cp_vs,
              mode: info?.mode ?? gMap.cp_vs.mode,
              shots: info?.shots ?? gMap.cp_vs.shots,
              preset: info?.preset ?? gMap.cp_vs.preset,
            },
          })
        : updateCorrectionMapSetting({
            ...gCorrectionMap,
            cp_vs: {
              ...gCorrectionMap.cp_vs,
              [tab]: {
                ...gCorrectionMap.cp_vs[tab],
                mode: info?.mode ?? gCorrectionMap.cp_vs[tab].mode,
                shots: info?.shots ?? gCorrectionMap.cp_vs[tab].shots,
                preset: info?.preset ?? gCorrectionMap.cp_vs[tab].preset,
              },
            },
          });
    },
    [gMap, gCorrectionMap],
  );
  const cpvsModeChangeFunc = (e, mode, tab) => {
    BasicCPVSChangeFunc(
      { mode: e.target.value },
      mode === OVERLAY_ADC_CATEGORY ? E_OVERLAY_MAP : E_OVERLAY_IMAGE,
      tab,
    );
  };
  const cpvsAdcShotChangeFunc = (e, mode) => {
    BasicCPVSChangeFunc(
      {
        shots:
          mode === OVERLAY_ADC_CATEGORY
            ? { ...gMap.cp_vs.shots, [e.shot]: e.info }
            : {
                ...gCorrectionMap.cp_vs[E_CPVS_ADC_MEASUREMENT].shots,
                [e.shot]: e.info,
              },
      },
      mode === OVERLAY_ADC_CATEGORY ? E_OVERLAY_MAP : E_OVERLAY_IMAGE,
      E_CPVS_ADC_MEASUREMENT,
    );
  };

  const cpvsCorrectionShotChangeFunc = (e, keys) => {
    BasicCPVSChangeFunc(
      {
        shots:
          keys === 'cp'
            ? {
                ...gCorrectionMap.cp_vs[E_CPVS_CORRECTION].shots,
                cp: Array.isArray(e)
                  ? e
                  : gCorrectionMap.cp_vs[E_CPVS_CORRECTION].shots.cp.map((o) =>
                      o.shot.id === e.shot.id ? e : o,
                    ),
              }
            : {
                ...gCorrectionMap.cp_vs[E_CPVS_CORRECTION].shots,
                vs: Array.isArray(e)
                  ? e
                  : gCorrectionMap.cp_vs[E_CPVS_CORRECTION].shots.vs.map((o) =>
                      o.shot.id === e.shot.id ? e : o,
                    ),
              },
      },
      OVERLAY_IMAGE_MAP,
      E_CPVS_CORRECTION,
    );
  };

  //--ETC SETTING-----------------

  const offsetChangeFunc = useCallback(
    (e, type) => {
      const data = getParseData(e);
      const set =
        type === E_OVERLAY_MAP
          ? { func: updateMapSetting, value: gMap }
          : [E_OVERLAY_IMAGE, E_OVERLAY_COMPONENT].includes(type)
          ? { func: updateCorrectionMapSetting, value: gCorrectionMap }
          : { func: undefined, value: undefined };
      if (data.id === 'mode') {
        set.func(
          data.value === 'auto'
            ? {
                ...set.value,
                offset: {
                  ...set.value.offset,
                  ...e,
                  info: set.value.offset.default,
                },
              }
            : { ...set.value, offset: { ...set.value.offset, ...e } },
        );
      } else {
        set.func({
          ...set.value,
          offset: {
            ...set.value.offset,
            info: {
              ...set.value.offset.info,
              [data.id]: { ...set.value.offset.info[data.id], ...data.value },
            },
          },
        });
      }
    },
    [gMap, gCorrectionMap],
  );

  const offsetResetFunc = useCallback(
    (type) => {
      if (type === E_OVERLAY_MAP) {
        const resetOffset = gAdcMeasurementInfo.shot.reduce(
          (acc, o) => ({ ...acc, [o]: OVERLAY_OFFSET_RESET }),
          {},
        );
        updateMapSetting({
          ...gMap,
          offset: {
            ...gMap.offset,
            info: resetOffset,
          },
        });
      } else if ([E_OVERLAY_IMAGE, E_OVERLAY_COMPONENT].includes(type)) {
        const resetOffset = gCorrectionInfo.shot.reduce(
          (acc, o) => ({ ...acc, [o]: OVERLAY_OFFSET_RESET }),
          {},
        );
        updateCorrectionMapSetting({
          ...gCorrectionMap,
          offset: {
            ...gCorrectionMap.offset,
            info: resetOffset,
          },
        });
      }
    },
    [gMap, gCorrectionMap],
  );
  const BasicChangeFunc = useCallback(
    (e, type, properties) => {
      type === E_OVERLAY_MAP
        ? updateMapSetting({
            ...gMap,
            [properties]: { ...gMap[properties], ...e },
          })
        : [E_OVERLAY_IMAGE, E_OVERLAY_COMPONENT].includes(type)
        ? updateCorrectionMapSetting({
            ...gCorrectionMap,
            [properties]: { ...gCorrectionMap[properties], ...e },
          })
        : {};
    },
    [gMap, gCorrectionMap],
  );

  const divChangeFunc = useCallback(
    (e, type) => BasicChangeFunc(e, type, 'div'),
    [BasicChangeFunc],
  );
  const displayMapChangeFunc = useCallback(
    (e, type) => BasicChangeFunc(e, type, 'display_map'),
    [BasicChangeFunc],
  );
  const plateSizeChangeFunc = useCallback(
    (e, type) => BasicChangeFunc(e, type, 'plate_size'),
    [BasicChangeFunc],
  );
  const columnNExtraInfoChangeFunc = useCallback(
    (e, type) => {
      type === E_OVERLAY_MAP
        ? updateMapSetting({ ...gMap, ...e })
        : [E_OVERLAY_IMAGE, E_OVERLAY_COMPONENT].includes(type)
        ? updateCorrectionMapSetting({ ...gCorrectionMap, ...e })
        : {};
    },
    [gMap, gCorrectionMap],
  );
  const EtcSettingUpdateMutation = useMutation(
    [QUERY_KEY.OVERLAY_ETC_SETTING_UPDATE],
    ({ obj, fab_name }) => put_Overlay_etc_setting({ obj, fab_name }),
    {
      onSuccess: () => {
        console.log('update success ');
      },
      onError: (error) => {
        NotificationBox('ERROR', error.message, 4.5);
      },
      onSettled: () => {
        updateEtcSetting(false);
      },
    },
  );

  const getAnovaTableFuc = useCallback((data) => {
    const data_value = Object.values(data);
    const disp_order = Object.keys(data_value?.[0] ?? {});
    const row = Object.keys(data).map((key, i) => ({
      ...data_value[i],
      ADC: key,
    }));
    return getTableForm({
      info: { disp_order: ['ADC'].concat(disp_order), row: row } ?? {},
    });
  }, []);

  return {
    OverlayResultType: type.selected,
    setOverlayResultType: changeGraphType,
    OverlayResultMode: mode,
    setOverlayResultMode: changeMode,
    getOverlayResultTypeList: type.list,
    gVariation,
    gMap,
    gAnova,
    gReproducibility,
    updateMapSetting,
    updateReproducibilitySetting,
    updateVariationSetting,
    updateAnovaSetting,
    updateCorrectionCommonInfo,
    updateAdcCommonInfo,
    updateCorrectionMapSetting,
    gAdcMeasurementData,
    gAdcMeasurementFabName,
    gAdcMeasurementCPVS,
    gCorrectionCPVS,
    gCorrectionInfo,
    gCorrectionFabName,
    isEtcUpdating, //etc setting
    updateEtcSetting, //etc setting
    gCorrectionData,
    gCorrectionMap,
    offsetChangeFunc,
    offsetResetFunc,
    divChangeFunc,
    displayMapChangeFunc,
    plateSizeChangeFunc,
    columnNExtraInfoChangeFunc,
    EtcSettingUpdateMutation,
    getAnovaTableFuc,

    cpvsModeChangeFunc,
    cpvsAdcShotChangeFunc,
    cpvsCorrectionShotChangeFunc,
    BasicCPVSChangeFunc,
    jobFileUpload,

    adc_correction_tooltip,
    stage_correction_tooltip,
    disp_option_correction,
    disp_option_cpvs,

    updateDisplay,
    setUpdateDisplay,
  };
};
export default useOverlayResult;
