import { createSlice } from '@reduxjs/toolkit';
const initialState = {
  period: { start: 0, end: 0 },
};
const SettingInfo = createSlice({
  name: 'SettingInfo',
  initialState,
  reducers: {
    initialSettingReducer: () => initialState,
    UpdateDurationReducer: (state, action) => {
      state.period = action.payload;
    },
  },
});

//reducer's action
export const {
  initialSettingReducer: initialSettingAction,
  UpdateDurationReducer,
} = SettingInfo.actions;

export const getValidPeriod = (state) => state.SettingInfo.period;

export default SettingInfo.reducer;
