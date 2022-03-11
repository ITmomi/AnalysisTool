import React from 'react';
import { Descriptions, InputNumber } from 'antd';
import * as SG from '../styleGroup';
import CustomAccordion from '../../../../UI/molecules/CustomAccordion/CustomAccodion';
import {
  MSG_3SIGMA_RANGE,
  MSG_3SIGMA_X,
  MSG_3SIGMA_Y,
  MSG_SETTING,
  MSG_Y_UPPER_LIMIT,
} from '../../../../../lib/api/Define/Message';
import useOverlayResultInfo from '../../../../../hooks/useOverlayResultInfo';

const ThreeSigmaRangeSetting = () => {
  const {
    updateReproducibilitySetting: updateRange,
    gReproducibility: range,
  } = useOverlayResultInfo();
  return (
    <CustomAccordion title={MSG_3SIGMA_RANGE} defaultValue={false}>
      <div css={SG.settingContentStyle} className="etc">
        <div className="content">
          <div css={SG.contentItemStyle} className="etc">
            <Descriptions layout="vertical" bordered>
              <Descriptions.Item label={MSG_SETTING}>
                {MSG_Y_UPPER_LIMIT}
              </Descriptions.Item>
              <Descriptions.Item label={MSG_3SIGMA_X}>
                <InputNumber
                  controls={false}
                  style={{ width: '60%', alignItems: 'center' }}
                  defaultValue={range?.three_sigma_x ?? ''}
                  onChange={(e) => updateRange({ ...range, three_sigma_x: e })}
                />
              </Descriptions.Item>
              <Descriptions.Item label={MSG_3SIGMA_Y}>
                <InputNumber
                  controls={false}
                  style={{ width: '60%', alignItems: 'center' }}
                  defaultValue={range?.three_sigma_y ?? ''}
                  onChange={(e) => updateRange({ ...range, three_sigma_y: e })}
                />
              </Descriptions.Item>
            </Descriptions>
          </div>
        </div>
      </div>
    </CustomAccordion>
  );
};

export default ThreeSigmaRangeSetting;
