import React from 'react';
import CustomAccordion from '../../../../UI/molecules/CustomAccordion/CustomAccodion';
import {
  MSG_ALL,
  MSG_RANGE_CHANGE,
  MSG_RANGE_SHOT_CHANGE,
  MSG_SETTING,
  MSG_SHOT_CHANGE,
  MSG_X_LOWER_LIMIT,
  MSG_X_UPPER_LIMIT,
  MSG_Y_LOWER_LIMIT,
  MSG_Y_UPPER_LIMIT,
} from '../../../../../lib/api/Define/Message';
import * as SG from '../styleGroup';
import { Descriptions, InputNumber, Select } from 'antd';
import { Option } from 'antd/es/mentions';
import useOverlayResultInfo from '../../../../../hooks/useOverlayResultInfo';
import useOverlaySettingInfo from '../../../../../hooks/useOverlaySettingInfo';

const RangeAndShotSetting = () => {
  const {
    updateVariationSetting: updateSetting,
    gVariation: variation,
  } = useOverlayResultInfo();
  const { adcCommonInfo: common } = useOverlaySettingInfo();

  return (
    <CustomAccordion title={MSG_RANGE_SHOT_CHANGE} defaultValue={false}>
      <div css={SG.settingContentStyle} className="etc">
        <div className="content">
          <div css={SG.contentItemStyle} className="etc">
            <Descriptions layout="vertical" bordered column={5}>
              <Descriptions.Item label={MSG_SETTING}>
                <div>{MSG_RANGE_CHANGE}</div>
              </Descriptions.Item>
              <Descriptions.Item label={MSG_X_LOWER_LIMIT}>
                <InputNumber
                  style={{ width: '75px', alignItems: 'center' }}
                  defaultValue={variation?.x_range_min ?? ''}
                  controls={false}
                  max={variation?.x_range_max}
                  onChange={(e) => updateSetting({ x_range_min: e })}
                />
              </Descriptions.Item>
              <Descriptions.Item label={MSG_X_UPPER_LIMIT}>
                <InputNumber
                  style={{ width: '75px', alignItems: 'center' }}
                  defaultValue={variation?.x_range_max ?? ''}
                  min={variation?.x_range_min ?? 0}
                  controls={false}
                  onChange={(e) => updateSetting({ x_range_max: e })}
                />
              </Descriptions.Item>
              <Descriptions.Item label={MSG_Y_LOWER_LIMIT}>
                <InputNumber
                  style={{ width: '75px', alignItems: 'center' }}
                  defaultValue={variation?.y_range_min ?? ''}
                  controls={false}
                  max={variation?.y_range_max ?? 0}
                  onChange={(e) => updateSetting({ y_range_min: e })}
                />
              </Descriptions.Item>
              <Descriptions.Item label={MSG_Y_UPPER_LIMIT}>
                <InputNumber
                  style={{ width: '75px', alignItems: 'center' }}
                  defaultValue={variation?.y_range_max ?? ''}
                  min={variation?.y_range_min ?? 0}
                  controls={false}
                  onChange={(e) => updateSetting({ y_range_max: e })}
                />
              </Descriptions.Item>
              <Descriptions.Item>{MSG_SHOT_CHANGE}</Descriptions.Item>
              <Descriptions.Item span={4}>
                <Select
                  defaultValue={variation?.select_shot ?? 'all'}
                  onChange={(e) => updateSetting({ select_shot: e })}
                  style={{ minWidth: '90px' }}
                >
                  <>
                    <Option value={'all'} key={`shot_all`}>
                      {MSG_ALL}
                    </Option>
                    {common.shot.map((shot, i) => {
                      return (
                        <Option value={shot} key={`shot_${i}`}>
                          {shot}{' '}
                        </Option>
                      );
                    })}
                  </>
                </Select>
              </Descriptions.Item>
            </Descriptions>
          </div>
        </div>
      </div>
    </CustomAccordion>
  );
};
export default RangeAndShotSetting;
