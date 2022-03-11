import React, { useState, useMemo } from 'react';
import PropTypes from 'prop-types';
import { Button, Select, Upload, Spin } from 'antd';
import { InboxOutlined, UploadOutlined } from '@ant-design/icons';
import useModal from '../../../../../lib/util/modalControl/useModal';
import useOverlayInfo from '../../../../../hooks/useOverlaySettingInfo';
import useMgmtInfo from '../../../../../hooks/useMgmtInfo';
import {
  post_Overlay_Local_FilesUpload,
  get_Overlay_Remote_Info,
} from '../../../../../lib/api/axios/useOverlayRequest';
import { OVERLAY_ADC_CATEGORY } from '../../../../../lib/api/Define/etc';
import { overlay_source } from '../../../../../lib/api/Define/OverlayDefault';
import { MSG_LOCAL, MSG_REMOTE } from '../../../../../lib/api/Define/Message';
import { RenderSelectOptions } from '../../../JobAnalysis/AnalysisTable/functionGroup';
import StatusModal from '../StatusModal/StatusModal';
import ProcessingModal from '../ProcessingModal/ProcessingModal';
import * as SG from '../styleGroup';
import { displayError } from '../SelectTarget/functionGroup';

const SelectSource = ({ mode }) => {
  const { openModal, closeModal } = useModal();
  const {
    adcMeasurementSet,
    correctionSet,
    updateAdcMeasurementSetting,
    updateCorrectionSetting,
  } = useOverlayInfo();
  const { ManagementInfo } = useMgmtInfo();

  const [loadState, setLoadState] = useState(false);
  const [addedFiles, setAddedFiles] = useState([]);

  const currentData = useMemo(() => {
    return mode === OVERLAY_ADC_CATEGORY ? adcMeasurementSet : correctionSet;
  }, [adcMeasurementSet, correctionSet]);
  const dbOptionList = useMemo(() => {
    if (currentData.source === MSG_REMOTE) {
      const result = [];
      const items =
        ManagementInfo.find((v) => v.target === MSG_REMOTE)?.items ?? [];

      if (items.length > 0) {
        items.reduce((acc, v) => {
          acc.push({ id: v.id, name: v.name });
          return acc;
        }, result);
      }

      return result;
    }
  }, [
    currentData.source,
    ManagementInfo.find((v) => v.target === MSG_REMOTE)?.items,
  ]);

  const changeFrom = (v) => {
    if (mode === OVERLAY_ADC_CATEGORY) {
      updateAdcMeasurementSetting({
        ...currentData,
        source: v,
      });
    } else {
      updateCorrectionSetting({
        ...currentData,
        source: v,
      });
    }
  };

  const changeRemote = async (v) => {
    setLoadState(true);

    await get_Overlay_Remote_Info({
      category: mode,
      db_id: v,
    })
      .then((data) => {
        if (mode === OVERLAY_ADC_CATEGORY) {
          updateAdcMeasurementSetting({
            ...adcMeasurementSet,
            source: MSG_REMOTE,
            source_info: {
              ...adcMeasurementSet.source_info,
              db: dbOptionList.find((x) => x.id === v),
            },
            targetInfo: {
              ...adcMeasurementSet.targetInfo,
              fab_name: '',
              equipment_name: '',
              period: ['', ''],
              selected: ['', ''],
              job: '',
              job_list: [],
              lot_id: [],
              lot_id_list: {},
              mean_dev_diff: [],
              mean_dev_diff_list: [],
              stage_correction: [],
              stage_correction_list: {},
              adc_correction: [],
              adc_correction_list: {},
              fab_list: data.fab ?? [],
              equipment_name_list: data.equipments ?? [],
            },
          });
        } else {
          updateCorrectionSetting({
            ...correctionSet,
            source: MSG_REMOTE,
            source_info: {
              ...correctionSet.source_info,
              db: dbOptionList.find((x) => x.id === v),
            },
            targetInfo: {
              ...correctionSet.targetInfo,
              fab_name: '',
              equipment_name: '',
              period: ['', ''],
              selected: ['', ''],
              job: '',
              job_list: [],
              lot_id: [],
              lot_id_list: {},
              mean_dev_diff: [],
              mean_dev_diff_list: [],
              stage_correction: [],
              stage_correction_list: {},
              adc_correction: [],
              adc_correction_list: {},
              fab_list: data.fab ?? [],
              equipment_name_list: data.equipments ?? [],
            },
          });
        }
      })
      .catch((e) => displayError(e.response.data.msg))
      .finally(() => setLoadState(false));
  };

  const processStart = async () => {
    const formData = new FormData();
    let upload_id = undefined;

    addedFiles.forEach((v) => {
      formData.append('files', v);
    });
    formData.append('category', mode);

    openModal(ProcessingModal, {
      title: 'Converting',
      message: 'Converting files',
    });

    await post_Overlay_Local_FilesUpload(formData)
      .then((id) => (upload_id = id.upload_id))
      .catch((e) => displayError(e.response.data.msg))
      .finally(() => closeModal(ProcessingModal));

    if (upload_id && upload_id !== '0') {
      if (mode === OVERLAY_ADC_CATEGORY) {
        updateAdcMeasurementSetting({
          ...adcMeasurementSet,
          source_info: {
            ...adcMeasurementSet.source_info,
            files_rid:
              adcMeasurementSet.source !== MSG_REMOTE
                ? upload_id
                : adcMeasurementSet.source_info.files_rid,
          },
        });
      } else {
        updateCorrectionSetting({
          ...correctionSet,
          source_info: {
            ...correctionSet.source_info,
            files_rid:
              correctionSet.source !== MSG_REMOTE
                ? upload_id
                : correctionSet.source_info.files_rid,
          },
        });
      }

      openModal(StatusModal, {
        id: upload_id,
        category: mode,
      });
    }
  };

  return (
    <div css={SG.componentStyle} className="stretch">
      <Spin size="large" tip="Loading..." spinning={loadState} />
      <div css={SG.componentTitleStyle}>Select Source</div>
      <div css={SG.contentWrapperStyle}>
        <div css={SG.contentStyle} className="full-width">
          <div css={SG.contentItemStyle} className="column-2">
            <span className="label">From</span>
            <Select
              value={currentData.source}
              style={{ width: '100%' }}
              onChange={changeFrom}
            >
              {overlay_source.map(RenderSelectOptions)}
            </Select>
          </div>
          {currentData.source === MSG_LOCAL ? (
            <div css={SG.contentItemStyle} className="upload column-2">
              <span className="label">Log Files</span>
              {mode === OVERLAY_ADC_CATEGORY ? (
                <Upload.Dragger
                  onChange={(e) => {
                    setAddedFiles(
                      e.fileList.length > 0
                        ? e.fileList.map((v) => v.originFileObj)
                        : [],
                    );
                  }}
                  beforeUpload={() => false}
                >
                  <p className="ant-upload-drag-icon">
                    <InboxOutlined />
                  </p>
                  <p className="ant-upload-text">
                    Click or drag file to this area to upload
                  </p>
                </Upload.Dragger>
              ) : (
                <Upload
                  onChange={(e) => {
                    setAddedFiles(
                      e.fileList.length > 0
                        ? [e.fileList[0].originFileObj]
                        : [],
                    );
                  }}
                  beforeUpload={() => false}
                  maxCount="1"
                  className="full-width"
                >
                  <Button icon={<UploadOutlined />}>Upload zip only</Button>
                </Upload>
              )}
            </div>
          ) : (
            <div css={SG.contentItemStyle} className="column-2">
              <span className="label">DB From</span>
              <Select
                style={{ width: '100%' }}
                value={currentData.source_info.db.id}
                onSelect={changeRemote}
              >
                {dbOptionList?.map((db) => {
                  return (
                    <Select.Option value={db.id} key={db.id}>
                      {db.name}
                    </Select.Option>
                  );
                }) ?? <></>}
              </Select>
            </div>
          )}
        </div>
      </div>
      {currentData.source === MSG_LOCAL ? (
        <div className="source-button-wrapper">
          <button
            css={SG.antdButtonStyle}
            className="white"
            disabled={addedFiles.length === 0}
            onClick={processStart}
          >
            Load Start
          </button>
        </div>
      ) : (
        ''
      )}
    </div>
  );
};
SelectSource.propTypes = {
  mode: PropTypes.string,
};

export default SelectSource;
