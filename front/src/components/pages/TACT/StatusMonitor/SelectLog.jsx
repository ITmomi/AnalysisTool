import React, {useState} from 'react';
import * as SG from './styleSheet';
import { Upload } from 'antd';
import {InboxOutlined,} from "@ant-design/icons";


const [addedFiles, setAddedFiles] = useState([]);

export const SelectLog = () => {
return (
	<div css={SG.componentStyle} className="stretch">
		<div css={SG.componentTitleStyle}>Select Source</div>
		<div css={SG.contentWrapperStyle}>
			<div css={SG.contentStyle} className="full-width">
				<div css={SG.contentItemStyle} className="upload column-2">
					<span className="label">Log Files</span>
					<Upload.Dragger
						onChange={(e) => {
							setAddedFiles(
								e.fileList.length > 0
									? e.fileList.map((v) => v.originFileObj)
									: [],
							);
						}}
						beforeUpload={() => false}
					>
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
				css={SG.antdButtonStyle}
				className="white"
				disabled={addedFiles.length === 0}
			>
				Load Start
			</button>
		</div>
	</div>
);
};