import React from 'react';
import { SourceTarget as JtactSourceTarget } from "./JobTACT/SourceTarget";
import { SourceTarget as PtactSourceTarget } from "./PlateTACT/SourceTarget"
import {sectionStyle} from "../../Overlay/Fragments/styleGroup";
import SelectSource from "../../Overlay/Fragments/SelectSource/SelectSource";
import {OVERLAY_ADC_CATEGORY} from "../../../../lib/api/Define/etc";
import OverlayResult from "../../Overlay/Fragments/OverlayResult/OverlayResult";

const TactSelectTarget = ({ selected }) => {
	return selected === '1' ? (
		<JtactSourceTarget />
	) : (
	 <PtactSourceTarget />
	);
}


const Tact = () => {
	return (
		<section css={sectionStyle}>
			<SelectSource mode={OVERLAY_ADC_CATEGORY} />
			<TactSelectTarget selected={} />
			<OverlayResult mode={OVERLAY_ADC_CATEGORY} />
		</section>
	);
};