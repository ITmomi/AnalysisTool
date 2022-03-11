import React, { useState, useRef, useEffect, useMemo } from 'react';
import {
  Form,
  Select,
  Button,
  Radio,
  Input,
  Popconfirm,
  Tooltip,
  Cascader,
} from 'antd';
import PropTypes from 'prop-types';
import Plotly from 'plotly.js-dist';
import styled from '@emotion/styled';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/mode-javascript';
import 'ace-builds/src-noconflict/theme-tomorrow';
import { CSSTransition } from 'react-transition-group';
import { createAxisData } from '../../../pages/JobAnalysis/AnalysisGraph/functionGroup';
import { displayNotification } from '../../../pages/JobAnalysis/functionGroup';
import { CommonRegex } from '../../../../lib/util/RegExp';
import useRuleSettingInfo from '../../../../hooks/useRuleSettingInfo';
import * as SG from './styleGroup';
import { RenderSelectOptions } from '../../../pages/JobAnalysis/AnalysisTable/functionGroup';
import { createOptionData, createMultiData } from './functionGroup';
import {
  createYZoptionList,
  createYvalue,
} from '../GraphAddEdit/functionGroup';

const { Option } = Select;
const { Item } = Form;
const { Group } = Radio;
const defaultScript = `function renderGraph(Plotly, element, params) {
  var graph1 = {
      x: Object.values(params.x)[0],
      y: Object.values(params.y)[0],
      z: params.z,
      name: Object.keys(params.y)[0],
      type: 'scatter'
  };

  var figure = [graph1];

  var layout = {
      title: params.title,
      showlegend: true,
      xaxis: {
          range: params.range.x
      },
      yaxis: {
          range: params.range.y
      },
      zaxis: {
          range: params.range.z
      }
  };

  Plotly.newPlot(element, figure, layout);
  
  if (params.func) {
    element.on('plotly_relayout', params.func);
  }
}
`;
const defaultErrorMsg = `
  There is a problem with the script.
  Please check the settings again.
`;
const StyledEditor = styled.div`
  margin-top: 10px;
  * {
    font-family: consolas;
    line-height: 1;
  }
`;
const GraphManagement = React.memo(({ closer, isOpen }) => {
  const {
    visualStepInfo,
    updateVisualInfo,
    ruleStepConfig,
  } = useRuleSettingInfo();
  const [errorMsg, setErrorMsg] = useState('');
  const [mode, setMode] = useState('1');
  const [addType, setAddType] = useState('');
  const [editType, setEditType] = useState('');
  const [addScript, setAddScript] = useState(defaultScript);
  const [editScript, setEditScript] = useState('');
  const [addData, setAddData] = useState({
    x: '0',
    y: [],
    z: '0',
  });
  const [editData, setEditData] = useState({
    x: '0',
    y: [],
    z: '0',
  });
  const [isPreview, setIsPreview] = useState(false);
  const optionList = useMemo(
    () => createOptionData(ruleStepConfig[ruleStepConfig.length - 2]?.data),
    [ruleStepConfig[ruleStepConfig.length - 2]?.data],
  );
  const graphArea = useRef();

  const changeData = (key, v) => {
    let newData = {};
    if (mode === '1') {
      if (key === 'type') {
        setAddType(v);
      } else if (key === 'script') {
        setAddScript(v);
      } else {
        newData = addData;
        newData[key] = v;
        setAddData(Object.assign({}, newData));
      }
    } else {
      if (key === 'type') {
        setEditType(v);
        setEditScript(
          visualStepInfo.function_graph_type.find((z) => z.name === v).script,
        );
      } else if (key === 'script') {
        setEditScript(v);
      } else {
        newData = editData;
        newData[key] = v;
        setEditData(Object.assign({}, newData));
      }
    }
  };

  const renderGraph = () => {
    try {
      const currentRows = createMultiData(
        ruleStepConfig[ruleStepConfig.length - 2].data,
        'row',
      );
      const currentData = mode === '1' ? addData : editData;
      const currentScript = mode === '1' ? addScript : editScript;
      const renderFunc = new Function('return ' + currentScript)();
      const { xaxisData, yaxisData, zaxisData } = createAxisData(
        currentRows,
        {
          ...currentData,
          y: createYvalue(
            createMultiData(
              ruleStepConfig[ruleStepConfig.length - 2].data,
              'disp_graph',
            ),
            'analysis',
            currentData.y,
          ),
        },
        'analysis',
        Array.isArray(ruleStepConfig[ruleStepConfig.length - 2].data.data),
      );

      const params = {
        x: xaxisData,
        y: yaxisData,
        z: zaxisData,
        title: 'Example',
        range: {
          x: [],
          y: [],
          z: [],
        },
      };
      renderFunc(Plotly, graphArea.current, params);
      setErrorMsg('');
      setIsPreview(true);
    } catch (e) {
      setErrorMsg(defaultErrorMsg);
      setIsPreview(false);
    }
  };

  const disablePreview = () => {
    const currentData = mode === '1' ? addData : editData;
    const currentType = mode === '1' ? 'add' : editType;

    return currentData.y.length === 0 || currentType === '';
  };

  const onApply = () => {
    let message = '',
      description = '',
      tmpGraphType = [...visualStepInfo.function_graph_type],
      tmpGraphList = [...visualStepInfo.graph_list],
      tmpGraphItems = [...visualStepInfo.items];

    switch (mode) {
      case '1':
      default:
        if (
          graphArea.current.getElementsByClassName('plot-container').length ===
          0
        ) {
          description =
            'The graph has not been drawn yet. Please save again after the graph is drawn.';
        } else if (!isPreview) {
          description =
            'Save is not executed because the graph has not been changed.';
        } else if (
          !CommonRegex.test(addType) ||
          visualStepInfo.graph_list?.find((v) => v.name === addType) !==
            undefined
        ) {
          description =
            'The graph type is not correct or it is already registered. Please re-enter.';
        } else {
          tmpGraphType.push({
            id: null,
            name: addType,
            script: addScript,
            type: 'user',
          });
          tmpGraphList.push({
            name: addType,
            type: 'user',
          });
        }

        if (description !== '') {
          message = 'Save failed';
        }
        break;

      case '2':
        if (
          graphArea.current.getElementsByClassName('plot-container').length ===
          0
        ) {
          description =
            'The graph has not been drawn yet. Please save again after the graph is drawn.';
        } else if (
          editScript ===
          visualStepInfo.function_graph_type.find((v) => v.name === editType)
            .script
        ) {
          description =
            'Save is not executed because the script has not been changed.';
        } else if (!isPreview) {
          description =
            'Save is not executed because the graph has not been changed.';
        } else {
          tmpGraphType = tmpGraphType.map((v) => {
            return v.name === editType
              ? {
                  ...v,
                  script: editScript,
                }
              : v;
          });
          tmpGraphItems = tmpGraphItems.map((v) => {
            return v.type.find((z) => z === editType)
              ? {
                  ...v,
                  script_info: {
                    ...v.script_info,
                    script: editScript,
                  },
                }
              : v;
          });
        }

        if (description !== '') {
          message = 'Save failed';
        }
        break;

      case '3':
        if (editType === '') {
          message = 'Delete failed';
          description =
            'There is no graph type selected. Please select the graph type to delete.';
        } else {
          tmpGraphType = tmpGraphType.filter((v) => v.name !== editType);
          tmpGraphList = tmpGraphList.filter((v) => v.name !== editType);
          tmpGraphItems = tmpGraphItems.map((v) => {
            if (v === '') {
              return v;
            } else {
              const newType = v.type.filter((v) => v !== editType);
              return newType.length > 0
                ? {
                    ...v,
                    type: newType,
                  }
                : '';
            }
          });
        }
        break;
    }

    if (message !== '') {
      displayNotification({
        message: message,
        description: description,
        duration: 3,
        style: { borderLeft: '8px solid red' },
      });
    } else {
      updateVisualInfo(
        mode === '1'
          ? {
              ...visualStepInfo,
              function_graph_type: tmpGraphType,
              graph_list: tmpGraphList,
            }
          : mode === '2'
          ? {
              ...visualStepInfo,
              function_graph_type: tmpGraphType,
              items: tmpGraphItems,
            }
          : {
              function_graph_type: tmpGraphType,
              graph_list: tmpGraphList,
              items: tmpGraphItems,
            },
      );

      displayNotification({
        message: mode !== '3' ? 'Save completed' : 'Delete Completed',
        description:
          mode !== '3'
            ? 'Graph saving has been successfully completed.'
            : 'Graph deletion has been successfully completed.',
        duration: 3,
        style: { borderLeft: '8px solid green' },
      });

      if (mode === '1') {
        setAddType('');
        setAddScript(defaultScript);
      } else if (mode === '3') {
        if (tmpGraphType.length === 1) {
          setMode('1');
        }
        setAddType('');
        setEditType('');
        setEditScript('');
      }

      graphArea.current.removeAttribute('class');
      graphArea.current.firstChild?.remove();
      setIsPreview(false);
    }
  };

  const changeMode = (v) => {
    if (v === '1' || mode === '1') {
      graphArea.current.removeAttribute('class');
      graphArea.current.firstChild?.remove();
      setIsPreview(false);
    }
    setMode(v);
  };

  const closeManagement = () => {
    closer();
    setErrorMsg('');
    setMode('1');
    setAddType('');
    setEditType('');
    setAddScript(defaultScript);
    setEditScript('');
    setAddData({
      x: '0',
      y: [],
      z: '0',
    });
    setEditData({
      x: '0',
      y: [],
      z: '0',
    });
    setIsPreview(false);
    graphArea.current.removeAttribute('class');
    graphArea.current.firstChild?.remove();
  };

  useEffect(() => {
    const currentData = mode === '1' ? addData : editData;
    if (currentData.y.length > 0 && errorMsg.length === 0) {
      renderGraph();
    }
  }, [errorMsg]);

  return (
    <CSSTransition in={isOpen} classNames="modal" unmountOnExit timeout={100}>
      <>
        <div css={SG.backgroundStyle} />
        <div css={SG.mainStyle}>
          <div>
            <div>User Graph Management</div>
            <div>
              <Button onClick={closeManagement}>Close</Button>
              {mode === '3' ? (
                <Popconfirm
                  title={
                    <div css={SG.popconfirmWrapper}>
                      <p>Are you sure you want to delete this graph type?</p>
                      <p>
                        Warning: Graphs using this graph type will also be
                        deleted.
                      </p>
                    </div>
                  }
                  onConfirm={onApply}
                >
                  <Button type="primary">Delete</Button>
                </Popconfirm>
              ) : (
                <Button type="primary" onClick={onApply}>
                  Save
                </Button>
              )}
            </div>
          </div>
          <div>
            <div>
              <Form labelAlign="left">
                <Item label="Mode">
                  <Group
                    onChange={(e) => changeMode(e.target.value)}
                    value={mode}
                  >
                    <Radio value="1">Add</Radio>
                    <Radio
                      value="2"
                      disabled={
                        visualStepInfo.function_graph_type.find(
                          (v) => v.type === 'user',
                        ) === undefined
                      }
                    >
                      Edit
                    </Radio>
                    <Radio
                      value="3"
                      disabled={
                        visualStepInfo.function_graph_type.find(
                          (v) => v.type === 'user',
                        ) === undefined
                      }
                    >
                      Delete
                    </Radio>
                  </Group>
                </Item>
                <SideMenu
                  mode={mode}
                  type={mode === '1' ? addType : editType}
                  values={mode === '1' ? addData : editData}
                  options={{
                    type: visualStepInfo.function_graph_type,
                    ...optionList,
                  }}
                  changeFunc={changeData}
                />
                <Item>
                  <StyledEditor>
                    <AceEditor
                      mode="javascript"
                      theme="tomorrow"
                      width="100%"
                      showGutter
                      highlightActiveLine
                      value={mode === '1' ? addScript : editScript}
                      onChange={(v) => changeData('script', v)}
                      setOptions={{
                        tabSize: 2,
                        showPrintMargin: false,
                        showLineNumbers: true,
                        useWorker: false,
                      }}
                    />
                  </StyledEditor>
                </Item>
              </Form>
            </div>
            <div>
              <Button
                type="primary"
                onClick={renderGraph}
                disabled={disablePreview()}
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
});
GraphManagement.propTypes = {
  closer: PropTypes.func.isRequired,
  isOpen: PropTypes.bool.isRequired,
};

const SideMenu = React.memo(({ mode, type, values, options, changeFunc }) => {
  const yzOptionList = useMemo(() => createYZoptionList(options.y), [
    JSON.stringify(options.y),
  ]);

  return (
    <>
      <Item label="Graph Type">
        {mode !== '1' ? (
          <Select value={type} onChange={(v) => changeFunc('type', v)}>
            {options.type.map((v) => {
              if (v.type !== 'system') {
                return (
                  <Option value={v.name} key={v.name}>
                    {mode === '2' ? (
                      <Tooltip
                        placement="right"
                        title="Unsaved data will be lost when you change the graph type."
                      >
                        {v.name}
                      </Tooltip>
                    ) : (
                      <>{v.name}</>
                    )}
                  </Option>
                );
              }
            })}
          </Select>
        ) : (
          <Input
            value={type}
            onChange={(e) => changeFunc('type', e.target.value)}
            maxLength="30"
          />
        )}
      </Item>
      <Item label="Axis(X)">
        <Select value={values.x} onChange={(v) => changeFunc('x', v)}>
          <Option value="0">None</Option>
          {options.x.map(RenderSelectOptions)}
        </Select>
      </Item>
      <Item label="Axis(Y)">
        {Array.isArray(options.y) ? (
          <Select
            mode="multiple"
            value={values.y}
            onChange={(v) => changeFunc('y', v)}
            maxTagCount="responsive"
          >
            {options.y.map(RenderSelectOptions)}
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
        {Array.isArray(options.z) ? (
          <Select value={values.z} onChange={(v) => changeFunc('z', v)}>
            <Option value="0">None</Option>
            {options.z.map(RenderSelectOptions)}
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
SideMenu.propTypes = {
  mode: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  values: PropTypes.object.isRequired,
  options: PropTypes.object.isRequired,
  changeFunc: PropTypes.func.isRequired,
};
SideMenu.displayName = 'SideMenu';

export default GraphManagement;
