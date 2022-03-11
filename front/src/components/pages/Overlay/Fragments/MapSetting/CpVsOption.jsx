import React, { useMemo, useState } from 'react';
import { Button, Popconfirm, Radio, Select, Spin, Tooltip } from 'antd';
import * as SG from '../styleGroup';
import {
  MSG_CP_VS,
  MSG_CP_VS_EACH_SHOT,
  MSG_CP_VS_FROM_LOG,
  MSG_CP_VS_SHOT1_SAME,
  MSG_DEFAULT,
  MSG_NEW_PRESET,
  MSG_PRESET,
  MSG_SAVE_PRESET,
  MSG_TABLE_NAME_REGEXP,
  MSG_UPDATE_PRESET,
} from '../../../../../lib/api/Define/Message';
import useOverlayResultInfo from '../../../../../hooks/useOverlayResultInfo';
import {
  CPVS_MODE,
  CPVS_MODE as Mode,
} from '../../../../../lib/api/Define/OverlayDefault';
import { useMutation, useQuery } from 'react-query';
import { QUERY_KEY } from '../../../../../lib/api/Define/QueryKey';
import {
  add_Overlay_preset_info,
  delete_Overlay_preset_info,
  get_Overlay_preset_Info,
  update_Overlay_preset_info,
} from '../../../../../lib/api/axios/useOverlayRequest';
import {
  E_CPVS_ADC_MEASUREMENT,
  E_CPVS_CORRECTION,
  E_Default,
  E_New,
  OVERLAY_ADC_CATEGORY,
  OVERLAY_CORRECTION_CATEGORY,
} from '../../../../../lib/api/Define/etc';
import { DeleteOutlined } from '@ant-design/icons';
import PropTypes from 'prop-types';
import { NotificationBox } from '../../../../UI/molecules/NotificationBox';
import useOverlaySettingInfo from '../../../../../hooks/useOverlaySettingInfo';
import InputForm from '../../../../UI/atoms/Input/InputForm';
import { TableNameRegex } from '../../../../../lib/util/RegExp';
import { css } from '@emotion/react';
import QuestionCircleOutlined from '@ant-design/icons/lib/icons/QuestionCircleOutlined';

const { Option } = Select;

const contentsStyle = css`
  & .ant-form-item {
    margin-bottom: 0px;
  }
`;

const CpVsMode = ({ mode, tab, value, disabled }) => {
  const { cpvsModeChangeFunc: ChangeEvent } = useOverlayResultInfo();
  return (
    <>
      <span className="label">{MSG_CP_VS}</span>
      <Radio.Group
        value={value ?? Mode.FROM_LOG}
        className="radio-cp-vs"
        onChange={(e) => ChangeEvent(e, mode, tab)}
      >
        {tab !== E_CPVS_CORRECTION ? (
          <Radio value={Mode.FROM_LOG} disabled={disabled}>
            {MSG_CP_VS_FROM_LOG}
          </Radio>
        ) : (
          <></>
        )}
        <Radio value={Mode.EACH}>{MSG_CP_VS_EACH_SHOT}</Radio>
        <Radio value={Mode.SAME}>{MSG_CP_VS_SHOT1_SAME}</Radio>
      </Radio.Group>
    </>
  );
};
CpVsMode.propTypes = {
  value: PropTypes.string,
  mode: PropTypes.string,
  tab: PropTypes.string,
  disabled: PropTypes.bool,
};

