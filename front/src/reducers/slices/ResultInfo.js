import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  selectedRow: [],
  originalFilteredRows: {},
  analysisGraphInfo: [],
  originalGraphInfo: [],
  savedAnalysisAggregation: {},
  visualization: {},
  analysis: {
    type: '',
    period: {},
    filter: [],
    aggregation: {},
    dispOrder: [],
    dispGraph: [],
    data: {},
    common_axis_x: [],
  },
  original: {
    period: {},
    filter: [],
    aggregation: {},
    dispOrder: [],
    dispGraph: [],
    data: {},
    common_axis_x: [],
  },
};

const ResultInfo = createSlice({
  name: 'ResultInfo',
  initialState,
  reducers: {
    initialReducer: () => initialState,
    UpdateAnalysisReducer: (state, action) => {
      state.analysis = action.payload;
    },
    UpdateOriginalReducer: (state, action) => {
      state.original = action.payload;
    },
    UpdateSelectedRowReducer: (state, action) => {
      state.selectedRow = action.payload;
    },
    UpdateOriginalFilteredRowsReducer: (state, action) => {
      state.originalFilteredRows = action.payload;
    },
    UpdateAnalysisGraphInfoReducer: (state, action) => {
      state.analysisGraphInfo = action.payload;
    },
    UpdateSavedAnalysisAggregationReducer: (state, action) => {
      state.savedAnalysisAggregation = action.payload;
    },
    UpdateOriginalGraphInfoReducer: (state, action) => {
      state.originalGraphInfo = action.payload;
    },
    UpdateVisualizationReducer: (state, action) => {
      state.visualization = action.payload;
    },
  },
});

export const {
  initialReducer: initialAction,
  UpdateAnalysisReducer,
  UpdateOriginalReducer,
  UpdateSelectedRowReducer,
  UpdateAnalysisGraphInfoReducer,
  UpdateSavedAnalysisAggregationReducer,
  UpdateOriginalFilteredRowsReducer,
  UpdateOriginalGraphInfoReducer,
  UpdateVisualizationReducer,
} = ResultInfo.actions;

export default ResultInfo.reducer;
