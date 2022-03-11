import React, { useMemo } from 'react';
import CpVsOption from './CpVsOption';
import CommonCpVsTable from './CommonCpVsTable';
import JobFileUpload from './JobFileUpload';
import PropTypes from 'prop-types';
import {
  E_CPVS_ADC_MEASUREMENT,
  E_OVERLAY_COMPONENT,
  E_OVERLAY_IMAGE,
  E_OVERLAY_MAP,
} from '../../../../../lib/api/Define/etc';
import useOverlayResultInfo from '../../../../../hooks/useOverlayResultInfo';

const CpVsMeasurement = ({ mode, type }) => {
  const {
    gMap,
    gCorrectionMap,
    gCorrectionCPVS,
    gAdcMeasurementCPVS,
  } = useOverlayResultInfo();
  const info = useMemo(
    () =>
      type === E_OVERLAY_MAP
        ? { setting: gMap.cp_vs, origin: gAdcMeasurementCPVS }
        : [E_OVERLAY_IMAGE, E_OVERLAY_COMPONENT].includes(type)
        ? {
            setting: gCorrectionMap.cp_vs?.adc_measurement ?? {},
            origin: gCorrectionCPVS[E_CPVS_ADC_MEASUREMENT],
          }
        : undefined,
    [
      gMap.cp_vs,
      gCorrectionMap.cp_vs,
      gAdcMeasurementCPVS,
      gCorrectionCPVS.adc_measurement,
    ],
  );
  return (
    <>
      <CpVsOption
        mode={mode}
        type={type}
        obj={info}
        tab={E_CPVS_ADC_MEASUREMENT}
      />
      <CommonCpVsTable mode={mode} obj={info} />
      <JobFileUpload mode={mode} obj={info.setting} />
    </>
  );
};
CpVsMeasurement.propTypes = {
  mode: PropTypes.string,
  type: PropTypes.string,
};

export default CpVsMeasurement;
