export const InputFormDateRegex = /^(2\d\d\d)-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[01])$/;
export const GraphDateRegex = /^([12]\d\d\d)-(0[1-9]|1[0-2])-(0[1-9]|1\d|2\d|3[01])(\s(0\d|1\d|2[0-3]):[0-5]\d(:[0-5]\d(\.\d{1,6})?)?)?$/;
export const GraphRangeRegex = /^(-?\d{1,20}(\.\d{1,20})?$)|^(\d{0,20})$/;
export const CommonRegex = /^[a-zA-Z]{1,30}$|^[a-zA-Z]\w{0,28}[a-zA-Z]$/;
export const AllMax30Regex = /^.{1,30}$/;
export const RuleNameRegex = /^\w{1,30}$/;
export const TableNameRegex = /^[a-z\d_]{1,30}$/;
export const NumberRegex = /^\d{1,3}$/;
export const AnyRegex = /^.+$/m;
export const coefRegex = /^[1]0*$/;
export const AnalysisPeriodRegex = /^([1-9]|1\d|2[0-3])[Hh]$|^([1-9]|[1-9]\d|[0-2]\d\d|3[0-6][0-5])[dD]$|^([1-9]|1[0-2])[mM]$|^[1-9][yY]$/;
