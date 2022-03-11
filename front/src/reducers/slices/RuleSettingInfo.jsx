import { createSlice } from '@reduxjs/toolkit';
import { MSG_LOCAL } from '../../lib/api/Define/Message';
const initialState = {
  config: [],
  func: { source_type: MSG_LOCAL },
  convert: { log_define: {}, info: [], header: [], custom: [] },
  filter: [],
  analysis: { items: [], filter_default: [], aggregation_default: {} },
  visualization: { items: [], graph_list: [], function_graph_type: [] },
};
const RuleSettingInfo = createSlice({
  name: 'RuleSettingInfo',
  initialState,
  reducers: {
    initialReducer: () => initialState,
    UpdateStepConfigReducer: (state, action) => {
      state.config = action.payload;
    },

    UpdateFuncStepReducer: (state, action) => {
      state.func = action.payload;
    },
    UpdateConvertStepInfoReducer: (state, action) => {
      state.convert = action.payload;
    },
    UpdateFilterStepInfoReducer: (state, action) => {
      state.filter = action.payload;
    },
    UpdateAnalysisStepInfoReducer: (state, action) => {
      state.analysis = action.payload;
    },
    UpdateVisualStepInfoReducer: (state, action) => {
      state.visualization = action.payload;
    },
  },
});

//reducer's action
export const {
  initialReducer: initialAction,
  UpdateStepConfigReducer,
  UpdateFuncStepReducer,
  UpdateConvertStepInfoReducer,
  UpdateFilterStepInfoReducer,
  UpdateAnalysisStepInfoReducer,
  UpdateVisualStepInfoReducer,
} = RuleSettingInfo.actions;

export const getConfigStepInfo = (state) => state.RuleSettingInfo.config;
export const getFuncStepInfo = (state) => state.RuleSettingInfo.func;
export const getConvertStepInfo = (state) => state.RuleSettingInfo.convert;
export const getFilterStepInfo = (state) => state.RuleSettingInfo.filter;
export const getAnalysisStepInfo = (state) => state.RuleSettingInfo.analysis;
export const getVisualStepInfo = (state) => state.RuleSettingInfo.visualization;

export default RuleSettingInfo.reducer;
