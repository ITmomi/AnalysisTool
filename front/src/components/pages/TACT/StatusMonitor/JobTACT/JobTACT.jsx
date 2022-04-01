import React from 'react';
import * as SS from '../styleSheet';
import {CloudDownloadOutlined, DownOutlined,} from "@ant-design/icons";
import {MSG_DOWNLOAD} from "../../../../../lib/api/Define/Message";
import {InputNumber, Switch, Menu, Dropdown, Button,} from "antd";
import ColorPicker from "rc-color-picker";
import CustomRadioGroup from "../../../../UI/molecules/CustomRadioGroup/CustomRadioGroup";
import {JOB_TACT, TACT_LIST} from './TactDefault'

const CustomMenu = () => {
	const handleMenuClick = (e) => {
		console.log('click', e);
	};

	const changeHandler = (colors) => {
		console.log(colors);
	};

	const closeHandler = (colors) => {
		console.log(colors);
	};

	return (
		<Menu css={SS.tactColorBoxStyle} onClick={(e) => handleMenuClick(e)} >
			<Menu.Item key="1">
				<ColorPicker
					color="#40A9FF"
					alpha={30}
					onChange={changeHandler}
					onClose={closeHandler}
					placement="topLeft"
					className="some-class"
					enableAlpha={false}
				>
					<button className="rc-color-picker-trigger"/>
				</ColorPicker>
				<div>
					<div>315A07A1/1LAA1EE</div>
					<div>#40A9FF</div>
				</div>
			</Menu.Item>
			<Menu.Item key="2">
				<ColorPicker
					color="#FFA940"
					alpha={30}
					onChange={changeHandler}
					onClose={closeHandler}
					placement="topLeft"
					className="some-class"
					enableAlpha={false}
				>
					<button className="rc-color-picker-trigger"/>
				</ColorPicker>
				<div>
					<div>425B03A1/1LAA2EE</div>
					<div>#FFA940</div>
				</div>
			</Menu.Item>
			<Menu.Item key="3">
				<ColorPicker
					color="#52C41A"
					alpha={30}
					onChange={changeHandler}
					onClose={closeHandler}
					placement="topLeft"
					className="some-class"
					enableAlpha={false}
				>
					<button className="rc-color-picker-trigger"/>
				</ColorPicker>
				<div>
					<div>546B0DLS/1LDB2EE</div>
					<div>#52C41A</div>
				</div>
			</Menu.Item>
		</Menu>
	);
};

export const JobTact = () => {

	return (
		<div css={SS.componentStyle} className="span">
			<div css={SS.controlStyle}>
				<div>
					<CustomRadioGroup
						changeFunc={(e) => console.log(e)}
						currentChecked={JOB_TACT}
						options={TACT_LIST}
						name="result-type"
					/>
				</div>
				<div css={SS.customButtonStyle}>
					<button
						css={SS.antdButtonStyle}
						className="white"
						style={{ marginLeft: '8px', fontWeight: 400 }}
					>
						<CloudDownloadOutlined />
						<span> {MSG_DOWNLOAD} </span>
					</button>
				</div>
			</div>
			<div css={SS.lineStyle}/>
			<div>
				<span css={SS.subTitleStyle}>Graph Setting</span>
			</div>
			<div css={SS.tactGraphSettingStyle}>
				<Switch checkedChildren="Auto" unCheckedChildren="Manual" defaultChecked />
				<div>
				<span>Y:Lower Limit</span>
				<InputNumber
					min={1}
					max={100}
					step={1}
					style={{ width: '100%' }}
				/>
				</div>
				<div>
					<span>Y:Upper Limit</span>
					<InputNumber
						min={1}
						max={100}
						step={1}
						style={{ width: '100%' }}
					/>
				</div>
			</div>
			<div style={{display: 'flex'}}>
				<span css={SS.subTitleStyle}>Graph Color Setting</span>
				<div css={SS.tactGraphColorSettingStyle}>
					<Dropdown overlay={CustomMenu} css={SS.tactGraphColorButtonStyle}>
						<Button>
							Job TACT Color<DownOutlined />
						</Button>
					</Dropdown>
				</div>
			</div>

		</div>
	);
};