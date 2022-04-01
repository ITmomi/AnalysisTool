import React from 'react';
import * as SS from '../StatusMonitor/styleSheet';
import {Upload, Radio, Switch, Select} from 'antd';
import {InboxOutlined, PlayCircleOutlined} from '@ant-design/icons';

export const SelectLog = () => {
	const [value, setValue] = React.useState(1);

	const onChange = e => {
		console.log('radio checked', e.target.value);
		setValue(e.target.value);
	};
	return (
		<>
			<div css={SS.componentStyle} className="stretch">
				<div css={SS.componentTitleStyle}>Select Source</div>
				<div css={SS.contentWrapperStyle}>
					<div css={SS.contentStyle} className="full-width">
						<div css={SS.tsMemoryDumpContentItemStyle} className="upload column-2">
							<span className="label">Log Type</span>
								<Radio.Group onChange={onChange} value={value} className='radioStyle'>
									<Radio value={1}>Copy File</Radio>
									<Radio value={2}>logServer Log</Radio>
									<Radio value={3}>Import Log</Radio>
								</Radio.Group>
						</div>
						<div css={SS.tsMemoryDumpContentItemStyle} className="upload column-2">
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
						<div css={SS.tsMemoryDumpContentItemStyle} className="upload column-2" style={
							{display:'flex', justifyContent:"space-between"}
						}>
							<span className="label">Auto Adjustment</span>
							<Switch style={{left:'-15px'}} defaultChecked/>
						</div>
						<div css={SS.tsMemoryDumpContentItemStyle} className="upload column-2">
							<span className="label">EquipMent</span>
							<Select
								style={{ width: '100%' }}
							>
							</Select>
						</div>
					</div>
					<button
						css={SS.customButtonStyle}
						className="absolute"

					>
						<PlayCircleOutlined />
						<span>Start</span>
					</button>
				</div>
			</div>
		</>
	);
};