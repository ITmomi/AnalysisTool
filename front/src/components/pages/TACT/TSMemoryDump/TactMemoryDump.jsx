import React from "react";
import {tsMemoryDumpSectionStyle} from "../StatusMonitor/styleSheet";
import {SelectLog} from './SelectLog';
import {LogTable} from "./LogTable";
import {DrawingGraph} from "./DrawingGraph";


const TactMemoryDump=()=> {
	console.log("TactMemoryDump");
	return (
		<>
			<section css={tsMemoryDumpSectionStyle}>
				<SelectLog/>
				<LogTable/>
				<DrawingGraph/>
			</section>
		</>
	);
};
export default TactMemoryDump;