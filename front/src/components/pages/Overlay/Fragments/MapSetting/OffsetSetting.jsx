import React, { useMemo } from 'react';
import { Button, InputNumber, Switch } from 'antd';
import * as SG from '../styleGroup';
import CustomAccordion from '../../../../UI/molecules/CustomAccordion/CustomAccodion';
import PropTypes from 'prop-types';
import {
  MSG_OFFSET_X,
  MSG_OFFSET_XY,
  MSG_OFFSET_Y,
} from '../../../../../lib/api/Define/Message';
import {
  E_OVERLAY_COMPONENT,
  E_OVERLAY_IMAGE,
  E_OVERLAY_MAP,
} from '../../../../../lib/api/Define/etc';
import useOverlayResult from '../../../../../hooks/useOverlayResultInfo';

const OffsetSetting = ({ type }) => {
  const {
    gMap,
    gCorrectionMap: gCorrection,
    offsetChangeFunc,
    offsetResetFunc,
  } = useOverlayResult();
  const setting = useMemo(
    () =>
      (type === E_OVERLAY_MAP
        ? gMap
        : [E_OVERLAY_IMAGE, E_OVERLAY_COMPONENT].includes(type)
        ? gCorrection
        : undefined
      ).offset,
    [gMap, gCorrection],
  );

  return (
    <CustomAccordion title={MSG_OFFSET_XY} defaultValue={true}>
      <div css={SG.settingContentStyle}>
        <div className="content">
          <div css={SG.contentItemStyle} className="column-3">
            <div
              className="switch-wrapper"
              style={{
                display: 'inline-flex',
                flexDirection: 'column',
                width: '80px',
              }}
            >
              <Switch
                checkedChildren={'auto'}
                unCheckedChildren={'Manual'}
                checked={setting?.mode === 'auto'}
                onChange={(e) =>
                  offsetChangeFunc(
                    { mode: e === true ? 'auto' : 'manual' },
                    type,
                  )
                }
                style={{ marginBottom: '5px' }}
              />
              <Button
                type="dashed"
                size="small"
                shape="round"
                disabled={setting?.mode === 'auto'}
                style={{ height: '21px', fontWeight: '600' }}
                onClick={() => offsetResetFunc(type)}
              >
                {'RESET'}
              </Button>
            </div>
            <span className="title">{MSG_OFFSET_X}</span>
            <span className="title">{MSG_OFFSET_Y}</span>
          </div>
          {Object.keys(setting.info).map((shotN, i) => (
            <>
              <div
                css={SG.contentItemStyle}
                className="column-3"
                key={`${shotN}_${i}`}
              >
                <span className="label">{`Shot ${shotN}`}</span>
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="Offset X"
                  min={'0.0'}
                  max={'999.0'}
                  step={'0.1'}
                  value={setting?.info?.[shotN]?.x ?? ''}
                  onChange={(e) =>
                    offsetChangeFunc({ [shotN]: { x: e } }, type)
                  }
                  disabled={setting?.mode === 'auto'}
                />
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="Offset Y"
                  min={'0.0'}
                  max={'999.0'}
                  step={'0.1'}
                  value={setting?.info?.[shotN]?.y ?? ''}
                  onChange={(e) =>
                    offsetChangeFunc({ [shotN]: { y: e } }, type)
                  }
                  disabled={setting?.mode === 'auto'}
                />
              </div>
            </>
          ))}
        </div>
      </div>
    </CustomAccordion>
  );
};
OffsetSetting.propTypes = {
  type: PropTypes.string,
};

export default OffsetSetting;
