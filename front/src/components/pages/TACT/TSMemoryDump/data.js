import React from "react";
import { Tag } from "antd";

export const columns = [
	{
		title: 'LEVEL',
		dataIndex: 'name',
		key: 'name',
		render: (name) => {
			const splitStr = name.split('-');
			let tagColor = 'magenta';

			switch (splitStr[0]) {
				case '2':
					tagColor = 'orange';
					break;
				case '3':
					tagColor = 'green';
					break;
				case '4':
					tagColor = 'purple'
					break;
				default:
					break;
			}
			return	(
				<>
					<Tag color={tagColor}>
						{`LEVEL ${splitStr[0]}`}
					</Tag> {splitStr[1]} / {splitStr[2]}
				</>
		);
		},
	},
	{
		title: 'Start',
		dataIndex: 'StartTime',
		key: 'StartTime',
		width: '15%',
	},
	{
		title: 'End',
		dataIndex: 'EndTime',
		width: '15%',
		key: 'EndTime',

	},
	{
		title: 'Elapsed',
		dataIndex: 'Elapsed',
		width: '15%',
		key: 'Elapsed',
		filters: [
			{
				text: '500',
				value: '500',
			},
			{
				text: '1000',
				value: '1000',
			},
		],
	},
];

export const data = [
	{
		key: 1,
		name: '1-PU10000-AFC Pos Move & Mecha Pre Measuremenet',
		StartTime: 0.00,
		EndTime: 4.34,
		Elapsed: 4.34,
		children: [
			{
				key: 11,
				name: '2-PU11000-AFC Pos Move (Stage)',
				StartTime: 0.00,
				EndTime: 2.67,
				Elapsed: 2.67,
			},
			{
				key: 12,
				name: '2-PU11001-AFC Pos Move (Stage)',
				StartTime: 0.01,
				EndTime: 2.67,
				Elapsed: 2.66,
				children: [
					{
						key: 121,
						name: '3-PU20001-Previous Plate Mecha Pre Pos (Chuck)',
						StartTime: 0.02,
						EndTime: 0.92,
						Elapsed: 0.90,
					},
				],
			},
			{
				key: 13,
				name: '2-PU30000-AFC Measurement & TV Pre Measurement',
				StartTime: 4.34,
				EndTime: 7.37,
				Elapsed: 3.03,
				children: [
					{
						key: 131,
						name: '3-PU31001-AFC Measurement & Mecha Pre Comp Move',
						StartTime: 4.34,
						EndTime: 4.70,
						Elapsed: 0.36,
						children: [
							{
								key: 1311,
								name: '4-PU31101-TV Pre Measurement',
								StartTime: 4.72,
								EndTime: 7.77,
								Elapsed: 0.05,
							},
							{
								key: 1312,
								name: '4-PU31102-Fine Pos Move',
								StartTime: 4.72,
								EndTime: 7.37,
								Elapsed: 0.40,
							},
						],
					},
				],
			},
		],
	},
	{
		key: 2,
		name: '1-PU40000-AMF Forming Line',
		StartTime: 4.34,
		EndTime: 5.34,
		Elapsed: 1.00,
	},
];