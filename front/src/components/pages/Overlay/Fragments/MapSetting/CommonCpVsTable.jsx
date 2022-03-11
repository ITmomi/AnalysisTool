import React from 'react';
import { Input, Select } from 'antd';
import * as SG from '../styleGroup';
import {
  CP_VS_DISPLAY_LIST,
  CPVS_MODE as Mode,
} from '../../../../../lib/api/Define/OverlayDefault';
import useOverlayResult from '../../../../../hooks/useOverlayResultInfo';
import PropTypes from 'prop-types';

const CpVsColumn = ({ shotN, shotInfo, changeEvent, mode, origin }) => {
  const ChangeFunc = (key, value) => {
    changeEvent({ shot: shotN, info: { ...shotInfo, [key]: value } });
  };
  if (!shotInfo ?? true) return <></>;
  return (
    <tr>
      <td style={{ minWidth: '70px' }}>Shot {shotN}:</td>
      {Object.keys(shotInfo ?? {}).map((o, idx) => (
        <>
          <td>
            {o === 'display' ? (
              <>
                <Select
                  style={{ minWidth: '100px' }}
                  disabled={origin.expo_mode !== 30}
                  value={shotInfo[o]}
                  key={`${o}_${idx}`}
                  onChange={(v) => ChangeFunc(o, v)}
                >
                  {CP_VS_DISPLAY_LIST.map((item, j) => (
                    <>
                      <Select.Option value={item} key={j}>
                        {item}
                      </Select.Option>
                    </>
                  ))}
                </Select>
              </>
            ) : (
              <Input
                value={mode === Mode.FROM_LOG ? '' : shotInfo[o]}
                onChange={(v) => ChangeFunc(o, v.target.value)}
                disabled={
                  mode === Mode.FROM_LOG ||
                  (mode === Mode.SAME && parseInt(shotN) !== origin.shot[0])
                }
              />
            )}
          </td>
        </>
      ))}
    </tr>
  );
};
CpVsColumn.propTypes = {
  shotN: PropTypes.string,
  shotInfo: PropTypes.object,
  changeEvent: PropTypes.func,
  mode: PropTypes.string,
  origin: PropTypes.object,
};
const CommonCpVsTable = ({ mode, obj }) => {
  const { cpvsAdcShotChangeFunc } = useOverlayResult();
  const changeEvent = (e) => {
    cpvsAdcShotChangeFunc(e, mode);
  };
  return (
    <div className="table-wrapper">
      <table css={SG.tableStyle}>
        <thead>
          <tr>
            <th>{'SHOT'}</th>
            {Object.keys(obj.origin?.default ?? {})?.map((o, i) => (
              <>
                <th key={`h_${i}`}>{o.toUpperCase()}</th>
              </>
            ))}
          </tr>
        </thead>
        <tbody>
          {Object.entries(obj.setting?.shots ?? {})?.map((shot, i) => {
            return (
              <>
                <CpVsColumn
                  changeEvent={changeEvent}
                  shotInfo={shot[1]}
                  key={`shot_${i}`}
                  shotN={shot[0]}
                  mode={obj.setting?.mode}
                  origin={obj.origin}
                />
              </>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
CommonCpVsTable.propTypes = {
  mode: PropTypes.string,
  obj: PropTypes.object,
};

export default CommonCpVsTable;
