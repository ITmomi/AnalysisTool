import React, { useMemo } from 'react';
import { CloudDownloadOutlined } from '@ant-design/icons';
import {
  MSG_DOWNLOAD,
  MSG_X,
  MSG_Y,
} from '../../../../../lib/api/Define/Message';
import * as SG from '../styleGroup';
import { postFormdataRequestExport } from '../../../../../lib/api/axios/requests';
import { URL_EXPORT_OVERLAY } from '../../../../../lib/api/Define/URL';
import useOverlaySettingInfo from '../../../../../hooks/useOverlaySettingInfo';
import PropTypes from 'prop-types';
import {
  E_OVERLAY_ANOVA,
  E_OVERLAY_COMPONENT,
  E_OVERLAY_IMAGE,
  E_OVERLAY_REPRODUCIBILITY,
  E_OVERLAY_VARIATION,
  OVERLAY_ADC_CATEGORY,
} from '../../../../../lib/api/Define/etc';
import { getGraphImage2, jsonToCSV } from '../../../../../lib/util/plotly-test';
import useOverlayResultInfo from '../../../../../hooks/useOverlayResultInfo';

const ResultDownload = ({ mode, Update }) => {
  const {
    correctionSet,
    adcMeasurementSet,
    getReAnalysisParameter,
  } = useOverlaySettingInfo();
  const {
    gCorrectionData,
    gAdcMeasurementData,
    gCorrectionMap,
    gMap,
    gVariation,
    gAnova,
    gReproducibility,
    getAnovaTableFuc,
  } = useOverlayResultInfo();
  const originInfo = useMemo(() => {
    return mode === OVERLAY_ADC_CATEGORY ? adcMeasurementSet : correctionSet;
  }, [gAdcMeasurementData, gCorrectionData]);
  const MapSetting = useMemo(() => {
    return mode === OVERLAY_ADC_CATEGORY ? gMap : gCorrectionMap;
  }, [Update]);
  const makeProperties = () => {
    let postData = getReAnalysisParameter(mode, originInfo);
    console.log('postData', postData);
    const obj =
      mode === OVERLAY_ADC_CATEGORY
        ? {
            ...postData,
            map: MapSetting,
            variation: gVariation,
            reproducibility: gReproducibility,
            anova: gAnova,
          }
        : {
            ...postData,
            correction: MapSetting,
          };
    console.log('obj', obj);
    return JSON.stringify(obj);
  };
  const makeFileName = (v) => {
    const fileList = {
      [E_OVERLAY_VARIATION]: ['shot', 'rot_mag'],
      [E_OVERLAY_REPRODUCIBILITY]: [MSG_X, MSG_Y],
    };
    const FolderList = {
      [E_OVERLAY_IMAGE]: 'Correction_Image_Map',
      [E_OVERLAY_COMPONENT]: 'Correction_Component_Map',
    };

    const filename = v.split('.');
    if (Object.keys(fileList).includes(filename[0])) {
      const obj = fileList;
      return `${filename[0]}.${obj[filename[0]][+filename[1]]}.png`;
    } else if (Object.keys(FolderList).includes(filename[0])) {
      const obj = FolderList;
      return `${obj[filename[0]]}.${filename[1]}.png`;
    }
    return v;
  };
  const getTableCsv = (data) => {
    const convertJson = [];
    data.dataSource.map((row) => {
      const tmp = {};
      data.columns.map((obj) =>
        Object.assign(tmp, { [obj.title]: row[obj.dataIndex] }),
      );
      convertJson.push(tmp);
    });
    return jsonToCSV(convertJson);
  };

  const downloadFunc = async () => {
    const FormObj = new FormData();
    console.log('==============settings.json======================');
    FormObj.append(
      'setting',
      new Blob([makeProperties()], {
        type: 'application/json',
      }),
    );
    console.log('==============getGraphImage======================');
    const imgData = await getGraphImage2();
    imgData.forEach((v) => {
      FormObj.append('files', new File([v.url], makeFileName(v.filename)));
    });
    console.log('==============anova csv file======================');
    if (mode === OVERLAY_ADC_CATEGORY) {
      const anovaTable_X = getAnovaTableFuc(gAdcMeasurementData.anova?.X ?? {});
      const anovaTable_Y = getAnovaTableFuc(gAdcMeasurementData.anova?.Y ?? {});
      FormObj.append(
        'files',
        new File([getTableCsv(anovaTable_Y)], `${E_OVERLAY_ANOVA}.Y.csv`),
      );
      FormObj.append(
        'files',
        new File([getTableCsv(anovaTable_X)], `${E_OVERLAY_ANOVA}.X.csv`),
      );
    }

    const { status } = await postFormdataRequestExport(
      `${URL_EXPORT_OVERLAY}/${mode}/${originInfo.source_info.files_rid}`,
      FormObj,
    );
    console.log('status', status);
  };
  return (
    <>
      <button
        css={SG.antdButtonStyle}
        className="white"
        style={{ marginLeft: '8px', fontWeight: 400 }}
        onClick={downloadFunc}
      >
        <CloudDownloadOutlined />
        <span> {MSG_DOWNLOAD} </span>
      </button>
    </>
  );
};
ResultDownload.propTypes = {
  mode: PropTypes.string,
  Update: PropTypes.bool,
};
export default ResultDownload;
