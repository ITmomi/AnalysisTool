import React from 'react';
import * as SS from '../styleSheet';
import {Upload} from 'antd';
import { InboxOutlined } from '@ant-design/icons';

export const SelectLog = () => {
return (
	<>
	<div css={SS.componentStyle} className="stretch">
		<div css={SS.componentTitleStyle}>Select Source</div>
		<div css={SS.contentWrapperStyle}>
			<div css={SS.contentStyle} className="full-width">
				<div css={SS.contentItemStyle} className="upload column-2">
					<span className="label">Log Files</span>
					<Upload.Dragger>
						<p className="ant-upload-drag-icon">
							<InboxOutlined />
						</p>
						<p className="ant-upload-text">
							Click or drag file to this area to upload
						</p>
					</Upload.Dragger>
				</div>
			</div>
		</div>

		<div className="source-button-wrapper">
			<button
				css={SS.antdButtonStyle}
				className="white"
			>
				Load Start
			</button>
		</div>
	</div>
	</>
);
};