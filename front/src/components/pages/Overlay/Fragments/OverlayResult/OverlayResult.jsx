import React, { useEffect } from 'react';
import PropTypes from 'prop-types';
import * as SG from '../styleGroup';
import ResultDownload from './ResultDownload';
import useOverlayResultInfo from '../../../../../hooks/useOverlayResultInfo';
import {
  E_OVERLAY_ANOVA,
  OVERLAY_ADC_CATEGORY,
} from '../../../../../lib/api/Define/etc';
import CustomRadioGroup from '../../../../UI/molecules/CustomRadioGroup/CustomRadioGroup';
import OverlayResultGraph from './OverlayResultGraph';
import OverlayResultSetting from './OverlayResultSetting';

export const OverlayResult = ({ mode }) => {
  const {
    OverlayResultMode,
    setOverlayResultMode,
    OverlayResultType,
    setOverlayResultType,
    getOverlayResultTypeList,
    gAdcMeasurementData,
    gCorrectionData,
    updateDisplay,
    setUpdateDisplay,
  } = useOverlayResultInfo();
  useEffect(() => {
    if (OverlayResultMode !== mode) {
      setOverlayResultMode(mode ?? OVERLAY_ADC_CATEGORY);
    }
  }, [mode]);

  if (
    OverlayResultMode === undefined ||
    !(mode === OVERLAY_ADC_CATEGORY ? gAdcMeasurementData : gCorrectionData)
  )
    return <></>;
  return (
    <div css={SG.componentStyle} className="span">
      <div css={SG.controlStyle}>
        <CustomRadioGroup
          changeFunc={(e) => setOverlayResultType(e)}
          currentChecked={OverlayResultType.id}
          options={getOverlayResultTypeList}
          name="result-type"
        />
        <div css={SG.customButtonStyle}>
          <ResultDownload mode={mode} Update={updateDisplay} />
        </div>
      </div>
      {OverlayResultType?.id ?? false ? (
        <>
          {OverlayResultType.id !== E_OVERLAY_ANOVA ? (
            <div css={SG.settingStyle}>
              <OverlayResultSetting
                type={OverlayResultType}
                mode={mode}
                UpdateGraph={{ update: updateDisplay, func: setUpdateDisplay }}
              />
            </div>
          ) : (
            <></>
          )}
          <div css={SG.resultStyle}>
            <OverlayResultGraph
              mode={mode}
              type={OverlayResultType.id}
              origin_data={
                mode === OVERLAY_ADC_CATEGORY
                  ? gAdcMeasurementData
                  : gCorrectionData
              }
              UpdateGraph={{ update: updateDisplay, func: setUpdateDisplay }}
            />
          </div>
        </>
      ) : (
        <></>
      )}
    </div>
  );
};
OverlayResult.propTypes = {
  mode: PropTypes.string,
};

export default OverlayResult;
