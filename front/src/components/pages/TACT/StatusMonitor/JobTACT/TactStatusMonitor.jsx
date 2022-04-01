import React from "react";
import {SelectLog} from './SelectLog';
import {SourceTarget} from "./SourceTarget";
import {sectionStyle} from "../styleSheet";
import {JobTact} from "./JobTACT";




 const TactStatusMonitor=()=> {
 	console.log("TactStatusMonitor");
	return (
		<>
			<section css={sectionStyle}>
				<SelectLog/>
				<SourceTarget/>
				<JobTact/>
			</section>
		</>
			);
};
export default TactStatusMonitor;