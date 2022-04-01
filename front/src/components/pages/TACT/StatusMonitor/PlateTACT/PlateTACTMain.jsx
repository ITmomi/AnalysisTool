import React from "react";
import {SelectLog} from '../JobTACT/SelectLog';
import {SourceTarget} from "./SourceTarget";
import {sectionStyle} from "../styleSheet";
import {PlateTact} from "./PlateTACT";

const PlateTACTMain=()=> {
	console.log("TactStatusMonitor");
	return (
		<>
			<section css={sectionStyle}>
				<SelectLog/>
				<SourceTarget/>
				<PlateTact/>
			</section>
		</>
	);
};
export default PlateTACTMain;