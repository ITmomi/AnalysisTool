import React, { useEffect, useState } from 'react';
import * as SG from '../styleGroup';
import OffsetSetting from '../MapSetting/OffsetSetting';
import CpVsSetting from '../MapSetting/CpVsSetting';
import EtcSetting from '../MapSetting/EtcSetting';
import PropTypes from 'prop-types';
import {
  MSG_RE_START,
  MSG_SETTING,
} from '../../../../../lib/api/Define/Message';
import {
  E_OVERLAY_COMPONENT,
  E_OVERLAY_IMAGE,
  E_OVERLAY_MAP,
  E_OVERLAY_REPRODUCIBILITY,
  E_OVERLAY_VARIATION,
  OVERLAY_ADC_CATEGORY,
} from '../../../../../lib/api/Define/etc';
import ThreeSigmaRangeSetting from '../ReproducibilitySetting/ThreeSigmaRangeSetting';
import RangeAndShotSetting from '../VariationSetting/RangeAndShotSetting';
import { process_Overlay_Start } from '../SelectTarget/functionGroup';
import useOverlaySettingInfo from '../../../../../hooks/useOverlaySettingInfo';
import useModal from '../../../../../lib/util/modalControl/useModal';
import { PlayCircleOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import useOverlayResultInfo from '../../../../../hooks/useOverlayResultInfo';
import ProcessingModal from '../ProcessingModal/ProcessingModal';
import Coordinate from '../../../../../static/arrows_icon.svg';
import { Button, Popover } from 'antd';
import { css } from '@emotion/react';
const coordinate_style = css`
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 75%;
`;

const coordinateImgStyle = css`
  font-weight: 700;
  & img {
    transform: rotate(135deg);
    padding: 3rem;
  }
`;
const ResultGraphSetting = ({ mode, type, UpdateGraph }) => {
  const {
    adcMeasurementSet,
    correctionSet,
    updateOriginDataSetting,
    getReAnalysisParameter,
  } = useOverlaySettingInfo();
  const {
    gCorrectionMap,
    gMap,
    gCorrectionData,
    gAdcMeasurementData,
  } = useOverlayResultInfo();
  const { openModal, closeModal } = useModal();
  const [reStart, setRestart] = useState(false);
  const [isReAnalysis, setReAnalysis] = useState(false);
  const reAnalysis = async (start) => {
    if (start && isReAnalysis === false) {
      openModal(ProcessingModal, {
        title: 'Graph drawing',
        message: 'just moment please',
      });
      setTimeout(() => UpdateGraph.func(true), 1000);
    } else {
      let postData = getReAnalysisParameter(
        mode,
        mode === OVERLAY_ADC_CATEGORY ? adcMeasurementSet : correctionSet,
      );
      await process_Overlay_Start({
        postData,
        openModal,
        closeModal,
        mode,
        updateOriginDataSetting,
      }).then(() => {
        UpdateGraph.func(true);
      });
    }
  };
  useEffect(() => {
    if (reStart === false) {
      console.log('enable re-start');
      setRestart(true);
    }
  }, [gMap, gCorrectionMap]);

  useEffect(() => {
    if (
      (mode === OVERLAY_ADC_CATEGORY
        ? gAdcMeasurementData
        : gCorrectionData) !== undefined
    ) {
      setReAnalysis(true);
      console.log('need Analysis process!!!');
    }
  }, [gMap.cp_vs, gCorrectionMap.cp_vs]);

  useEffect(() => {
    if ((UpdateGraph?.update ?? false) === false) {
      setReAnalysis(false);
      setRestart(false);
      closeModal(ProcessingModal);
      console.log('Analysis process!!! completed');
    }
    console.log('UpdateGraph.update', UpdateGraph?.update);
  }, [UpdateGraph.update]);

  const CoordinateContent = (
    <>
      <div css={coordinateImgStyle}>
        <img src={Coordinate} alt={'Coordinate'} />
      </div>
    </>
  );

  return (
    <>
      <div className="header">
        <div className="coordinate_test">
          {type.title} {MSG_SETTING}
          {[E_OVERLAY_IMAGE, E_OVERLAY_COMPONENT, E_OVERLAY_MAP].includes(
            type.id,
          ) ? (
            <span style={coordinate_style}>
              <Popover
                content={CoordinateContent}
                title="Coordinate"
                trigger="hover"
              >
                <Button
                  shape="circle"
                  type="text"
                  icon={<QuestionCircleOutlined />}
                />
              </Popover>
            </span>
          ) : (
            <></>
          )}
        </div>
        <div>
          {[E_OVERLAY_IMAGE, E_OVERLAY_COMPONENT, E_OVERLAY_MAP].includes(
            type.id,
          ) ? (
            <button
              css={SG.customButtonStyle}
              className="blue"
              onClick={() => reAnalysis(true)}
              disabled={reStart === false}
            >
              <PlayCircleOutlined />
              <span>{MSG_RE_START}</span>
            </button>
          ) : (
            <></>
          )}
        </div>
      </div>
      <div className="main">
        {[E_OVERLAY_COMPONENT, E_OVERLAY_IMAGE, E_OVERLAY_MAP].includes(
          type.id,
        ) ? (
          <>
            <OffsetSetting mode={mode} type={type.id} />
            <CpVsSetting mode={mode} type={type.id} />
            <EtcSetting mode={mode} type={type.id} />
          </>
        ) : type.id === E_OVERLAY_VARIATION ? (
          <RangeAndShotSetting />
        ) : type.id === E_OVERLAY_REPRODUCIBILITY ? (
          <ThreeSigmaRangeSetting />
        ) : (
          <></>
        )}
      </div>
    </>
  );
};
ResultGraphSetting.propTypes = {
  mode: PropTypes.string,
  type: PropTypes.object,
  UpdateGraph: PropTypes.object,
};
export default ResultGraphSetting;
