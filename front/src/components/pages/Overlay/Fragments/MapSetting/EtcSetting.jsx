import React, { useMemo } from 'react';
import { InputNumber, Switch, Button } from 'antd';
import PropTypes from 'prop-types';
import * as SG from '../styleGroup';
import CustomAccordion from '../../../../UI/molecules/CustomAccordion/CustomAccodion';
import {
  MSG_DISPLAY_MAP,
  MSG_DIV,
  MSG_LOWER_ROW,
  MSG_NUMBER_OF_COLUMNS,
  MSG_PLATE_SIZE,
  MSG_SAVE,
  MSG_SHOW_EXTRA_INFO,
  MSG_SIZE_X,
  MSG_SIZE_Y,
  MSG_STILDE,
  MSG_UPPER_ROW,
} from '../../../../../lib/api/Define/Message';
import useOverlayResultInfo from '../../../../../hooks/useOverlayResultInfo';
import { css } from '@emotion/react';
import {
  E_OVERLAY_COMPONENT,
  E_OVERLAY_IMAGE,
  E_OVERLAY_MAP,
} from '../../../../../lib/api/Define/etc';

const BlockWrapper = css`
  min-width: 50%;
  padding: 15px !important;
  background-color: aliceblue;
`;
const contentsWrapper = css`
  display: flex;
  flex-direction: row;
`;
const DIVSetting = ({ type, obj }) => {
  const { divChangeFunc: changeFunc } = useOverlayResultInfo();

  return (
    <>
      <span className="label">{MSG_DIV}</span>
      <div className="tx-right">
        {type === E_OVERLAY_MAP ? (
          <>
            {' '}
            <span className="margin-r">{MSG_UPPER_ROW}</span>
            <InputNumber
              min={0.1}
              max={10.0}
              step={0.1}
              style={{ width: '22%' }}
              value={obj?.div_upper ?? ''}
              onChange={(e) => changeFunc({ div_upper: e }, type)}
            />{' '}
          </>
        ) : (
          <>
            <span className="margin-r">{MSG_LOWER_ROW}</span>
            <InputNumber
              min={0.1}
              max={10.0}
              step={0.1}
              style={{ width: '22%' }}
              value={obj?.div_lower ?? ''}
              onChange={(e) => changeFunc({ div_lower: e }, type)}
            />
            <span className="margin-lr">{MSG_UPPER_ROW}</span>
            <InputNumber
              min={0.1}
              max={10.0}
              step={0.1}
              style={{ width: '22%' }}
              value={obj?.div_upper ?? ''}
              onChange={(e) => changeFunc({ div_upper: e }, type)}
            />{' '}
          </>
        )}
      </div>
    </>
  );
};
DIVSetting.propTypes = {
  type: PropTypes.string,
  obj: PropTypes.object,
};

const DisplayMapSetting = ({ type, obj, origin }) => {
  const { displayMapChangeFunc: changeFunc } = useOverlayResultInfo();

  return (
    <>
      <span className="label">{MSG_DISPLAY_MAP}</span>
      <div>
        <InputNumber
          min={origin?.min ?? 1}
          max={obj?.max ?? 30}
          defaultValue={obj?.min ?? 1}
          onChange={(e) => changeFunc({ min: e }, type)}
        />
        <span className="margin-lr">{MSG_STILDE}</span>
        <InputNumber
          min={obj?.min ?? 1}
          max={origin?.max}
          defaultValue={obj?.max ?? 30}
          onChange={(e) => changeFunc({ max: e }, type)}
        />
      </div>
    </>
  );
};
DisplayMapSetting.propTypes = {
  type: PropTypes.string,
  obj: PropTypes.object,
  origin: PropTypes.object,
};

const PlateSizeSetting = ({ type, obj }) => {
  const { plateSizeChangeFunc: changeFunc } = useOverlayResultInfo();

  return (
    <>
      <span className="label">{MSG_PLATE_SIZE}</span>
      <div className="tx-right">
        <span className="margin-r">{MSG_SIZE_X}</span>
        <InputNumber
          min={1000}
          max={9999}
          style={{ width: '30%' }}
          value={obj?.size_x ?? 2500}
          onChange={(e) => changeFunc({ size_x: e }, type)}
        />
        <span className="margin-lr">{MSG_SIZE_Y}</span>
        <InputNumber
          min={1000}
          max={9999}
          style={{ width: '30%' }}
          value={obj?.size_y ?? 2500}
          onChange={(e) => changeFunc({ size_y: e }, type)}
        />
      </div>
    </>
  );
};
PlateSizeSetting.propTypes = {
  type: PropTypes.string,
  obj: PropTypes.object,
};

