import {
	E_TACT_JOBTACT,
	E_TACT_PLATETACT,
	E_TACT_PLATEDETAILTACT,
} from './TactEtc'

export const JOB_TACT = {
	id: E_TACT_JOBTACT,
	title: 'JobTACT'
};
export const PLETE_TACT = {
	id: E_TACT_PLATETACT,
	title: 'PlateTACT'
};
export const PLATEDETAIL_TACT = {
	id: E_TACT_PLATEDETAILTACT,
	title: 'PlateDetailTACT'
};

export const TACT_LIST = [
	JOB_TACT,
	PLETE_TACT,
	PLATEDETAIL_TACT
];