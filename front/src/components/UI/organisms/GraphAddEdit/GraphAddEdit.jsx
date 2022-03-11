import React, {
  useRef,
  useState,
  useEffect,
  useCallback,
  useMemo,
} from 'react';
import { Form, Select, Button, Input, DatePicker, Cascader } from 'antd';
import { CSSTransition } from 'react-transition-group';
import Plotly from 'plotly.js-dist';
import PropTypes from 'prop-types';
import dayjs from 'dayjs';
import { backgroundStyle } from '../GraphManagement/styleGroup';
import { displayNotification } from '../../../pages/JobAnalysis/functionGroup';
import { createAxisData } from '../../../pages/JobAnalysis/AnalysisGraph/functionGroup';
import useRuleSettingInfo from '../../../../hooks/useRuleSettingInfo';
import useResultInfo from '../../../../hooks/useResultInfo';
import * as SG from './styleGroup';
import * as FN from './functionGroup';
import {
  GraphDateRegex,
  GraphRangeRegex,
  CommonRegex,
} from '../../../../lib/util/RegExp';
import { getParseData } from '../../../../lib/util/Util';
import { RenderSelectOptions } from '../../../pages/JobAnalysis/AnalysisTable/functionGroup';
import { DATE_FORMAT } from '../../../../lib/api/Define/etc';

const { Option } = Select;
const { Item } = Form;
const { RangePicker } = DatePicker;
const defaultErrorMsg = `
  There is a problem with the script.
  Please check the settings again.
`;

