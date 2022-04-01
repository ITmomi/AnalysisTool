import React from 'react';
import * as SS from '../styleSheet';
import {DatePicker, Select, Switch,} from "antd";
import {PlayCircleOutlined} from "@ant-design/icons";

const { Option } = Select;
export const SourceTarget = () => {
	return (
		<div css={SS.componentStyle}>
			<div css={SS.componentTitleStyle}>Select Target</div>
			<div css={SS.contentWrapperStyle} className="mg-bottom">
				<div css={SS.contentStyle}>
					<div css={SS.contentItemStyle} className="column-2">
						<span className="label">Period</span>
						<DatePicker.RangePicker

							style={{ width: '100%' }}
							inputReadOnly
							allowClear={false}
							showTime
						/>
					</div>
					<div css={SS.contentItemStyle} className="column-2"
						style={
							{display:'flex', justifyContent:"space-between"}
						}
					>
						<span className="label">Display Outlier</span>
						<Switch checkedChildren="ON" unCheckedChildren="OFF" defaultChecked />
					</div>
					<div css={SS.contentItemStyle} className="column-2">
						<span className="label">Job</span>
						<Select
							style={{ width: '100%' }}
						>
					    </Select>
					</div>
					<div css={SS.contentItemStyle} className="column-2">
						<span className="label">Unit</span>
						<Select
							defaultValue="Lot"
							style={{ width: '100%' }}
						>
							<Option value="Lot">Lot</Option>
							<Option value="Plate">Plate</Option>
						</Select>
					</div>
					<div css={SS.contentItemStyle} className="column-2">
						<span className="label">ADC/FDC</span>
						<Select
							defaultValue="ALL"
							style={{ width: '100%' }}
						>
							<Option value="ALL">ALL</Option>
							<Option value="ADC">ADC</Option>
							<Option value="FDC">FDC</Option>
						</Select>
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
		</div>
	);
};
