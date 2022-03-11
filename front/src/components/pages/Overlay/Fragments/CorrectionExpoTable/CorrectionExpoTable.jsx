import React from 'react';
import PropTypes from 'prop-types';
import CustomTextCheckBox from '../CustomTextCheckBox/CustomTextCheckBox';
import * as tStyle from './styleGroup';
import useOverlayResultInfo from '../../../../../hooks/useOverlayResultInfo';

const CorrectionExpoTable = ({ columns, rows, name }) => {
  if (columns === undefined || rows === undefined) return;
  const {
    gCorrectionMap,
    cpvsCorrectionShotChangeFunc,
  } = useOverlayResultInfo();

  const changeShotFunc = (name, shotN, properties, value) => {
    const { cp_vs } = gCorrectionMap;
    let shotInfo;
    if (shotN === undefined) {
      shotInfo = cp_vs.correction.shots[name].map((o) => ({
        ...o,
        [properties]: { ...o[properties], checked: value.mode === 'on' },
      }));
    } else {
      const clone = cp_vs.correction.shots[name].find(
        (o) => o.shot.id === shotN,
      );
      shotInfo = {
        ...clone,
        [properties]: {
          ...clone[properties],
          ...value,
        },
      };
    }
    console.log(shotInfo);
    cpvsCorrectionShotChangeFunc(shotInfo, name);
  };

  return (
    <div className="table-wrapper">
      <table css={tStyle.controlTableStyle}>
        <thead>
          <tr>
            {Object.keys(columns).map((v, i) => {
              const list = rows.filter((o) => o[v]?.checked === false);
              return (
                <th key={i}>
                  {v === 'shot' ? (
                    v
                  ) : (
                    <CustomTextCheckBox
                      id={`${v}_chk`}
                      label={v}
                      isChecked={list.length === 0}
                      changeFunc={(e) => changeShotFunc(name, undefined, v, e)}
                    />
                  )}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {rows.map((v, idx) => {
            return (
              <tr key={`${name}_${idx}`}>
                {Object.keys(v).map((x, i) => {
                  return (
                    <td key={`${name}_${idx}_${i}`}>
                      <CustomTextCheckBox
                        id={`${name}_${idx}_${i}`}
                        isChecked={
                          x === 'shot' ? v[x].mode === 'auto' : v[x].checked
                        }
                        disabled={v.shot.mode === 'auto'}
                        label={x === 'shot' ? v[x].id : undefined}
                        useText={x !== 'shot'}
                        value={x !== 'shot' ? v[x].value : undefined}
                        onText="auto"
                        offText="manual"
                        changeFunc={(e) =>
                          changeShotFunc(name, v.shot.id, x, e)
                        }
                      />
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
CorrectionExpoTable.propTypes = {
  columns: PropTypes.object.isRequired,
  rows: PropTypes.array.isRequired,
  name: PropTypes.string,
};

export default CorrectionExpoTable;
