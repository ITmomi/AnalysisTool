import React, { useCallback, useEffect, useMemo } from 'react';
import PropTypes from 'prop-types';
import Plotly from 'plotly.js-dist';
import {
  MapDefaultScript,
  ReproducibilityDefaultScript,
  VariationDefaultScript,
  AnovaDefaultScript,
  BaraDefaultScript,
  CorrectionCompScript,
  CorrectImageScript,
} from '../../../../../lib/util/Graph';
import {
  E_OVERLAY_ANOVA,
  E_OVERLAY_COMPONENT,
  E_OVERLAY_IMAGE,
  E_OVERLAY_MAP,
  E_OVERLAY_REPRODUCIBILITY,
  E_OVERLAY_VARIATION,
  OVERLAY_ADC_CATEGORY,
} from '../../../../../lib/api/Define/etc';
import useOverlayResultInfo from '../../../../../hooks/useOverlayResultInfo';
import {
  MSG_3SIGMA_X,
  MSG_3SIGMA_Y,
  MSG_X,
  MSG_Y,
} from '../../../../../lib/api/Define/Message';
import { Divider } from 'antd';
import { AnovaTab, AnovaTable } from '../AnovaSetting';
import useOverlaySettingInfo from '../../../../../hooks/useOverlaySettingInfo';
import MapLotTable from '../MapSetting/MapLotTable';
import {
  OVERLAY_ADC_TYPE_LIST,
  OVERLAY_CORRECTION_TYPE_LIST,
} from '../../../../../lib/api/Define/OverlayDefault';

const gScript = [
  { id: E_OVERLAY_MAP, func: [MapDefaultScript] },
  {
    id: E_OVERLAY_VARIATION,
    func: [BaraDefaultScript, VariationDefaultScript],
  },
  {
    id: E_OVERLAY_REPRODUCIBILITY,
    func: [ReproducibilityDefaultScript, ReproducibilityDefaultScript],
  },
  {
    id: E_OVERLAY_ANOVA,
    func: [AnovaDefaultScript, AnovaDefaultScript],
  },
  {
    id: E_OVERLAY_IMAGE,
    func: [CorrectImageScript],
  },
  {
    id: E_OVERLAY_COMPONENT,
    func: [CorrectionCompScript],
  },
];
const common = { screen_width: 1700, screen_height: 500 };
const DISP_NAME = (msg) => ({ disp_name: msg });
const Reproducibility_X = {
  ...common,
  title: MSG_3SIGMA_X,
  ...DISP_NAME(MSG_X),
};
const Reproducibility_Y = {
  ...common,
  title: MSG_3SIGMA_Y,
  ...DISP_NAME(MSG_Y),
};

