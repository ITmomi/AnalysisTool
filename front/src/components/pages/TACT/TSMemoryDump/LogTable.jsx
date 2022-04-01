import React from 'react';
import {columns, data} from './data';
import { Table } from 'antd';
import {CloudDownloadOutlined} from "@ant-design/icons";
import * as SS from '../StatusMonitor/styleSheet';


const rowSelection = {
	onChange: (selectedRowKeys, selectedRows) => {
		console.log(`selectedRowKeys: ${selectedRowKeys}`, 'selectedRows: ', selectedRows);
	},
	onSelect: (record, selected, selectedRows) => {
		console.log(record, selected, selectedRows);
	},
};

export const LogTable = () => {
	return (
		<>
			<div css={SS.tsComponentStyle} className="span">
				<div css={SS.controlStyle}>
					<div css={SS.componentTitleStyle}>Log Table</div>
					<div css={SS.customButtonStyle}>
						<button
							css={SS.antdButtonStyle}
							className="white"
							style={{ marginLeft: '8px', fontWeight: 400 }}
						>
							<CloudDownloadOutlined />
							<span> Download </span>
						</button>
					</div>
				</div>
				<div css={SS.tsTableStyle}>
					<Table
						columns={columns}
						rowSelection={{ ...rowSelection}}
						dataSource={data}
					/>
				</div>
				<div>
					<button
						css={SS.antdButtonStyle}
						className="blue"
						style={{width:'136px', float:'right'}}
					>
						View Graph
					</button>
				</div>
			</div>
		</>
	);
};