const CpVsOption = ({ mode, type, obj, tab }) => {
  const {
    BasicCPVSChangeFunc,
    gAdcMeasurementFabName: adc_fab_name,
    gCorrectionFabName: correction_fab_name,
  } = useOverlayResultInfo();
  const {
    getCorrectionCpVsDefault,
    getCorrectionCpVsSetting,
  } = useOverlaySettingInfo();
  const defaultShotInfo = useMemo(
    () =>
      tab === E_CPVS_ADC_MEASUREMENT
        ? obj.origin?.shot?.reduce(
            (acc, o) =>
              Object.assign(acc, {
                [o]: obj.origin?.default,
              }),
            {},
          )
        : getCorrectionCpVsDefault(obj.origin.default, obj.origin.shot),
    [obj.origin.shot, obj.origin.default],
  );
  const [loading, setLoading] = useState({ mode: undefined, status: false });
  const [preset, setPreset] = useState({ id: E_Default, title: E_Default });

  const updateShotAndPresetInfo = (info) => {
    BasicCPVSChangeFunc(info, type, tab);
  };
  const updatePresetInfo = ({ preset }) => {
    updateShotAndPresetInfo({ preset });
  };
  const updateShotInfo = ({ mode, shots }) => {
    updateShotAndPresetInfo({ mode, shots });
  };
  useQuery(
    [QUERY_KEY.OVERLAY_PRESET_GET, preset.id],
    () =>
      get_Overlay_preset_Info({
        mode:
          mode === OVERLAY_CORRECTION_CATEGORY && tab === E_CPVS_CORRECTION
            ? OVERLAY_CORRECTION_CATEGORY
            : OVERLAY_ADC_CATEGORY,
        id: preset.id,
      }),
    {
      enabled:
        ![E_Default, E_New].includes(preset.id) &&
        loading.mode === 'get' &&
        loading.status,
      onSuccess: (info) => {
        updateShotInfo({
          mode: info.mode,
          shots:
            mode === OVERLAY_CORRECTION_CATEGORY && tab === E_CPVS_CORRECTION
              ? getCorrectionCpVsSetting(
                  undefined,
                  info?.step ?? info.shots,
                  obj.origin?.shot,
                )
              : info?.step ?? info.shots,
        });
      },
      onError: (error) => {
        NotificationBox('ERROR', error.message, 0);
      },
      onSettled: () => {
        setLoading({ mode: undefined, status: false });
      },
    },
  );
  const addMutation = useMutation(
    [QUERY_KEY.OVERLAY_PRESET_ADD],
    add_Overlay_preset_info,
    {
      onSuccess: (info) => {
        updatePresetInfo({
          preset: { ...obj.setting.preset, [+info]: preset.title },
        });
        setPreset((prev) => ({ ...prev, id: +info }));
      },
      onError: (err) => {
        NotificationBox('ERROR', err.message, 0);
      },
      onSettled: () => {
        setLoading({ mode: undefined, status: false });
      },
    },
  );
  const updateMutation = useMutation(
    [QUERY_KEY.OVERLAY_PRESET_UPDATE],
    update_Overlay_preset_info,
    {
      onSuccess: () => {
        updatePresetInfo({
          preset: { ...obj.setting.preset, [preset.id]: preset.title },
        });
      },
      onError: (err) => {
        console.log(err);
        NotificationBox('ERROR', err.message, 0);
      },
      onSettled: () => {
        setLoading({ mode: undefined, status: false });
      },
    },
  );
  const deleteMutation = useMutation(
    [QUERY_KEY.OVERLAY_PRESET_DELETE],
    (id) =>
      delete_Overlay_preset_info({
        id,
        mode:
          mode === OVERLAY_CORRECTION_CATEGORY && tab === E_CPVS_CORRECTION
            ? OVERLAY_CORRECTION_CATEGORY
            : OVERLAY_ADC_CATEGORY,
        tab,
      }),
    {
      onSuccess: ({ id }) => {
        const clone = { ...obj.setting.preset };
        delete clone[id];
        updatePresetInfo({ preset: clone });
        updateShotAndPresetInfo({
          preset: clone,
          mode:
            tab === E_CPVS_ADC_MEASUREMENT
              ? CPVS_MODE.FROM_LOG
              : CPVS_MODE.EACH,
          shot: defaultShotInfo,
        });
        setPreset({ title: E_Default, id: E_Default });
      },
      onError: (err) => {
        NotificationBox('ERROR', err.message, 0);
      },
      onSettled: () => {
        setLoading({ mode: undefined, status: false });
      },
    },
  );

  const savePreset = () => {
    setLoading({ mode: 'add/update', status: true });
    const presetMode =
      mode === OVERLAY_CORRECTION_CATEGORY && tab === E_CPVS_CORRECTION
        ? OVERLAY_CORRECTION_CATEGORY
        : OVERLAY_ADC_CATEGORY;
    if (preset.id === E_New) {
      addMutation.mutate({
        preset: {
          name: preset.title,
          fab_nm:
            mode === OVERLAY_ADC_CATEGORY ? adc_fab_name : correction_fab_name,
          mode: obj.setting.mode,
        },
        shots: obj.setting.shots,
        mode: presetMode,
      });
    } else {
      updateMutation.mutate({
        preset: { name: preset.title, mode: obj.setting.mode },
        shots: obj.setting.shots,
        mode: presetMode,
        preset_id: preset.id,
      });
    }
  };
  const deletePreset = (id) => {
    setLoading({ mode: 'delete', status: true });
    deleteMutation.mutate(id);
  };

  const selectPreset = (id) => {
    if ([E_Default, E_New].includes(id)) {
      setPreset({ id: id, title: id === E_Default ? E_Default : '' });
      if (id === E_Default) {
        updateShotInfo({
          mode:
            tab === E_CPVS_ADC_MEASUREMENT
              ? CPVS_MODE.FROM_LOG
              : CPVS_MODE.EACH,
          shots: defaultShotInfo,
        });
      }
    } else {
      setPreset({ id: id, title: obj.setting.preset[id] });
      setLoading({ mode: 'get', status: true });
    }
  };

  return (
    <>
      <Spin tip="Loading..." spinning={loading.status}>
        <div
          css={SG.contentItemStyle}
          className="column-3"
          style={{ paddingBottom: '10px' }}
        >
          <Tooltip
            placement="topLeft"
            title={MSG_TABLE_NAME_REGEXP}
            arrowPointAtCenter
          >
            <span className="label">{MSG_PRESET}</span>
            <QuestionCircleOutlined
              style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
            />
          </Tooltip>

          <Select
            style={{ width: '100%' }}
            onChange={(v) => selectPreset(v)}
            value={preset.id}
          >
            <Option value={E_Default} key={`option_default`}>
              {MSG_DEFAULT}
            </Option>
            ;
            {Object.entries(obj.setting?.preset ?? {}).map(([id, title]) => (
              <>
                <Option value={+id} key={`option_${id}`}>
                  {' '}
                  {title}
                  <Popconfirm
                    title={`Are you sure to delete Preset [${title}] ? `}
                    onConfirm={(e) => {
                      e.stopPropagation();
                      deletePreset(id);
                    }}
                  >
                    <Button
                      type="text"
                      icon={<DeleteOutlined />}
                      style={{ float: 'right' }}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </Popconfirm>
                </Option>
              </>
            ))}
            <Option value={E_New} key={`option_new`}>
              {MSG_NEW_PRESET}
            </Option>
            ;
          </Select>
          <div className="preset-setting" style={contentsStyle}>
            <InputForm.input
              formName={'Title'}
              placeholder="Enter preset name."
              value={preset.title}
              disabled={preset.id === E_Default}
              required={false}
              changeFunc={(e) =>
                setPreset({ ...preset, title: e?.Title ?? '' })
              }
              regExp={{
                pattern: TableNameRegex,
                message: '',
              }}
            />
            <button
              css={SG.antdButtonStyle}
              className="white"
              onClick={savePreset}
              disabled={
                preset.id === E_Default || !TableNameRegex.test(preset.title)
              }
            >
              {[E_Default, E_New].includes(preset.id)
                ? MSG_SAVE_PRESET
                : MSG_UPDATE_PRESET}
            </button>
          </div>
        </div>
      </Spin>
      <div css={SG.contentItemStyle} className="column-3">
        <CpVsMode
          mode={mode}
          tab={tab}
          value={obj?.setting.mode}
          disabled={obj.origin?.included === false}
        />
      </div>
    </>
  );
};
CpVsOption.propTypes = {
  mode: PropTypes.string,
  type: PropTypes.string,
  obj: PropTypes.object,
  tab: PropTypes.string,
};
export default CpVsOption;
