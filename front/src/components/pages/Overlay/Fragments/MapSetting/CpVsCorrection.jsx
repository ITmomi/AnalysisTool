import React, { useMemo } from 'react';
import CpVsOption from './CpVsOption';
import PropTypes from 'prop-types';
import { E_CPVS_CORRECTION } from '../../../../../lib/api/Define/etc';
import useOverlayResultInfo from '../../../../../hooks/useOverlayResultInfo';
import CorrectionExpoTable from '../CorrectionExpoTable/CorrectionExpoTable';

const CpVsCorrection = ({ mode, type }) => {
  const { gCorrectionMap, gCorrectionInfo: info } = useOverlayResultInfo();
  const obj = useMemo(
    () => ({
      setting: gCorrectionMap.cp_vs?.correction ?? {},
      origin: info.origin,
    }),
    [gCorrectionMap.cp_vs, info.origin],
  );
  console.log('info', info);
  console.log('CpVsSetting', type);
  console.log('tmpArray', obj);
  if (obj.setting?.shots?.cp[0] === undefined) return <></>;
  return (
    <>
      <div>
        <CpVsOption
          mode={mode}
          tab={E_CPVS_CORRECTION}
          type={type}
          obj={{
            setting: obj.setting,
            origin: obj.origin.cp_vs[E_CPVS_CORRECTION],
          }}
        />
        <div className="table-wrapper">
          <CorrectionExpoTable
            rows={obj.setting?.shots?.cp}
            columns={obj.setting?.shots?.cp[0]}
            name={'cp'}
          />
          <CorrectionExpoTable
            rows={obj.setting?.shots?.vs}
            columns={obj.setting?.shots?.vs[0]}
            name={'vs'}
          />
        </div>
      </div>
    </>
  );
};
CpVsCorrection.propTypes = {
  mode: PropTypes.string,
  type: PropTypes.string,
};

export default CpVsCorrection;
