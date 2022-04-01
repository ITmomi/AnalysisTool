import React from 'react';
import * as SS from '../StatusMonitor/styleSheet';
import {CloudDownloadOutlined} from "@ant-design/icons";



export const DrawingGraph = () => {
	return (
		<>
			<div css={SS.tsComponentStyle} className="span">
				<div css={SS.controlStyle}>
					<div css={SS.componentTitleStyle}>Drawing Graph</div>
					<div>
						<div css={SS.customButtonStyle}>
							<button
								css={SS.antdButtonStyle}
								className="white"
								style={{ marginLeft: '8px', fontWeight: 400 }}
							>
								<CloudDownloadOutlined />
								<span> Enter The Palate No. </span>
							</button>
						</div>
					</div>
				</div>
			</div>
		</>
	);
};