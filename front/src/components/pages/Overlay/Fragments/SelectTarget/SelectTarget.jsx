import React, { useMemo, useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  DatePicker,
  Divider,
  Input,
  Radio,
  Select,
  Space,
  Spin,
  TreeSelect,
} from 'antd';
import { PlayCircleOutlined, PlusCircleOutlined } from '@ant-design/icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faArrowLeft } from '@fortawesome/free-solid-svg-icons';
import dayjs from 'dayjs';
import useOverlayInfo from '../../../../../hooks/useOverlaySettingInfo';
import useModal from '../../../../../lib/util/modalControl/useModal';
import {
  get_Overlay_Remote_Equipment_Info,
  get_Overlay_Correction_Setting_Info,
  post_Overlay_Plate_Info,
} from '../../../../../lib/api/axios/useOverlayRequest';
import {
  DATE_FORMAT,
  OVERLAY_ADC_CATEGORY,
} from '../../../../../lib/api/Define/etc';
import { RenderSelectOptions } from '../../../JobAnalysis/AnalysisTable/functionGroup';
import {
  createTreeSelectData,
  createInitTreeValues,
  createPostData,
  disabledDate,
  initStageAdcInfo,
  startDisableCheck,
  process_Overlay_Start,
  displayError,
} from './functionGroup';
import * as SG from '../styleGroup';
import { CustomSelect, MeanAll } from './styleGroup';
import { MSG_LOCAL } from '../../../../../lib/api/Define/Message';
import { CommonRegex } from '../../../../../lib/util/RegExp';

