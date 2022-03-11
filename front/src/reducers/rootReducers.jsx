import { combineReducers } from '@reduxjs/toolkit';
import AnalysisInfo from './slices/AnalysisInfo';
import SettingInfo from './slices/SettingInfo';
import BasicInfo from './slices/BasicInfo';
import RuleSettingInfo from './slices/RuleSettingInfo';
import ResultInfo from './slices/ResultInfo';
import OverlayInfo from './slices/OverlayInfo';

const rootReducer = combineReducers({
  AnalysisInfo,
  SettingInfo,
  BasicInfo,
  RuleSettingInfo,
  ResultInfo,
  OverlayInfo,
});

export default rootReducer;
