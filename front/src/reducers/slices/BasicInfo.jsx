import { createSlice } from '@reduxjs/toolkit';
import { MAIN } from '../../lib/api/Define/URL';
const initialState = {
  path: [MAIN],
  supportUrl: [],
  menuInfo: '',
  version: '',
  mgmtInfo: [],
  categories: [],
};
const BasicInfo = createSlice({
  name: 'BasicInfo',
  initialState,
  reducers: {
    initialBasicReducer: () => initialState,
    UpdateCurrentPathReducer: (state, action) => {
      state.path = action.payload;
    },
    UpdateSupportJobUrlReducer: (state, action) => {
      state.supportUrl = action.payload;
    },
    UpdateMgmtInfoReducer: (state, action) => {
      const Object = {
        target: action.payload.target,
        title: action.payload.title,
        items: action.payload.items,
      };
      const existObj = state.mgmtInfo.find(
        (obj) => obj.target === Object.target,
      );
      return {
        ...state,
        mgmtInfo:
          existObj === undefined
            ? [...state.mgmtInfo, Object]
            : state.mgmtInfo.map((obj) =>
                obj.target === Object.target ? Object : obj,
              ),
      };
    },
    UpdateVersionInfoReducer: (state, action) => {
      state.version = action.payload;
    },
    UpdateMenuInfoReducer: (state, action) => {
      state.menuInfo = action.payload;
    },
    UpdateCategoriesReducer: (state, action) => {
      state.categories = action.payload;
    },
  },
});

//reducer's action
export const {
  initialBasicReducer: initialCommonAction,
  UpdateCurrentPathReducer,
  UpdateSupportJobUrlReducer,
  UpdateMgmtInfoReducer,
  UpdateVersionInfoReducer,
  UpdateMenuInfoReducer,
  UpdateCategoriesReducer,
} = BasicInfo.actions;

export const getCurrentPath = (state) => state.BasicInfo.path;
export const getSupportUrl = (state) => state.BasicInfo.supportUrl;
export const getVersionInfo = (state) => state.BasicInfo.version;
export const getMenuInfo = (state) => state.BasicInfo.menuInfo;
export const getMgmtInfo = (state) => state.BasicInfo.mgmtInfo;
export const getCategories = (state) => state.BasicInfo.categories;

export default BasicInfo.reducer;