const OverlayResultGraph = ({ mode, type, origin_data, UpdateGraph }) => {
  const { adcCommonInfo: adcCommon } = useOverlaySettingInfo();
  const {
    gReproducibility,
    gMap,
    gVariation,
    gAnova,
    updateAnovaSetting,
    gCorrectionMap: gCorrection,
    gAdcMeasurementData: gAdcOrigin,
    gCorrectionData: gCorrectionOrigin,
    adc_correction_tooltip,
    stage_correction_tooltip,
    disp_option_correction,
    disp_option_cpvs,
  } = useOverlayResultInfo();
  const getScriptObject = useCallback((id) => {
    return gScript.find((o) => o.id === id);
  }, []);
  const RenderGraph = useCallback(
    ({ renderFunc, element, object }) => {
      renderFunc(Plotly, element, origin_data ?? {}, object);
    },
    [origin_data],
  );
  const typeObject = useMemo(() => getScriptObject(type), [
    type,
    getScriptObject,
  ]);
  const LotIdList = useMemo(
    () =>
      Object.keys(
        mode === OVERLAY_ADC_CATEGORY
          ? gAdcOrigin.data
          : gCorrectionOrigin.data.map,
      ),
    [mode, gAdcOrigin, gCorrectionOrigin],
  );

  const drawRenderObject = {
    [E_OVERLAY_ANOVA]: [
      { ...common, ...DISP_NAME('X') },
      { ...common, ...DISP_NAME('Y') },
    ],
    [E_OVERLAY_MAP]: [
      {
        ...gMap,
        disp_option: disp_option_cpvs(mode),
      },
    ],
    [E_OVERLAY_VARIATION]: [
      {
        ...gVariation,
        ...common,
        select_shot:
          gVariation.select_shot === 'all'
            ? adcCommon?.shot
            : gVariation.select_shot,
      },
      {},
    ],
    [E_OVERLAY_REPRODUCIBILITY]: [
      {
        ...Reproducibility_X,
        upper_limit: gReproducibility.three_sigma_x,
      },
      {
        ...Reproducibility_Y,
        upper_limit: gReproducibility.three_sigma_y,
      },
    ],
    [E_OVERLAY_IMAGE]: [
      {
        ...gCorrection,
        disp_option_correction: disp_option_correction,
        disp_option_map: disp_option_cpvs(mode),
      },
    ],
    [E_OVERLAY_COMPONENT]: [
      {
        ...gCorrection,
        adc_correction_tooltip: adc_correction_tooltip,
        stage_correction_tooltip: stage_correction_tooltip,
        disp_option_correction: disp_option_correction,
      },
    ],
  };
  const drawGraph = (graphObject, forceDisplay) => {
    if ((forceDisplay ?? false) && graphObject.id !== undefined) {
      if (
        [E_OVERLAY_MAP, E_OVERLAY_IMAGE, E_OVERLAY_COMPONENT].includes(
          graphObject.id,
        )
      ) {
        LotIdList.map((lot) => {
          graphObject?.func?.map((_, i) => {
            RenderGraph({
              renderFunc: graphObject?.func[i] ?? null,
              object: { ...drawRenderObject[graphObject.id][i], lot_name: lot },
              element: `${graphObject.id}_${lot}_${i}`,
            });
          });
        });
      } else {
        graphObject?.func?.map((_, i) => {
          RenderGraph({
            renderFunc: graphObject?.func[i] ?? null,
            object: drawRenderObject[graphObject.id][i],
            element: `${graphObject.id}_${
              graphObject.id === E_OVERLAY_ANOVA ? (i === 0 ? 'X' : 'Y') : i
            }`,
          });
        });
      }
    }
  };
  useEffect(() => {
    console.log('draw type change / gAnova/gVariation or gReproducibility');
    if (type === typeObject?.id) {
      drawGraph(typeObject, 1);
    }
  }, [gAnova, gReproducibility, gVariation]);

  useEffect(() => {
    console.log('UpdateGraph?.update', UpdateGraph?.update ?? false);
    if (UpdateGraph?.update ?? false) {
      (mode === OVERLAY_ADC_CATEGORY
        ? OVERLAY_ADC_TYPE_LIST
        : OVERLAY_CORRECTION_TYPE_LIST
      ).map((graph) => drawGraph(getScriptObject(graph.id), 1));
      UpdateGraph.func(false);
    }
  }, [UpdateGraph]);
  useEffect(() => {
    console.log('origin_data update!!!');
    UpdateGraph.func(true);
  }, [origin_data]);

  return (
    <>
      {(mode === OVERLAY_ADC_CATEGORY
        ? OVERLAY_ADC_TYPE_LIST
        : OVERLAY_CORRECTION_TYPE_LIST
      ).map((graph, i) => (
        <>
          <div key={i} style={type === graph.id ? {} : { display: 'none' }}>
            {graph.id === E_OVERLAY_ANOVA ? (
              <div>
                <AnovaTab
                  list={gAnova.list}
                  selected={gAnova.selected}
                  changeEvent={(e) =>
                    updateAnovaSetting({ ...gAnova, selected: e })
                  }
                />
                <AnovaTable
                  origin={adcCommon.origin?.anova ?? {}}
                  selected={gAnova.selected}
                />{' '}
                <Divider />
                <div
                  id={`${graph.id}_X`}
                  style={gAnova.selected === 'X' ? {} : { display: 'none' }}
                />
                <div
                  id={`${graph.id}_Y`}
                  style={gAnova.selected === 'Y' ? {} : { display: 'none' }}
                />
              </div>
            ) : [E_OVERLAY_MAP, E_OVERLAY_COMPONENT, E_OVERLAY_IMAGE].includes(
                graph.id,
              ) ? (
              <>
                {LotIdList.map((lot, index) => {
                  return (
                    <>
                      {graph.id === E_OVERLAY_MAP && gMap.show_extra_info ? (
                        <>
                          <MapLotTable
                            origin={adcCommon?.origin?.data}
                            lot_id={lot}
                            lot_idx={index + 1}
                          />
                        </>
                      ) : (
                        <></>
                      )}
                      {gScript
                        .find((o) => o.id === graph.id)
                        ?.func.map((_, i) => (
                          <>
                            {' '}
                            <div id={`${graph.id}_${lot}_${i}`} />
                          </>
                        ))}
                      <Divider />
                    </>
                  );
                })}
              </>
            ) : (
              <>
                {gScript
                  .find((o) => o.id === graph.id)
                  ?.func.map((_, i) => (
                    <>
                      {' '}
                      <div id={`${graph.id}_${i}`} />
                    </>
                  ))}
              </>
            )}
          </div>
        </>
      ))}
    </>
  );
};
OverlayResultGraph.propTypes = {
  mode: PropTypes.string,
  type: PropTypes.string,
  origin_data: PropTypes.object,
  UpdateGraph: PropTypes.object,
};
export default OverlayResultGraph;
