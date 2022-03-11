import { createSlice } from '@reduxjs/toolkit';
const initialState = {
  Summary: {
    yAxis: [],
    column: '',
    dataSource: '',
    subItem: '',
    args: '',
  },
  Detail: {
    yAxis: [],
    selectedOptions: [],
    column: '',
    dataSource: '',
  },
};
const AnalysisInfo = createSlice({
  name: 'AnalysisInfo',
  initialState,
  reducers: {
    initAnalysisReducer: () => initialState,
    DetailYAxiosReducer: (state, action) => {
      state.Detail.yAxis = action.payload;
    },
    SummaryYAxiosReducer: (state, action) => {
      state.Summary.yAxis = action.payload;
    },
    SummaryHeaderReducer: (state, action) => {
      state.Summary.column = action.payload;
    },
    SummaryDataReducer: (state, action) => {
      state.Summary.dataSource = action.payload;
    },
    SummarySubMenuReducer: (state, action) => {
      state.Summary.subItem = action.payload;
    },
    SummaryArgsReducer: (state, action) => {
      state.Summary.args = action.payload;
    },
    DetailHeaderReducer: (state, action) => {
      state.Detail.column = action.payload;
    },
    DetailDataReducer: (state, action) => {
      state.Detail.dataSource = action.payload;
    },
    DetailOptionReducer: (state, action) => {
      state.Detail.selectedOptions = action.payload;
    },
  },
});

//reducer's action
export const {
  initAnalysisReducer: initAnalysisAction,
  SummaryHeaderReducer,
  SummaryDataReducer,
  SummaryYAxiosReducer,
  DetailHeaderReducer,
  DetailDataReducer,
  DetailYAxiosReducer,
  DetailOptionReducer,
  SummarySubMenuReducer,
  SummaryArgsReducer,
} = AnalysisInfo.actions;

export const AnalysisSummaryData = (state) => state.AnalysisInfo.Summary;
export const AnalysisSummarySubItemData = (state) =>
  state.AnalysisInfo.Summary.subItem;
export const AnalysisDetailData = (state) => state.AnalysisInfo.Detail;

export default AnalysisInfo.reducer;
