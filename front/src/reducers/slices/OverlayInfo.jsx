import { createSlice } from '@reduxjs/toolkit';
import { MSG_LOCAL, MSG_X, MSG_Y } from '../../lib/api/Define/Message';
import { V_OFF } from '../../lib/api/Define/etc';
import { getParseData } from '../../lib/util/Util';

const initialValue = {
  source: MSG_LOCAL,
  source_info: {
    files_rid: '',
    db: { id: '', name: '' },
  },
  targetInfo: {
    fab_name: '',
    fab_list: [],
    equipment_name: '',
    equipment_name_list: {},
    period: ['', ''],
    selected: ['', ''],
    job: '',
    job_list: [],
    lot_id: [],
    lot_id_list: {},
    mean_dev_diff: [],
    mean_dev_diff_list: [],
    ae_correction: V_OFF,
    stage_correction: [],
    stage_correction_list: {},
    adc_correction: [],
    adc_correction_list: {},
  },
  info: { plate: [], shot: [], origin: undefined },
};
const mapInitial = {
  column_num: undefined,
  show_extra_info: true,
  div: {
    div_upper: undefined,
    div_lower: undefined,
    scale: undefined,
  },
  display_map: {
    min: 1,
    max: 30,
  },
  plate_size: {
    size_x: undefined,
    size_y: undefined,
  },
  offset: {},
  cp_vs: {},
};
const AdcGraphInitial = {
  map: mapInitial,
  variation: {
    x_range_min: 0,
    x_range_max: 0,
    y_range_min: 0,
    y_range_max: 0,
    select_shot: 'all',
  },
  reproducibility: {
    three_sigma_x: 0,
    three_sigma_y: 0,
  },
  anova: {
    list: [MSG_X.toUpperCase(), MSG_Y.toUpperCase()],
    selected: MSG_X.toUpperCase(),
  },
};
/*const CorrectionGraphInitial = {
  image: mapInitial,
  component: mapInitial,
};*/
const initialState = {
  correction: { ...initialValue, graph: mapInitial },
  adcMeasurement: { ...initialValue, graph: AdcGraphInitial },
};
const OverlayInfo = createSlice({
  name: 'OverlayInfo',
  initialState,
  reducers: {
    initialReducer: () => initialState,
    UpdateAdcMeasurementCommonInfoReducer: (state, action) => {
      state.adcMeasurement.info = action.payload;
    },
    UpdateCorrectionCommonInfoReducer: (state, action) => {
      state.correction.info = action.payload;
    },
    UpdateAdcMeasurementInfoReducer: (state, action) => {
      state.adcMeasurement = action.payload;
    },
    UpdateCorrectionInfoReducer: (state, action) => {
      state.correction = action.payload;
    },
    UpdateMapGraphSettingReducer: (state, action) => {
      console.log('UpdateMapGraphSettingReducer', action.payload);
      state.adcMeasurement.graph.map = action.payload;
    },
    UpdateAnovaGraphSettingReducer: (state, action) => {
      state.adcMeasurement.graph.anova = action.payload;
    },
    UpdateReproducibilityGraphSettingReducer: (state, action) => {
      state.adcMeasurement.graph.reproducibility = action.payload;
    },
    UpdateVariationGraphSettingReducer: (state, action) => {
      const uValue = getParseData(action.payload);
      const cloneVariation = { ...state.adcMeasurement.graph.variation };
      return {
        ...state,
        adcMeasurement: {
          ...state.adcMeasurement,
          graph: {
            ...state.adcMeasurement.graph,
            variation: { ...cloneVariation, [uValue.id]: uValue.value },
          },
        },
      };
    },
    UpdateCorrectionMapGraphSettingReducer: (state, action) => {
      state.correction.graph = action.payload;
    },
  },
});

//reducer's action
export const {
  initialReducer: initialOverlay,
  UpdateAdcMeasurementInfoReducer,
  UpdateAdcMeasurementCommonInfoReducer,
  UpdateReproducibilityGraphSettingReducer,
  UpdateVariationGraphSettingReducer,
  UpdateCorrectionInfoReducer,
  UpdateCorrectionCommonInfoReducer,
  UpdateAnovaGraphSettingReducer,
  UpdateMapGraphSettingReducer,
  UpdateCorrectionMapGraphSettingReducer,
} = OverlayInfo.actions;

export const getCorrectionSetting = (state) => state.OverlayInfo.correction;
export const getAdcMeasurementSetting = (state) =>
  state.OverlayInfo.adcMeasurement;

export default OverlayInfo.reducer;
