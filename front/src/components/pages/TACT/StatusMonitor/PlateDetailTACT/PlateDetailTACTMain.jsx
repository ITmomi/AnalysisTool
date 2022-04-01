import React from "react";
import {SelectLog} from '../JobTACT/SelectLog';
import {SourceTarget} from "./SourceTarget";
import {sectionStyle} from "../styleSheet";
import {PlateDetailTACT} from "./PlateDetailTACT";

const PlateDetailTACTMain=()=> {
	console.log("TactStatusMonitor");
	return (
		<>
			<section css={sectionStyle}>
				<SelectLog/>
				<SourceTarget/>
				<PlateDetailTACT/>
			</section>
		</>
	);
};
export default PlateDetailTACTMain;