import React from 'react';
import SelectSource from '../Fragments/SelectSource/SelectSource';
import SelectTarget from '../Fragments/SelectTarget/SelectTarget';
import OverlayResult from '../Fragments/OverlayResult/OverlayResult';
import { sectionStyle } from '../Fragments/styleGroup';
import { OVERLAY_ADC_CATEGORY } from '../../../../lib/api/Define/etc';

const Measurement = () => {
  return (
    <section css={sectionStyle}>
      <SelectSource mode={OVERLAY_ADC_CATEGORY} />
      <SelectTarget mode={OVERLAY_ADC_CATEGORY} />
      <OverlayResult mode={OVERLAY_ADC_CATEGORY} />
    </section>
  );
};
export default Measurement;
