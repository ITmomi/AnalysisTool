import React, { useState } from 'react';
import PropTypes from 'prop-types';
import * as SG from '../styleGroup';
import CustomAccordion from '../../../../UI/molecules/CustomAccordion/CustomAccodion';
import CustomRadioGroup from '../../../../UI/molecules/CustomRadioGroup/CustomRadioGroup';
import CpVsMeasurement from './CpVsMeasurement';
import {
  E_CPVS_ADC_MEASUREMENT,
  OVERLAY_ADC_CATEGORY,
} from '../../../../../lib/api/Define/etc';
import { MSG_CP_VS } from '../../../../../lib/api/Define/Message';
import { OVERLAY_CORRECTION_CPVS_LIST } from '../../../../../lib/api/Define/OverlayDefault';
import CpVsCorrection from './CpVsCorrection';

const CpVsSetting = ({ mode, type }) => {
  const [tab, setTab] = useState(OVERLAY_CORRECTION_CPVS_LIST[0].id);

  return (
    <CustomAccordion title={MSG_CP_VS} defaultValue={true}>
      <div
        css={SG.settingContentStyle}
        className={mode !== OVERLAY_ADC_CATEGORY ? 'full-width' : ''}
      >
        <div className="content">
          {mode === OVERLAY_ADC_CATEGORY ? (
            <CpVsMeasurement mode={mode} type={type} />
          ) : (
            <>
              <div className="radio-wrapper">
                <CustomRadioGroup
                  changeFunc={(v) => setTab(v)}
                  currentChecked={tab}
                  options={OVERLAY_CORRECTION_CPVS_LIST}
                  name="cp-vs-option"
                  className="cp-vs"
                />
              </div>
              <div
                css={SG.settingContentStyle}
                className={
                  'tab ' +
                  (tab === E_CPVS_ADC_MEASUREMENT ? '' : 'correction-cp-vs')
                }
              >
                {tab === E_CPVS_ADC_MEASUREMENT ? (
                  <CpVsMeasurement mode={mode} type={type} />
                ) : (
                  <CpVsCorrection mode={mode} type={type} />
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </CustomAccordion>
  );
};
CpVsSetting.propTypes = {
  mode: PropTypes.string,
  type: PropTypes.string,
};

export default CpVsSetting;
