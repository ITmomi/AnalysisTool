import React from 'react';
import SelectSource from '../Fragments/SelectSource/SelectSource';
import SelectTarget from '../Fragments/SelectTarget/SelectTarget';
import OverlayResult from '../Fragments/OverlayResult/OverlayResult';
import { OVERLAY_CORRECTION_CATEGORY } from '../../../../lib/api/Define/etc';
import { sectionStyle } from '../Fragments/styleGroup';

const Correction = () => {
  return (
    <section css={sectionStyle}>
      <SelectSource mode={OVERLAY_CORRECTION_CATEGORY} />
      <SelectTarget mode={OVERLAY_CORRECTION_CATEGORY} />
      <OverlayResult mode={OVERLAY_CORRECTION_CATEGORY} />
    </section>
  );
};

export default Correction;
