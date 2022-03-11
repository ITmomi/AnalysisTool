import React from 'react';
import PropTypes from 'prop-types';
import {
  E_MULTI_TYPE,
  E_SINGLE_TYPE,
  E_STEP_1,
  E_STEP_2,
  E_STEP_3,
  E_STEP_4,
  E_STEP_5,
  E_STEP_6,
} from '../../../lib/api/Define/etc';
import Step1_Setting from './Step1_Setting';
import Step2_Setting from './Step2_Setting';
import Step3_Setting from './Step3_Setting';
import Step4_Setting from './Step4_Setting';
import Step5_Setting from './Step5_Setting';
import Step6_Setting from './Step6_Setting';
import Step2_Multi_Setting from './MultiAnalysis/Step2_Setting';
import Step3_Multi_Setting from './MultiAnalysis/Step3_Setting';
import Step4_Multi_Setting from './MultiAnalysis/Step4_Setting';

/*============================================================================
==                         STEP Setting Page                                ==
============================================================================*/

const Contents = ({ current, data, changeFunc, type }) => {
  return (
    <>
      {current === E_STEP_1 ? (
        <Step1_Setting.view_contents onChange={changeFunc} />
      ) : current === E_STEP_2 ? (
        type === E_SINGLE_TYPE ? (
          <Step2_Setting.view_contents data={data} onChange={changeFunc} />
        ) : (
          <Step2_Multi_Setting.view_contents
            data={data}
            onChange={changeFunc}
          />
        )
      ) : current === E_STEP_3 ? (
        type === E_SINGLE_TYPE ? (
          <Step3_Setting.view_contents data={data} onChange={changeFunc} />
        ) : (
          <Step3_Multi_Setting.view_contents
            data={data}
            onChange={changeFunc}
          />
        )
      ) : current === E_STEP_4 ? (
        type === E_SINGLE_TYPE ? (
          <Step4_Setting.view_contents data={data} />
        ) : (
          <Step4_Multi_Setting.view_contents data={data} onChange={onchange} />
        )
      ) : current === E_STEP_5 ? (
        <Step5_Setting.view_contents data={data} onChange={changeFunc} />
      ) : current === E_STEP_6 ? (
        <Step6_Setting.view_contents data={data} />
      ) : (
        <div>{''}</div>
      )}
    </>
  );
};
Contents.propTypes = {
  current: PropTypes.number,
  data: PropTypes.object,
  changeFunc: PropTypes.func,
  type: PropTypes.string,
};

const Preview = ({ current, data, type }) => {
  return (
    <>
      {current === E_STEP_1 ? (
        <Step1_Setting.view_preview data={data} />
      ) : current === E_STEP_2 ? (
        type === E_SINGLE_TYPE ? (
          <Step2_Setting.view_preview data={data} />
        ) : (
          <Step2_Multi_Setting.view_preview data={data} type={E_MULTI_TYPE} />
        )
      ) : current === E_STEP_3 ? (
        type === E_SINGLE_TYPE ? (
          <Step3_Setting.view_preview data={data} />
        ) : (
          <Step3_Multi_Setting.view_preview data={data} />
        )
      ) : current === E_STEP_4 ? (
        type === E_SINGLE_TYPE ? (
          <Step4_Setting.view_preview data={data} />
        ) : (
          <Step4_Multi_Setting.view_preview type={type} />
        )
      ) : current === E_STEP_5 ? (
        <Step5_Setting.view_preview data={data} />
      ) : current === E_STEP_6 ? (
        <Step6_Setting.view_preview type={E_SINGLE_TYPE} />
      ) : (
        <div />
      )}
    </>
  );
};
Preview.propTypes = {
  current: PropTypes.number,
  data: PropTypes.object,
  type: PropTypes.string,
};

const StepSetting = ({ children }) => {
  return <div>{children}</div>;
};

StepSetting.propTypes = {
  children: PropTypes.node,
};
StepSetting.preview = Preview;
StepSetting.contents = Contents;
export default StepSetting;