const SelectTarget = ({ mode }) => {
  const { openModal, closeModal } = useModal();
  const {
    adcMeasurementSet,
    correctionSet,
    updateCorrectionSetting,
    updateAdcMeasurementSetting,
    updateOriginDataSetting,
  } = useOverlayInfo();

  const [fabName, setFabName] = useState('');
  const [loadState, setLoadState] = useState(false);
  const [radioAdc, setRadioAdc] = useState('');
  const [inputError, setInputError] = useState(false);

  const currentData = useMemo(
    () =>
      mode === OVERLAY_ADC_CATEGORY
        ? adcMeasurementSet.targetInfo
        : correctionSet.targetInfo,
    [adcMeasurementSet.targetInfo, correctionSet.targetInfo],
  );
  const lotIdOptions = useMemo(() => {
    return createTreeSelectData(
      currentData.lot_id_list,
      currentData.job,
      'lot',
    );
  }, [currentData.job]);
  const stageCorrectionOptions = useMemo(() => {
    return createTreeSelectData(
      currentData.stage_correction_list,
      'all',
      'stage',
    );
  }, [currentData.stage_correction_list]);
  const adcCorrectionOptions = useMemo(() => {
    return createTreeSelectData(
      currentData.adc_correction_list,
      radioAdc,
      'adc',
    );
  }, [currentData.adc_correction_list, radioAdc]);

  const checkName = () => {
    if (inputError) return;

    if (currentData.fab_list.includes(fabName) || !CommonRegex.test(fabName)) {
      setInputError(true);
    } else {
      changeRedux([...currentData.fab_list, fabName], 'fab_list');
    }
  };

  const changeFabName = (v) => {
    if (inputError) setInputError(false);
    setFabName(v);
  };

  const changeFab = async (v) => {
    if (mode !== OVERLAY_ADC_CATEGORY) {
      setLoadState(true);

      let tmpData = undefined;

      await get_Overlay_Correction_Setting_Info(v)
        .then((data) => {
          tmpData = data;
        })
        .catch((e) => displayError(e.response.data.msg))
        .finally(() => {
          setLoadState(false);
          if (tmpData) {
            const { radio, adc, stage } = initStageAdcInfo(
              tmpData.adc_correction ?? undefined,
              tmpData.stage_correction ?? undefined,
            );

            if (radio) {
              setRadioAdc(radio);
            }

            updateCorrectionSetting({
              ...correctionSet,
              targetInfo: {
                ...correctionSet.targetInfo,
                fab_name: v,
                equipment_name: '',
                stage_correction: stage
                  ? stage
                  : correctionSet.targetInfo.stage_correction,
                stage_correction_list:
                  tmpData.stage_correction ??
                  correctionSet.targetInfo.stage_correction_list,
                adc_correction: adc
                  ? adc
                  : correctionSet.targetInfo.adc_correction,
                adc_correction_list:
                  tmpData.adc_correction ??
                  correctionSet.targetInfo.adc_correction_list,
              },
            });
          } else {
            updateCorrectionSetting({
              ...correctionSet,
              targetInfo: {
                ...correctionSet.targetInfo,
                fab_name: v,
                equipment_name: '',
              },
            });
          }
        });
    } else {
      updateAdcMeasurementSetting({
        ...adcMeasurementSet,
        targetInfo: {
          ...currentData,
          fab_name: v,
          equipment_name: '',
        },
      });
    }
  };

  const changeRedux = (v, key, radio) => {
    if (mode === OVERLAY_ADC_CATEGORY) {
      updateAdcMeasurementSetting({
        ...adcMeasurementSet,
        targetInfo: { ...currentData, [key]: v },
      });
    } else {
      let tmpData =
        key === 'adc_correction_select' || key === 'adc_correction_radio'
          ? { ...currentData }
          : { ...currentData, [key]: v };

      if (key === 'adc_correction_select') {
        let curOptionList = { ...tmpData.adc_correction_list[radioAdc] };
        Object.keys(curOptionList).forEach((x) => {
          if (x !== 'selected') {
            curOptionList[x] =
              v.find((y) => y.split('-')[1] === x) !== undefined;
          }
        });

        tmpData = {
          ...tmpData,
          adc_correction_list: {
            ...tmpData.adc_correction_list,
            [radioAdc]: curOptionList,
          },
          adc_correction: v,
        };
      }

      if (key === 'adc_correction_radio') {
        Object.keys(tmpData.adc_correction_list).forEach((x) => {
          let curOptionList = { ...tmpData.adc_correction_list[x] };
          curOptionList.selected = x === radio;

          tmpData = {
            ...tmpData,
            adc_correction_list: {
              ...tmpData.adc_correction_list,
              [x]: curOptionList,
            },
            adc_correction: v,
          };
        });
      }

      updateCorrectionSetting({
        ...correctionSet,
        targetInfo: tmpData,
      });
    }
  };

  const changeEquipment = async (v) => {
    setLoadState(true);
    let tmpData = undefined;

    await get_Overlay_Remote_Equipment_Info({
      category: mode,
      db_id:
        mode === OVERLAY_ADC_CATEGORY
          ? adcMeasurementSet.source_info.db.id
          : correctionSet.source_info.db.id,
      fab: currentData.fab_name,
      equipment_name: v,
    })
      .then((data) => {
        tmpData = data;
      })
      .catch((e) => displayError(e.response.data.msg))
      .finally(() => {
        setLoadState(false);
        if (tmpData) {
          const periodSet =
            tmpData.period.length > 0 ? tmpData.period : undefined;
          if (mode === OVERLAY_ADC_CATEGORY) {
            updateAdcMeasurementSetting({
              ...adcMeasurementSet,
              source_info: {
                ...adcMeasurementSet.source_info,
                files_rid: tmpData.rid,
              },
              targetInfo: {
                ...adcMeasurementSet.targetInfo,
                equipment_name: v,
                period: periodSet ?? adcMeasurementSet.targetInfo.period,
                selected: periodSet ?? adcMeasurementSet.targetInfo.selected,
                job: tmpData.job ? '' : adcMeasurementSet.targetInfo.job,
                job_list: tmpData.job ?? adcMeasurementSet.targetInfo.job_list,
                lot_id: tmpData.lot_id
                  ? []
                  : adcMeasurementSet.targetInfo.lot_id,
                lot_id_list:
                  tmpData.lot_id ?? adcMeasurementSet.targetInfo.lot_id_list,
                mean_dev_diff: tmpData.plate
                  ? []
                  : adcMeasurementSet.targetInfo.mean_dev_diff,
                mean_dev_diff_list:
                  tmpData.plate ??
                  adcMeasurementSet.targetInfo.mean_dev_diff_list,
              },
            });
          } else {
            updateCorrectionSetting({
              ...correctionSet,
              source_info: {
                ...correctionSet.source_info,
                files_rid: tmpData.rid,
              },
              targetInfo: {
                ...correctionSet.targetInfo,
                equipment_name: v,
                period: periodSet ?? correctionSet.targetInfo.period,
                selected: periodSet ?? correctionSet.targetInfo.selected,
                job: tmpData.job ? '' : correctionSet.targetInfo.job,
                job_list: tmpData.job ?? correctionSet.targetInfo.job_list,
                lot_id: tmpData.lot_id ? [] : correctionSet.targetInfo.lot_id,
                lot_id_list:
                  tmpData.lot_id ?? correctionSet.targetInfo.lot_id_list,
                mean_dev_diff: tmpData.plate
                  ? []
                  : correctionSet.targetInfo.mean_dev_diff,
                mean_dev_diff_list:
                  tmpData.plate ?? correctionSet.targetInfo.mean_dev_diff_list,
                stage_correction: tmpData.stage_correction
                  ? []
                  : correctionSet.targetInfo.stage_correction,
                stage_correction_list:
                  tmpData.stage_correction ??
                  correctionSet.targetInfo.stage_correction_list,
                adc_correction: tmpData.adc_correction
                  ? []
                  : correctionSet.targetInfo.adc_correction,
                adc_correction_list:
                  tmpData.adc_correction ??
                  correctionSet.targetInfo.adc_correction_list,
              },
            });
          }
        } else {
          changeRedux(v, 'equipment_name');
        }
      });
  };

  const changeMeanAll = (v) => {
    if (mode === OVERLAY_ADC_CATEGORY) {
      updateAdcMeasurementSetting({
        ...adcMeasurementSet,
        targetInfo: {
          ...adcMeasurementSet.targetInfo,
          mean_dev_diff: v ? currentData.mean_dev_diff_list : [],
        },
      });
    } else {
      updateCorrectionSetting({
        ...correctionSet,
        targetInfo: {
          ...correctionSet.targetInfo,
          mean_dev_diff: v ? currentData.mean_dev_diff_list : [],
        },
      });
    }
  };

  const changeRadio = (v) => {
    setRadioAdc(v);
    changeRedux(
      createInitTreeValues(
        currentData.adc_correction_list,
        'adc_correction',
        v,
      ),
      'adc_correction_radio',
      v,
    );
  };

  const processStart = async () => {
    const postData = createPostData(
      mode === OVERLAY_ADC_CATEGORY ? adcMeasurementSet : correctionSet,
      mode,
    );
    await process_Overlay_Start({
      postData,
      openModal,
      updateOriginDataSetting,
      closeModal,
      mode,
    });
  };

  useEffect(() => {
    if (mode !== OVERLAY_ADC_CATEGORY && radioAdc === '') {
      const { radio, adc, stage } = initStageAdcInfo(
        currentData.adc_correction_list,
        currentData.stage_correction_list,
      );

      if (radio) {
        setRadioAdc(radio);
      }

      updateCorrectionSetting({
        ...correctionSet,
        targetInfo: {
          ...correctionSet.targetInfo,
          stage_correction: stage
            ? stage
            : correctionSet.targetInfo.stage_correction,
          adc_correction: adc ? adc : correctionSet.targetInfo.adc_correction,
        },
      });
    }
  }, [currentData.adc_correction_list, currentData.stage_correction_list]);

  useEffect(() => {
    const fetch = async (cat, id, data) => {
      setLoadState(true);

      await post_Overlay_Plate_Info(cat, id, data)
        .then((data) => {
          if (mode === OVERLAY_ADC_CATEGORY) {
            updateAdcMeasurementSetting({
              ...adcMeasurementSet,
              targetInfo: {
                ...adcMeasurementSet.targetInfo,
                mean_dev_diff: [],
                mean_dev_diff_list: data.plate,
              },
            });
          } else {
            updateCorrectionSetting({
              ...correctionSet,
              targetInfo: {
                ...correctionSet.targetInfo,
                mean_dev_diff: [],
                mean_dev_diff_list: data.plate,
              },
            });
          }
        })
        .catch((e) => {
          displayError(e.response.data.msg);
        })
        .finally(() => {
          setLoadState(false);
        });
    };

    const rid =
      mode === OVERLAY_ADC_CATEGORY
        ? adcMeasurementSet.source_info.files_rid
        : correctionSet.source_info.files_rid;

    if (
      currentData.job !== '' &&
      currentData.lot_id.length > 0 &&
      rid !== '' &&
      currentData.selected[0] !== ''
    ) {
      fetch(mode, rid, {
        period: currentData.selected.join('~'),
        job: currentData.job,
        lot_id: currentData.lot_id.map((v) => {
          if (v.match(/LOTID/)) {
            return v.substr(v.indexOf('LOTID'));
          } else {
            const splitStr = v.split('-');
            return splitStr[splitStr.length - 1];
          }
        }),
      });
    }
  }, [currentData.job, currentData.lot_id]);

  return (
    <div css={SG.componentStyle}>
      <div
        className={
          'foreground' +
          ((mode === OVERLAY_ADC_CATEGORY &&
            ((adcMeasurementSet.source === MSG_LOCAL &&
              adcMeasurementSet.source_info.files_rid === '') ||
              (adcMeasurementSet.source !== MSG_LOCAL &&
                adcMeasurementSet.source_info.db.id === ''))) ||
          (mode !== OVERLAY_ADC_CATEGORY &&
            ((correctionSet.source === MSG_LOCAL &&
              correctionSet.source_info.files_rid === '') ||
              (correctionSet.source !== MSG_LOCAL &&
                correctionSet.source_info.db.id === '')))
            ? ' active'
            : '')
        }
      >
        <div>
          <FontAwesomeIcon icon={faArrowLeft} size="10x" />
          <p>Please first set the left.</p>
        </div>
      </div>
      <Spin size="large" tip="Loading..." spinning={loadState} />
      <div css={SG.componentTitleStyle}>Select Target</div>
      <div css={SG.contentWrapperStyle} className="mg-bottom">
        <div css={SG.contentStyle}>
          <div css={SG.contentItemStyle} className="column-2">
            <span className="label">Fab</span>
            <Select
              style={{ width: '100%' }}
              value={currentData.fab_name}
              onChange={(v) => changeFab(v)}
              dropdownRender={(menu) =>
                (mode === OVERLAY_ADC_CATEGORY &&
                  adcMeasurementSet.source === MSG_LOCAL) ||
                (mode !== OVERLAY_ADC_CATEGORY &&
                  correctionSet.source === MSG_LOCAL) ? (
                  <>
                    <CustomSelect>
                      <Input
                        type="text"
                        style={{ width: '100%' }}
                        value={fabName}
                        onChange={(e) => changeFabName(e.target.value)}
                        maxLength="30"
                        className={inputError ? 'input-error' : ''}
                      />
                      <div
                        className={'button' + (inputError ? ' error' : '')}
                        role="button"
                        onKeyDown={undefined}
                        tabIndex="-1"
                        onClick={checkName}
                      >
                        <PlusCircleOutlined />
                      </div>
                    </CustomSelect>
                    <Divider style={{ margin: '4px 0' }} />
                    {menu}
                  </>
                ) : (
                  menu
                )
              }
            >
              {currentData.fab_list.length === 0
                ? ''
                : currentData.fab_list.map(RenderSelectOptions)}
            </Select>
          </div>
          <div css={SG.contentItemStyle} className="column-2">
            <span className="label">Equipment</span>
            <Select
              style={{ width: '100%' }}
              value={currentData.equipment_name}
              onChange={changeEquipment}
              disabled={
                mode === OVERLAY_ADC_CATEGORY
                  ? adcMeasurementSet.source === MSG_LOCAL
                  : correctionSet.source === MSG_LOCAL
              }
            >
              {currentData.fab_name === ''
                ? ''
                : currentData.equipment_name_list[currentData.fab_name]?.map(
                    RenderSelectOptions,
                  )}
            </Select>
          </div>
          <div css={SG.contentItemStyle} className="column-2">
            <span className="label">Period</span>
            <DatePicker.RangePicker
              value={
                currentData.selected[0] !== ''
                  ? [
                      dayjs(currentData.selected[0]),
                      dayjs(currentData.selected[1]),
                    ]
                  : currentData.period
              }
              placeholder={
                currentData.period[0] !== ''
                  ? [
                      dayjs(currentData.period[0]).format(DATE_FORMAT),
                      dayjs(currentData.period[1]).format(DATE_FORMAT),
                    ]
                  : currentData.period
              }
              onChange={(v) =>
                changeRedux(
                  [
                    dayjs(v[0]).format(DATE_FORMAT),
                    dayjs(v[1]).format(DATE_FORMAT),
                  ],
                  'selected',
                )
              }
              style={{ width: '100%' }}
              disabledDate={(v) => disabledDate(currentData.period, v)}
              inputReadOnly
              allowClear={false}
              showTime
            />
          </div>
          <div css={SG.contentItemStyle} className="column-2">
            <span className="label">Job</span>
            <Select
              style={{ width: '100%' }}
              value={currentData.job}
              onChange={(v) => changeRedux(v, 'job')}
            >
              {currentData.job_list.map(RenderSelectOptions)}
            </Select>
          </div>
          <div css={SG.contentItemStyle} className="column-2">
            <span className="label">Lot ID</span>
            <TreeSelect
              treeData={lotIdOptions}
              value={currentData.lot_id}
              onChange={(v) => changeRedux(v, 'lot_id')}
              showCheckedStrategy={TreeSelect.SHOW_CHILD}
              style={{ width: '100%' }}
              maxTagCount="responsive"
              treeCheckable
              treeDefaultExpandAll
            />
          </div>
          {currentData.job === '' || currentData.lot_id.length === 0 ? (
            ''
          ) : (
            <div css={SG.contentItemStyle} className="column-2">
              <span className="label">Mean Deviation Diff</span>
              <Select
                style={{ width: '100%' }}
                mode="multiple"
                maxTagCount="responsive"
                value={currentData.mean_dev_diff}
                onChange={(v) => changeRedux(v, 'mean_dev_diff')}
                dropdownRender={(menu) =>
                  currentData.mean_dev_diff_list.length > 0 ? (
                    <>
                      <MeanAll>
                        <label htmlFor="mean-all">
                          <input
                            type="checkbox"
                            id="mean-all"
                            onChange={(e) => changeMeanAll(e.target.checked)}
                          />
                          <div className="button">All</div>
                        </label>
                      </MeanAll>
                      {menu}
                    </>
                  ) : (
                    menu
                  )
                }
              >
                {currentData.mean_dev_diff_list.length === 0
                  ? ''
                  : currentData.mean_dev_diff_list.map(RenderSelectOptions)}
              </Select>
            </div>
          )}
          <div css={SG.contentItemStyle} className="column-2">
            <span className="label">AE Correction</span>
            <Select
              style={{ width: '100%' }}
              value={currentData.ae_correction}
              onChange={(v) => changeRedux(v, 'ae_correction')}
            >
              <Select.Option value="off">Off</Select.Option>
              <Select.Option value="mode0">Shift/RotCorrection</Select.Option>
              <Select.Option value="mode1">
                Shift/RotCorrection/MagCorrection
              </Select.Option>
            </Select>
          </div>
          {mode !== OVERLAY_ADC_CATEGORY ? (
            <>
              <div css={SG.contentItemStyle} className="column-2">
                <span className="label">Stage Correction</span>
                <TreeSelect
                  treeData={stageCorrectionOptions}
                  value={currentData.stage_correction}
                  onChange={(v) => changeRedux(v, 'stage_correction')}
                  showCheckedStrategy={TreeSelect.SHOW_CHILD}
                  style={{ width: '100%' }}
                  maxTagCount="responsive"
                  treeCheckable
                  treeDefaultExpandAll
                />
              </div>
              <div css={SG.contentItemStyle} className="column-2">
                <span className="label">ADC Correction</span>
                <TreeSelect
                  treeData={adcCorrectionOptions}
                  value={currentData.adc_correction}
                  onChange={(v) => changeRedux(v, 'adc_correction_select')}
                  showCheckedStrategy={TreeSelect.SHOW_CHILD}
                  style={{ width: '100%' }}
                  maxTagCount="responsive"
                  treeCheckable
                  treeDefaultExpandAll
                  dropdownRender={(menu) =>
                    adcCorrectionOptions.length > 0 ? (
                      <>
                        <div style={{ padding: '8px' }}>
                          <Radio.Group
                            value={radioAdc}
                            onChange={(e) => changeRadio(e.target.value)}
                          >
                            <Space direction="vertical">
                              <Radio value="ADC Measurement">
                                ADC Measurement
                              </Radio>
                              <Radio value="ADC Offset">ADC Offset</Radio>
                              <Radio value="ADC Measurement + Offset">
                                ADC Measurement + Offset
                              </Radio>
                            </Space>
                          </Radio.Group>
                        </div>
                        {menu}
                      </>
                    ) : (
                      menu
                    )
                  }
                />
              </div>
            </>
          ) : (
            ''
          )}
        </div>
        <button
          css={SG.customButtonStyle}
          className="absolute"
          onClick={processStart}
          disabled={startDisableCheck(mode, currentData)}
        >
          <PlayCircleOutlined />
          <span>Start</span>
        </button>
      </div>
    </div>
  );
};
SelectTarget.propTypes = {
  mode: PropTypes.string,
};
SelectTarget.defaultProps = {
  mode: OVERLAY_ADC_CATEGORY,
};

export default SelectTarget;
