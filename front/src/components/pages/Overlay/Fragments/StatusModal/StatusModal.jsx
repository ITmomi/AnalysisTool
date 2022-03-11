import React, { useEffect, useState } from 'react';
import styled from '@emotion/styled';
import PropTypes from 'prop-types';
import { Modal, Button, Progress } from 'antd';
import { getStatus, getAnalysisInfo } from './functionGroup';
import useOverlayInfo from '../../../../../hooks/useOverlaySettingInfo';
import { OVERLAY_ADC_CATEGORY } from '../../../../../lib/api/Define/etc';
import useModal from '../../../../../lib/util/modalControl/useModal';
import ProcessingModal from '../ProcessingModal/ProcessingModal';
import { displayNotification } from '../../../JobAnalysis/functionGroup';
import { MSG_LOCAL } from '../../../../../lib/api/Define/Message';

const Contents = styled.div`
  display: flex;
  justify-content: space-around;
  align-items: center;
  & > div {
    &:first-of-type {
      display: flex;
      flex-direction: column;
      row-gap: 1rem;
    }
  }
`;

const StatusModal = ({ id, category, onClose }) => {
  const { openModal, closeModal } = useModal();
  const {
    adcMeasurementSet,
    correctionSet,
    updateAdcMeasurementSetting,
    updateCorrectionSetting,
  } = useOverlayInfo();
  const [statusInfo, setStatusInfo] = useState({
    status: 'running',
    percent: 0,
    detail: {
      error_files: 0,
      success_files: 0,
      total_files: 0,
      converted: 0,
    },
  });

  useEffect(() => {
    if (statusInfo.status === 'running') {
      const interval = setInterval(() => {
        getStatus(id, category, setStatusInfo)
          .then((data) => {
            setStatusInfo(
              data
                ? data
                : {
                    ...statusInfo,
                    status: 'error',
                  },
            );
          })
          .catch((e) => console.log(e));
      }, 1500);
      return () => clearInterval(interval);
    } else {
      if (statusInfo.status === 'success') {
        let receivedData = undefined,
          isError = undefined;

        onClose();
        openModal(ProcessingModal, {
          title: 'Analysing',
          message: 'Analysing data',
        });

        getAnalysisInfo(id, category)
          .then((data) => (receivedData = data))
          .catch((e) => {
            isError = e.response.data.msg;
          })
          .finally(() => {
            if (receivedData) {
              const newTargetData = {
                fab_name: '',
                fab_list: receivedData.fab ?? [],
                equipment_name: '',
                equipment_name_list: {},
                period: receivedData.period ?? ['', ''],
                selected: receivedData.period ?? ['', ''],
                job: '',
                job_list: receivedData.job ?? [],
                lot_id: [],
                lot_id_list: receivedData.lot_id ?? [],
                mean_dev_diff: [],
                mean_dev_diff_list: receivedData.plate ?? [],
                stage_correction: [],
                stage_correction_list: receivedData.stage_correction ?? {},
                adc_correction: [],
                adc_correction_list: receivedData.adc_correction ?? {},
              };

              category === OVERLAY_ADC_CATEGORY
                ? updateAdcMeasurementSetting({
                    ...adcMeasurementSet,
                    targetInfo: {
                      ...adcMeasurementSet.targetInfo,
                      ...newTargetData,
                    },
                  })
                : updateCorrectionSetting({
                    ...correctionSet,
                    targetInfo: {
                      ...correctionSet.targetInfo,
                      ...newTargetData,
                    },
                  });
            } else {
              category === OVERLAY_ADC_CATEGORY
                ? updateAdcMeasurementSetting({
                    ...adcMeasurementSet,
                    source_info: {
                      files_rid:
                        adcMeasurementSet.source === MSG_LOCAL
                          ? ''
                          : adcMeasurementSet.source_info.files_rid,
                      db:
                        adcMeasurementSet.source !== MSG_LOCAL
                          ? { id: '', name: '' }
                          : adcMeasurementSet.source_info.db,
                    },
                  })
                : updateCorrectionSetting({
                    ...correctionSet,
                    source_info: {
                      files_rid:
                        correctionSet.source === MSG_LOCAL
                          ? ''
                          : correctionSet.source_info.files_rid,
                      db:
                        correctionSet.source !== MSG_LOCAL
                          ? { id: '', name: '' }
                          : correctionSet.source_info.db,
                    },
                  });
            }
            closeModal(ProcessingModal);
            displayNotification({
              message: isError ? 'Error occurred' : 'Analysis Success',
              description: isError ?? 'The analysis was successful.',
              duration: 3,
              style: isError
                ? { borderLeft: '5px solid red' }
                : { borderLeft: '5px solid green' },
            });
          });
      }
    }
  }, [statusInfo.status]);

  return (
    <Modal
      visible
      centered
      title={
        statusInfo.status === 'running'
          ? 'PROCESS'
          : statusInfo.status === 'success'
          ? 'COMPLETE'
          : 'ERROR'
      }
      width={400}
      footer={[
        <Button key="button" type="primary" onClick={onClose}>
          {statusInfo.status === 'running' ? 'Cancel' : 'Close'}
        </Button>,
      ]}
      closable={false}
    >
      <Contents>
        <div>
          <div>{`Success files: ${statusInfo.detail.success_files}`}</div>
          <div>{`Error files: ${statusInfo.detail.error_files}`}</div>
          <div>{`Total files: ${statusInfo.detail.total_files}`}</div>
          <div>{`Converted rows: ${statusInfo.detail.converted}`}</div>
        </div>
        <div>
          <Progress
            type="circle"
            percent={statusInfo.percent}
            status={
              statusInfo.status === 'running'
                ? 'normal'
                : statusInfo.status === 'success'
                ? 'success'
                : 'exception'
            }
          />
        </div>
      </Contents>
    </Modal>
  );
};
StatusModal.propTypes = {
  id: PropTypes.string.isRequired,
  category: PropTypes.string.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default StatusModal;