const GraphAddEdit = React.memo(
  ({ data, mode, closer, isOpen, index, type, onClose }) => {
    const { visualStepInfo, updateVisualInfo } = useRuleSettingInfo();
    const {
      visualization,
      analysisData,
      originalData,
      originalFilteredRows,
      analysisGraphInfo,
      originalGraphInfo,
      setAnalysisGraphInfo,
      setOriginalGraphInfo,
    } = useResultInfo();
    const graphArea = useRef();
    const [graphData, setGraphData] = useState({
      type: [],
      x: '0',
      y: [],
      z: '0',
    });
    const [title, setTitle] = useState('');
    const [xRange, setXrange] = useState({
      min: '',
      max: '',
    });
    const [yRange, setYrange] = useState({
      min: '',
      max: '',
    });
    const [zRange, setZrange] = useState({
      min: '',
      max: '',
    });
    const [errorMsg, setErrorMsg] = useState('');
    const [isPreview, setIsPreview] = useState(false);
    const [originData, setOriginData] = useState({});

    const xOptionList = useMemo(() => {
      if (type !== 'step') {
        const selectedData = type === 'analysis' ? analysisData : originalData;
        return Array.isArray(selectedData.dispOrder)
          ? selectedData.dispOrder
          : selectedData.common_axis_x;
      }
    }, [JSON.stringify(analysisData), JSON.stringify(originalData)]);

    const updateRangeInfo = (e) => {
      const isBoxPlot =
        graphData.type.length === 1 && graphData.type[0] === 'box plot';
      let tmpX = undefined,
        tmpY = undefined;

      if (e['xaxis.range[0]'] !== undefined || e['xaxis.autorange']) {
        if (
          e['xaxis.autorange'] ||
          (!GraphDateRegex.test(e['xaxis.range[0]']) &&
            isNaN(parseInt(e['xaxis.range[0]'])))
        ) {
          tmpX = {
            min: '',
            max: '',
          };
        } else {
          tmpX = {
            min:
              GraphDateRegex.test(e['xaxis.range[0]']) && !isBoxPlot
                ? dayjs(e['xaxis.range[0]'])
                : e['xaxis.range[0]'],
            max:
              GraphDateRegex.test(e['xaxis.range[1]']) && !isBoxPlot
                ? dayjs(e['xaxis.range[1]'])
                : e['xaxis.range[1]'],
          };
        }
      }

      if (e['yaxis.range[0]'] !== undefined || e['yaxis.autorange']) {
        tmpY = {
          min: e['yaxis.autorange'] ? '' : e['yaxis.range[0]'],
          max: e['yaxis.autorange'] ? '' : e['yaxis.range[1]'],
        };
      }

      if (tmpX) {
        setXrange(tmpX);
      }

      if (tmpY) {
        setYrange(tmpY);
      }
      setIsPreview(true);
    };

    const renderGraph = (info, init) => {
      try {
        const graphType =
          type === 'step'
            ? visualStepInfo.function_graph_type
            : visualization.function_graph_type;
        const currentRows =
          type === 'step'
            ? originData?.row ??
              originData?.data?.row ??
              originData?.data?.data?.row ??
              []
            : type === 'analysis'
            ? analysisData.data
            : originalFilteredRows;
        const currentScript = graphType.find((v) => {
          return info.graphInfo.type === 'user'
            ? v.name === info.graphInfo.name
            : v.type === info.graphInfo.type;
        }).script;
        const renderFunc = new Function('return ' + currentScript)();
        const { xaxisData, yaxisData, zaxisData } = createAxisData(
          currentRows,
          {
            x: info.x,
            y: init
              ? info.y
              : FN.createYvalue(
                  type === 'step'
                    ? data.data
                    : type === 'analysis'
                    ? analysisData.dispGraph
                    : originalData.dispGraph,
                  type,
                  info.y,
                ),
            z: info.z,
          },
          type,
          type === 'step'
            ? Array.isArray(currentRows)
            : type === 'analysis'
            ? !Array.isArray(analysisData.dispOrder)
            : !Array.isArray(originalData.dispOrder),
        );

        const params = {
          type: info.type,
          x: xaxisData,
          y: yaxisData,
          z: zaxisData,
          title: info.title,
          range: {
            x: [
              typeof info.xRange.min !== 'string' &&
              typeof info.xRange.min !== 'number'
                ? dayjs(info.xRange.min).format(DATE_FORMAT)
                : info.xRange.min,
              typeof info.xRange.max !== 'string' &&
              typeof info.xRange.max !== 'number'
                ? dayjs(info.xRange.max).format(DATE_FORMAT)
                : info.xRange.max,
            ],
            y: [info.yRange.min, info.yRange.max],
            z: [info.zRange.min, info.zRange.max],
          },
          func: (e) => updateRangeInfo(e),
        };

        renderFunc(Plotly, graphArea.current, params);
        setErrorMsg('');
        if (!init) {
          setIsPreview(true);
        }
      } catch (e) {
        setErrorMsg(defaultErrorMsg);
      }
    };

    const changeGraphData = (t, v) => {
      const throwData =
        type === 'step'
          ? originData
          : type === 'analysis'
          ? analysisData.data
          : originalFilteredRows;
      const sampleData = FN.createSampleData(
        type,
        throwData,
        type === 'step'
          ? undefined
          : type === 'analysis'
          ? Array.isArray(analysisData.dispOrder)
          : Array.isArray(originalData.dispOrder),
      );
      if (
        (t === 'x' && !compareFormat(v)) ||
        (t === 'type' &&
          (v.length === 0 || v[0] !== 'box plot') &&
          ((typeof xRange.min === 'object' &&
            !FN.boxPlotExceptionCheck(type, sampleData, graphData.x)) ||
            (typeof xRange.min !== 'object' &&
              FN.boxPlotExceptionCheck(type, sampleData, graphData.x)))) ||
        (v[0] === 'box plot' && typeof xRange.min === 'object')
      ) {
        setXrange({
          min: '',
          max: '',
        });
      }
      let newData = graphData;
      newData[t] = v;
      setGraphData(Object.assign({}, newData));
      setIsPreview(false);
    };

    const compareFormat = (v) => {
      const throwData =
        type === 'step'
          ? originData
          : type === 'analysis'
          ? analysisData.data
          : originalFilteredRows;
      const sourceData = FN.createSampleData(
        type,
        throwData,
        type === 'analysis'
          ? Array.isArray(analysisData.dispOrder)
          : Array.isArray(originalData.dispOrder),
      );

      if (graphData.type[0] === 'box plot' && xRange.min !== '') {
        return typeof xRange.min !== 'object';
      }

      return sourceData === undefined || v === '0' || graphData.x === '0'
        ? true
        : GraphDateRegex.test(
            Array.isArray(sourceData) ? sourceData[0][v] : sourceData[v],
          ) ===
            GraphDateRegex.test(
              Array.isArray(sourceData)
                ? sourceData[0][graphData.x]
                : sourceData[graphData.x],
            );
    };

    const checkXrange = (v) => {
      if (graphData.type[0] === 'box plot' || v === '0') {
        return false;
      }

      const getColumnData = (rows, keys, array) => {
        const getData = (ListData, keyValue) => {
          return Object.values(ListData).map((list) =>
            Object.values(list).map((one) => {
              array.push(one[keyValue]);
            }),
          );
        };
        Array.isArray(rows)
          ? rows.map((row) => {
              Array.isArray(keys) ? getData(row[v[0]], v[1]) : getData(row, v);
            })
          : Object.values(rows).map((z) => array.push(z[v]));
      };
      let totalData = [];
      if (type === 'step') {
        if (data ?? false) {
          getColumnData(originData.row, v, totalData);
          return GraphDateRegex.test(totalData[0]);
        } else {
          return true;
        }
      } else {
        const sourceData =
          type === 'analysis' ? analysisData.data : originalFilteredRows;
        const isSingle =
          type === 'analysis'
            ? Array.isArray(analysisData.dispOrder)
            : Array.isArray(originalData.dispOrder);

        if (isSingle) {
          return GraphDateRegex.test(sourceData[0][v]);
        } else {
          let isDate = false;

          Object.keys(sourceData).forEach((x) => {
            if (
              Object.keys(sourceData[x]).length > 0 &&
              GraphDateRegex.test(sourceData[x][0][v])
            ) {
              isDate = true;
            }
          });

          return isDate;
        }
      }
    };

    const disablePreview = useCallback(() => {
      return (
        graphData.type.length === 0 ||
        graphData.y.length === 0 ||
        title.length === 0
      );
    }, [graphData, title]);

    const closeAddEdit = () => {
      if (type === 'step') {
        closer();
      } else {
        onClose();
      }
      setGraphData({
        type: [],
        x: '0',
        y: [],
        z: '0',
      });
      setTitle('');
      setXrange({
        min: '',
        max: '',
      });
      setYrange({
        min: '',
        max: '',
      });
      setZrange({
        min: '',
        max: '',
      });
      setIsPreview(false);
      graphArea.current.removeAttribute('class');
      graphArea.current.firstChild?.remove();
    };

    const onAddEdit = () => {
      let message =
          mode === 'add' ? 'Add graph completed' : 'Edit graph completed',
        description = '',
        style = { borderLeft: '8px solid green' };
      const itemsInfo =
        type === 'step'
          ? visualStepInfo.items
          : type === 'analysis'
          ? analysisGraphInfo
          : originalGraphInfo;

      if (graphData.type.length === 0) {
        description = 'Graph type is not set. Please check the graph type.';
      } else if (graphData.y.length === 0) {
        description =
          'No data has been selected for reference in the graph. Please select data.';
      } else if (
        graphArea.current.getElementsByClassName('plot-container').length === 0
      ) {
        description = `The graph has not been drawn yet. Please ${mode} again after the graph is drawn.`;
      } else if (!isPreview) {
        description =
          'Save is not executed because the graph has not been changed.';
      } else if (title.length === 0 || !CommonRegex.test(title)) {
        description = 'The title is incorrect. Please check the title setting.';
      } else if (
        xRange.min.length > 0 ||
        xRange.max.length > 0 ||
        yRange.min.length > 0 ||
        yRange.max.length > 0 ||
        zRange.min.length > 0 ||
        zRange.max.length > 0
      ) {
        if (
          ((typeof xRange.min === 'string' || typeof xRange.min === 'number') &&
            (!GraphRangeRegex.test(xRange.min) ||
              !GraphRangeRegex.test(xRange.max) ||
              FN.compareErrorCheck(xRange.min, xRange.max))) ||
          !GraphRangeRegex.test(yRange.min) ||
          !GraphRangeRegex.test(yRange.max) ||
          FN.compareErrorCheck(yRange.min, yRange.max) ||
          !GraphRangeRegex.test(zRange.min) ||
          !GraphRangeRegex.test(zRange.max) ||
          FN.compareErrorCheck(zRange.min, zRange.max)
        ) {
          description =
            'The range setting is incorrect. Please check the range setting.';
        }
      }

      if (description === '') {
        description =
          mode === 'add'
            ? 'Add a graph has been completed.'
            : 'Edit a graph has been completed.';

        const newItems = {
          id: mode === 'add' ? null : itemsInfo[index].id,
          type: graphData.type,
          x_axis: graphData.x === '0' ? '' : graphData.x,
          y_axis: FN.createYvalue(
            type === 'step'
              ? data.data
              : type === 'analysis'
              ? analysisData.dispGraph
              : originalData.dispGraph,
            type,
            graphData.y,
          ),
          z_axis:
            graphData.z === '0' || graphData.z[0] === '0' ? '' : graphData.z,
          title: title,
          x_range_min:
            typeof xRange.min !== 'string' && typeof xRange.min !== 'number'
              ? xRange.min.format('YYYY-MM-DD HH:mm:ss.SSS')
              : xRange.min,
          x_range_max:
            typeof xRange.max !== 'string' && typeof xRange.max !== 'number'
              ? xRange.max.format('YYYY-MM-DD HH:mm:ss.SSS')
              : xRange.max,
          y_range_min: yRange.min,
          y_range_max: yRange.max,
          z_range_min: zRange.min,
          z_range_max: zRange.max,
        };

        if (type === 'step') {
          updateVisualInfo({
            ...visualStepInfo,
            items:
              mode === 'add'
                ? [...visualStepInfo.items, newItems]
                : visualStepInfo.items.map((v, i) => {
                    return i !== index ? v : newItems;
                  }),
          });
        } else if (type === 'analysis') {
          setAnalysisGraphInfo(
            mode === 'add'
              ? [...analysisGraphInfo, newItems]
              : analysisGraphInfo.map((v, i) => {
                  return i !== index ? v : newItems;
                }),
          );
        } else {
          setOriginalGraphInfo(
            mode === 'add'
              ? [...originalGraphInfo, newItems]
              : originalGraphInfo.map((v, i) => {
                  return i !== index ? v : newItems;
                }),
          );
        }

        if (mode !== 'add') {
          closeAddEdit();
        } else {
          setIsPreview(false);
          setGraphData({
            ...graphData,
            type: [],
          });
          setXrange({
            min: '',
            max: '',
          });
          setYrange({
            min: '',
            max: '',
          });
          setZrange({
            min: '',
            max: '',
          });
          setTitle('');
          graphArea.current.removeAttribute('class');
          graphArea.current.firstChild?.remove();
        }
      } else {
        message = mode === 'add' ? 'Add graph failed' : 'Edit graph failed';
        style = { borderLeft: '8px solid red' };
      }

      displayNotification({
        message: message,
        description: description,
        duration: 3,
        style: style,
      });
    };

    useEffect(() => {
      if (mode !== 'add' && isOpen) {
        const currentInfo =
          type === 'step'
            ? visualStepInfo.items[index]
            : type === 'analysis'
            ? analysisGraphInfo[index]
            : originalGraphInfo[index];

        if (currentInfo) {
          setGraphData({
            type: currentInfo.type,
            x:
              currentInfo.x_axis === '' || currentInfo.x_axis === null
                ? '0'
                : currentInfo.x_axis,
            y: currentInfo.y_axis,
            z:
              currentInfo.z_axis === '' || currentInfo.z_axis === null
                ? '0'
                : currentInfo.z_axis,
          });
          setTitle(currentInfo.title);
          setXrange({
            min: GraphDateRegex.test(currentInfo.x_range_min)
              ? dayjs(currentInfo.x_range_min)
              : currentInfo.x_range_min === null
              ? ''
              : currentInfo.x_range_min,
            max: GraphDateRegex.test(currentInfo.x_range_max)
              ? dayjs(currentInfo.x_range_max)
              : currentInfo.x_range_max === null
              ? ''
              : currentInfo.x_range_max,
          });
          setYrange({
            min:
              currentInfo.y_range_min === null ? '' : currentInfo.y_range_min,
            max:
              currentInfo.y_range_max === null ? '' : currentInfo.y_range_max,
          });
          setZrange({
            min:
              currentInfo.z_range_min === null ? '' : currentInfo.z_range_min,
            max:
              currentInfo.z_range_max === null ? '' : currentInfo.z_range_max,
          });
          setIsPreview(true);

          renderGraph(
            {
              graphInfo:
                type === 'step'
                  ? visualStepInfo.graph_list.find(
                      (v) => v.name === currentInfo.type[0],
                    )
                  : visualization.graph_list.find(
                      (v) => v.name === currentInfo.type[0],
                    ),
              type: currentInfo.type,
              x: currentInfo.x_axis,
              y: currentInfo.y_axis,
              z: currentInfo.z_axis,
              title: currentInfo.title,
              xRange: {
                min: currentInfo.x_range_min,
                max: currentInfo.x_range_max,
              },
              yRange: {
                min: currentInfo.y_range_min,
                max: currentInfo.y_range_max,
              },
              zRange: {
                min: currentInfo.z_range_min,
                max: currentInfo.z_range_max,
              },
            },
            true,
          );
        }
      }
    }, [isOpen]);

    useEffect(() => {
      if (type === 'step') {
        setOriginData({
          row:
            data?.row ??
            data?.data?.row ??
            data?.data?.map((o) => {
              const pData = getParseData(o);
              return { [pData.id]: pData.value.row };
            }) ??
            {},
          disp_graph:
            data?.disp_graph ??
            data?.data?.disp_graph ??
            data?.data?.map((o) => {
              const pData = getParseData(o);
              return {
                label: pData.id,
                value: pData.id,
                children: pData.value.disp_graph.map((obj) => ({
                  label: obj,
                  value: obj,
                })),
              };
            }) ??
            [],
          disp_order:
            data?.disp_order ??
            data?.data?.disp_order ??
            data?.visualization?.common_axis_x ??
            [],
        });
      }
    }, []);

    if (isOpen === false && type === 'step') return <></>;

    return (
      <CSSTransition in={isOpen} classNames="modal" unmountOnExit timeout={100}>
        <>
          <div css={backgroundStyle} />
          <div css={SG.mainStyle}>
            <div>
              <div>{mode === 'add' ? 'Add Graph' : 'Edit Graph'}</div>
              <div>
                <Button onClick={closeAddEdit}>Close</Button>
                <Button type="primary" onClick={onAddEdit}>
                  {mode === 'add' ? 'Add' : 'Save'}
                </Button>
              </div>
            </div>
            <div>
              <div>
                <Form labelAlign="left">
                  <AxisTypeOption
                    values={graphData}
                    options={{
                      type:
                        type === 'step'
                          ? visualStepInfo.graph_list
                          : visualization.graph_list,
                      x:
                        type === 'step'
                          ? originData?.disp_order ?? {}
                          : xOptionList,
                      y:
                        type === 'step'
                          ? originData?.disp_graph ?? []
                          : type === 'analysis'
                          ? analysisData.dispGraph
                          : originalData.dispGraph,
                      z:
                        type === 'step'
                          ? originData?.disp_graph ?? []
                          : type === 'analysis'
                          ? analysisData.dispGraph
                          : originalData.dispGraph,
                    }}
                    changeFunc={changeGraphData}
                    type={type}
                  />
                  <Item label="Title">
                    <Input
                      value={title}
                      onChange={(e) => {
                        setTitle(e.target.value);
                        setIsPreview(false);
                      }}
                      maxLength="30"
                    />
                  </Item>
                  <Item label="X Range">
                    {!checkXrange(graphData.x) ? (
                      <div className="multi-input">
                        <Input
                          value={xRange.min}
                          onChange={(e) => {
                            setXrange((prevState) => {
                              return { ...prevState, min: e.target.value };
                            });
                            setIsPreview(false);
                          }}
                        />
                        <Input
                          value={xRange.max}
                          onChange={(e) => {
                            setXrange((prevState) => {
                              return { ...prevState, max: e.target.value };
                            });
                            setIsPreview(false);
                          }}
                        />
                      </div>
                    ) : (
                      <RangePicker
                        showTime
                        allowClear={false}
                        style={{ width: '100%' }}
                        value={
                          xRange.min === '' ? [] : [xRange.min, xRange.max]
                        }
                        onChange={(v) => {
                          setXrange({
                            min: v[0],
                            max: v[1],
                          });
                          setIsPreview(false);
                        }}
                        inputReadOnly
                      />
                    )}
                  </Item>
                  <Item label="Y Range">
                    <div className="multi-input">
                      <Input
                        value={yRange.min}
                        onChange={(e) => {
                          setYrange((prevState) => {
                            return { ...prevState, min: e.target.value };
                          });
                          setIsPreview(false);
                        }}
                      />
                      <Input
                        value={yRange.max}
                        onChange={(e) => {
                          setYrange((prevState) => {
                            return { ...prevState, max: e.target.value };
                          });
                          setIsPreview(false);
                        }}
                      />
                    </div>
                  </Item>
                  <Item label="Z Range">
                    <div className="multi-input">
                      <Input
                        value={zRange.min}
                        onChange={(e) => {
                          setZrange((prevState) => {
                            return { ...prevState, min: e.target.value };
                          });
                          setIsPreview(false);
                        }}
                      />
                      <Input
                        value={zRange.max}
                        onChange={(e) => {
                          setZrange((prevState) => {
                            return { ...prevState, max: e.target.value };
                          });
                          setIsPreview(false);
                        }}
                      />
                    </div>
                  </Item>
                </Form>
              </div>
              <div>
                <Button
                  type="primary"
                  disabled={disablePreview() === true}
                  onClick={() =>
                    renderGraph(
                      {
                        graphInfo:
                          type === 'step'
                            ? visualStepInfo.graph_list.find(
                                (v) => v.name === graphData.type[0],
                              )
                            : visualization.graph_list.find(
                                (v) => v.name === graphData.type[0],
                              ),
                        x: graphData.x,
                        y: graphData.y,
                        z: graphData.z,
                        type: graphData.type,
                        title: title,
                        xRange: xRange,
                        yRange: yRange,
                        zRange: zRange,
                      },
                      false,
                    )
                  }
                >
                  Preview
                </Button>
                <div ref={graphArea}>{errorMsg.length > 0 ? errorMsg : ''}</div>
              </div>
            </div>
          </div>
        </>
      </CSSTransition>
    );
  },
);

