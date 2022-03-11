import React from 'react';
import PropTypes from 'prop-types';
import Step6_Setting from '../Step6_Setting';
import {
  E_STEP_3,
  E_STEP_2,
  E_MULTI_TYPE,
} from '../../../../lib/api/Define/etc';
import VisualSetting from '../VisualSetting';
const addGraphButtonEvent = () => {
  console.log('[STEP4] addGraphButtonEvent');
};
const PreviewButtonEvent = () => {};
const PreviousButtonEvent = ({ funcStepInfo }) => {
  return funcStepInfo.use_org_analysis === false
    ? { step: E_STEP_3, status: 'pass' }
    : { step: E_STEP_2, status: 'pass' };
};

const EnableCheck = () => {
  return false;
};
/*============================================================================
==                         MULTI STEP 4 CONTENTS                            ==
============================================================================*/
const ContentsForm = ({ data }) => {
  return <VisualSetting type={E_MULTI_TYPE} data={data} />;
};
ContentsForm.propTypes = {
  onChange: PropTypes.func,
  data: PropTypes.object,
};
const PreviewForm = ({ type }) => {
  return <Step6_Setting.view_preview type={type} />;
};
PreviewForm.propTypes = {
  type: PropTypes.string,
};
const Step4_Multi_Setting = ({ children }) => {
  return <div>{children}</div>;
};

Step4_Multi_Setting.propTypes = {
  children: PropTypes.node,
};
Step4_Multi_Setting.btn_addGraph = addGraphButtonEvent;
Step4_Multi_Setting.btn_previous = PreviousButtonEvent;
Step4_Multi_Setting.btn_preview = PreviewButtonEvent;
Step4_Multi_Setting.check_next = EnableCheck;
Step4_Multi_Setting.check_preview = EnableCheck;
Step4_Multi_Setting.view_contents = ContentsForm;
Step4_Multi_Setting.view_preview = PreviewForm;

export default Step4_Multi_Setting;