const ColumnNumSetting = ({ type, obj }) => {
  const { columnNExtraInfoChangeFunc: changeFunc } = useOverlayResultInfo();

  return (
    <>
      <span className="label">{MSG_NUMBER_OF_COLUMNS}</span>
      <InputNumber
        min={1}
        max={5}
        value={obj ?? 4}
        onChange={(e) => changeFunc({ column_num: e }, type)}
      />
    </>
  );
};
ColumnNumSetting.propTypes = {
  type: PropTypes.string,
  obj: PropTypes.number,
};

const ExtraInfoSetting = ({ type, obj }) => {
  const { columnNExtraInfoChangeFunc: changeFunc } = useOverlayResultInfo();

  return (
    <>
      <span className="label">{MSG_SHOW_EXTRA_INFO}</span>
      <Switch
        checked={obj ?? false}
        onChange={(e) => changeFunc({ show_extra_info: e }, type)}
      />
    </>
  );
};
ExtraInfoSetting.propTypes = {
  type: PropTypes.string,
  obj: PropTypes.bool,
};
const EtcSetting = ({ type }) => {
  const {
    gMap,
    gCorrectionMap: gCorrection,
    gAdcMeasurementFabName,
    gCorrectionFabName,
    updateEtcSetting,
    isEtcUpdating,
    EtcSettingUpdateMutation: updateMutation,
    gAdcMeasurementData,
    gCorrectionData,
  } = useOverlayResultInfo();
  const setting = useMemo(
    () =>
      type === E_OVERLAY_MAP
        ? {
            value: gMap,
            origin: gAdcMeasurementData,
            fab_name: gAdcMeasurementFabName,
          }
        : [E_OVERLAY_IMAGE, E_OVERLAY_COMPONENT].includes(type)
        ? {
            value: gCorrection,
            origin: gCorrectionData,
            fab_name: gCorrectionFabName,
          }
        : undefined,
    [gMap, gCorrection, gCorrectionData, gAdcMeasurementData],
  );

  const ApplyButtonEnable = useMemo(() => {
    const { div, plate_size } = setting.value;
    return !!div.div_upper && !!plate_size.size_x && !!plate_size.size_y;
  }, [setting.value.div, setting.value.plate_size]);

  return (
    <CustomAccordion title="Etc." defaultValue={true}>
      <div css={SG.settingContentStyle} className="etc">
        <div className="content" css={contentsWrapper}>
          <div css={[BlockWrapper]}>
            {' '}
            {/*Left*/}
            <div css={SG.contentItemStyle} className="etc">
              <DisplayMapSetting
                obj={setting.value.display_map}
                type={type}
                origin={
                  setting.origin?.etc?.display_map ?? { max: 999, min: 0 }
                }
              />
            </div>
            <div css={SG.contentItemStyle} className="etc">
              <ColumnNumSetting obj={+setting.value.column_num} type={type} />
            </div>
            {type === E_OVERLAY_MAP ? (
              <div css={SG.contentItemStyle} className="etc">
                <ExtraInfoSetting
                  obj={!!setting.value.show_extra_info}
                  type={type}
                />
              </div>
            ) : (
              <></>
            )}
          </div>
          <div css={[BlockWrapper, { marginLeft: '10px' }]}>
            {' '}
            {/*right*/}
            <div css={SG.contentItemStyle} className="etc">
              <DIVSetting type={type} obj={setting.value.div} />
            </div>
            <div css={SG.contentItemStyle} className="etc">
              <PlateSizeSetting type={type} obj={setting.value.plate_size} />
            </div>
            <div css={SG.contentItemStyle} className="etc">
              <Button
                type="dashed"
                shape="round"
                disabled={!ApplyButtonEnable}
                onClick={() => {
                  updateEtcSetting(true);
                  updateMutation.mutate({
                    obj: setting.value,
                    fab_name: setting.fab_name,
                  });
                }}
                loading={isEtcUpdating}
              >
                {''} {MSG_SAVE}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </CustomAccordion>
  );
};
EtcSetting.propTypes = {
  type: PropTypes.string,
};

export default EtcSetting;