GraphAddEdit.propTypes = {
  data: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  closer: PropTypes.func,
  isOpen: PropTypes.bool,
  mode: PropTypes.string,
  index: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  type: PropTypes.string,
  onClose: PropTypes.func,
};
GraphAddEdit.defaultProps = {
  mode: 'add',
  type: 'step',
};

const AxisTypeOption = React.memo(({ values, options, changeFunc, type }) => {
  const yzOptionList = useMemo(() => FN.createYZoptionList(options.y), [
    JSON.stringify(options.y),
  ]);

  return (
    <>
      <Item label="Graph Type">
        <Select
          mode="multiple"
          value={values.type}
          onChange={(v) => changeFunc('type', v)}
          maxTagCount="responsive"
        >
          {options.type.map((v) => {
            return (
              <Option
                value={v.name}
                key={v.name}
                disabled={
                  values.type.length > 0 &&
                  ((options.type.find((z) => z.name === values.type[0]).type ===
                    'user' &&
                    v.type === 'system') ||
                    (options.type.find((z) => z.name === values.type[0])
                      .type === 'system' &&
                      v.type === 'user'))
                }
              >
                {v.name}
              </Option>
            );
          })}
        </Select>
      </Item>
      <Item label="Axis(X)">
        <Select value={values.x} onChange={(v) => changeFunc('x', v)}>
          <Option value="0">None</Option>
          {options.x.map(RenderSelectOptions)}
        </Select>
      </Item>
      <Item label="Axis(Y)">
        {(typeof options.y?.[0] ?? undefined) === 'object' &&
        type === 'step' ? (
          <Cascader
            options={options.y}
            onChange={(v) => changeFunc('y', v)}
            value={Array.isArray(values.y) ? values.y : []}
            multiple
            maxTagCount="responsive"
          />
        ) : type === 'step' || Array.isArray(options.y) ? (
          <Select
            mode="multiple"
            value={values.y}
            onChange={(v) => changeFunc('y', v)}
            maxTagCount="responsive"
          >
            {yzOptionList.map(RenderSelectOptions)}
          </Select>
        ) : (
          <Cascader
            options={yzOptionList}
            onChange={(v) => changeFunc('y', v)}
            value={values.y}
            multiple
            maxTagCount="responsive"
          />
        )}
      </Item>
      <Item label="Axis(Z)">
        {(typeof options.z?.[0] ?? undefined) === 'object' &&
        type === 'step' ? (
          <Cascader
            options={[
              {
                value: '0',
                label: 'None',
              },
              ...options.z,
            ]}
            onChange={(v) => changeFunc('z', v)}
            value={typeof values.z === 'string' ? [values.z] : values.z}
            allowClear={false}
          />
        ) : type === 'step' || Array.isArray(options.y) ? (
          <Select value={values.z} onChange={(v) => changeFunc('z', v)}>
            <Option value="0">None</Option>
            {yzOptionList.map(RenderSelectOptions)}
          </Select>
        ) : (
          <Cascader
            options={[
              {
                value: '0',
                label: 'None',
              },
              ...yzOptionList,
            ]}
            onChange={(v) => changeFunc('z', v)}
            value={typeof values.z === 'string' ? [values.z] : values.z}
            allowClear={false}
          />
        )}
      </Item>
    </>
  );
});
AxisTypeOption.displayName = 'AxisTypeOption';
AxisTypeOption.propTypes = {
  values: PropTypes.object.isRequired,
  options: PropTypes.object.isRequired,
  changeFunc: PropTypes.func.isRequired,
  type: PropTypes.string.isRequired,
};

export default GraphAddEdit;
