import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router';
import PropTypes from 'prop-types';
import dayjs from 'dayjs';
import { Tabs, Modal, Input, Form, Breadcrumb, Spin } from 'antd';
import Button from '../../UI/atoms/Button';
import {
  SaveOutlined,
  SlidersFilled,
  CloudDownloadOutlined,
  HomeOutlined,
} from '@ant-design/icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChartBar, faTable } from '@fortawesome/free-solid-svg-icons';
import {
  getAnalysisOptionInfo,
  getOriginalData,
  postHistoryData,
  postRequestExport,
} from '../../../lib/api/axios/requests';
import { RESPONSE_OK, DATE_FORMAT } from '../../../lib/api/Define/etc';
import { createGraphItems } from './functionGroup';
import ModalProvider from '../../../lib/util/modalControl/ModalProvider';
import AnalysisTable from './AnalysisTable/AnalysisTable';
import AnalysisGraph from './AnalysisGraph/AnalysisGraph';
import { default as GraphModal } from '../../../lib/util/modalControl/Modal';
import useResultInfo from '../../../hooks/useResultInfo';
import * as sg from './styleGroup';
import * as fn from './functionGroup';

const ResultMain = React.memo(() => {
  const {
    func_id,
    job_id,
    job_type,
    history_id,
    equipment_name,
    db_id,
    sql,
    list,
  } = useLocation().state;

  const {
    visualization,
    analysisData,
    originalData,
    originalFilteredRows,
    analysisGraphInfo,
    originalGraphInfo,
    selectedRow,
    setAnalysisInfo,
    setOriginalInfo,
    setOriginalFilteredRows,
    setVisualization,
    setAnalysisGraphInfo,
    setOriginalGraphInfo,
    initializing,
  } = useResultInfo();
  const [activeTab, setActiveTab] = useState('1');
  const [loadState, setLoadState] = useState(true);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [exportOpen, setExportOpen] = useState(false);
  const [checkTable, setCheckTable] = useState(false);
  const [checkGraph, setCheckGraph] = useState(false);
  const [isRenderGraph, setIsRenderGraph] = useState(false);
  const [isOriginal, setIsOriginal] = useState(false);
  const [historyName, setHistoryName] = useState(dayjs().format(DATE_FORMAT));

  const changeTab = useCallback((v) => {
    setActiveTab(v);
  }, []);

  const changeLoadState = useCallback((v) => {
    setLoadState(v);
  }, []);

  const clickData = async () => {
    changeLoadState(true);

    const dateStr =
      analysisData.period.selected.length > 0
        ? analysisData.period.selected
        : [analysisData.period.start, analysisData.period.end];
    let param = {
      fId: func_id,
      start: dateStr[0],
      end: dateStr[1],
    };

    if (
      analysisData.type.match(/multi/) === null ||
      analysisData.type.match(/setting/)
    ) {
      param = {
        ...param,
        rId: job_id,
        agMain:
          Object.keys(analysisData.aggregation).length > 0
            ? analysisData.aggregation.selected
            : '',
        agSub:
          Object.keys(analysisData.aggregation).length > 0
            ? analysisData.aggregation.selected.indexOf('all') === -1
              ? analysisData.aggregation.subItem[
                  analysisData.aggregation.selected
                ].selected
              : ''
            : '',
        filter: analysisData.filter,
        selected: selectedRow[0] === 'all' ? [] : selectedRow,
      };
    }

    const {
      data,
      option,
      items,
      message,
      common_axis_x,
    } = await getOriginalData(param, analysisData.type);
    const rowData = fn.createAnalysisData(analysisData.type, data, 'row');

    changeLoadState(false);

    if (message !== '') {
      fn.displayNotification({
        message: 'Error occurred',
        description: message,
        duration: 3,
        style: { borderLeft: '5px solid red' },
      });
    } else {
      setOriginalInfo({
        period: analysisData.period,
        filter: option.filter,
        aggregation: {},
        dispOrder: fn.createAnalysisData(analysisData.type, data, 'disp_order'),
        dispGraph: fn.createAnalysisData(analysisData.type, data, 'disp_graph'),
        data: rowData,
        common_axis_x: common_axis_x,
      });
      setOriginalFilteredRows(rowData);
      setOriginalGraphInfo(
        createGraphItems({
          function_graph_type: visualization.function_graph_type,
          graph_list: visualization.graph_list,
          items: items,
        }),
      );

      if (Object.keys(rowData).length > 0) {
        changeTab('2');
      } else {
        fn.displayNotification({
          message: 'No Data',
          description: 'There is no data to display.',
          duration: 3,
          style: { borderLeft: '5px solid green' },
        });
      }
    }
  };

  const saveHistory = async () => {
    setHistoryOpen(false);
    setLoadState(true);
    const tmpFilter = {};
    const infoKey = job_type === 'multi' ? 'infos' : 'info';
    analysisData.filter.reduce((acc, v) => {
      acc[v.target] =
        v.selected === undefined || v.selected === null ? '' : v.selected;
      return acc;
    }, tmpFilter);
    let tmpObj = {
      func_id: func_id,
      source: job_type,
      title: historyName,
      period: {
        start:
          analysisData.period.selected.length === 0
            ? analysisData.period.start
            : analysisData.period.selected[0],
        end:
          analysisData.period.selected.length === 0
            ? analysisData.period.end
            : analysisData.period.selected[1],
      },
      filter: tmpFilter,
      aggregation:
        Object.keys(analysisData.aggregation).length === 0
          ? {}
          : {
              [analysisData.aggregation.selected]:
                analysisData.aggregation.selected.indexOf('all') === -1
                  ? analysisData.aggregation.subItem[
                      analysisData.aggregation.selected
                    ].selected
                  : '',
            },
      visualization: {
        items:
          analysisGraphInfo.length === 0
            ? []
            : analysisGraphInfo
                .filter((v) => v !== '')
                .map((v) => {
                  return {
                    ...v,
                    y_axis: !Array.isArray(v.y_axis[0])
                      ? v.y_axis
                      : v.y_axis.map((x) => x.join('/')),
                    z_axis: Array.isArray(v.z_axis)
                      ? v.z_axis.join('/')
                      : v.z_axis,
                  };
                }),
      },
    };

    tmpObj[infoKey] = fn.createHistoryInfo({
      func_id,
      job_id,
      job_type,
      history_id,
      equipment_name,
      db_id,
      sql,
      list,
    });

    const { status } = await postHistoryData(tmpObj);
    setLoadState(false);

    fn.displayNotification({
      message:
        status === RESPONSE_OK
          ? 'History Save Successful'
          : 'History Save Failed',
      description:
        status === RESPONSE_OK
          ? 'Successfully saved history.'
          : 'Failed to save history. Please change the name and try again.',
      duration: 3,
      style:
        status === RESPONSE_OK
          ? { borderLeft: '5px solid green' }
          : { borderLeft: '5px solid red' },
    });

    if (status === RESPONSE_OK) {
      setHistoryName(dayjs().format(DATE_FORMAT));
    }
  };

  const executeExport = async () => {
    setExportOpen(false);
    setLoadState(true);
    const form = new FormData();

    if (checkTable) {
      fn.createExportTableData(
        analysisData.data,
        analysisData.dispOrder,
        'analysis',
        form,
      );
      if (Object.keys(originalData.data).length > 0) {
        fn.createExportTableData(
          originalData.data,
          originalData.dispOrder,
          'data',
          form,
        );
      }
    }

    if (checkGraph && isRenderGraph) {
      const imgData = await fn.createGraphImage();
      imgData.forEach((v) => {
        form.append('files', new File([v.url], v.filename));
      });
    }

    const status = await postRequestExport(form);
    setLoadState(false);
    setCheckGraph(false);
    setCheckTable(false);

    fn.displayNotification({
      message: status === RESPONSE_OK ? 'Export Successful' : 'Export Failed',
      description:
        status === RESPONSE_OK
          ? 'Successfully export data.'
          : 'Failed to export data. Please try again.',
      duration: 3,
      style:
        status === RESPONSE_OK
          ? { borderLeft: '5px solid green' }
          : { borderLeft: '5px solid red' },
    });
  };

  const openExport = useCallback(() => {
    setIsRenderGraph(
      document.querySelectorAll('div[class^="js-plotly-plot"]').length > 0,
    );
    setExportOpen(true);
  }, []);

  const closeExport = useCallback(() => {
    setCheckTable(false);
    setCheckGraph(false);
    setExportOpen(false);
  }, []);

  const buttonDisableCheck = () => {
    if (analysisData.type.match(/multi/) === null) {
      return activeTab !== '1' || selectedRow.length === 0;
    } else {
      return activeTab !== '1' || analysisData.type.match(/none/) !== null;
    }
  };

  useEffect(() => {
    const fetch = async () => {
      const rid =
        history_id !== 'undefined' && history_id !== undefined
          ? history_id
          : job_id;
      const data = await getAnalysisOptionInfo(func_id, rid, job_type);
      setAnalysisInfo({
        type: data.analysis_type,
        period: {
          ...data.period,
          start:
            data.period.start.length > 0
              ? dayjs(data.period.start).format(DATE_FORMAT)
              : '',
          end:
            data.period.end.length > 0
              ? dayjs(data.period.end).format(DATE_FORMAT)
              : '',
        },
        filter: data.filter,
        aggregation: data.aggregation ?? {},
        dispOrder: fn.createAnalysisData(
          data.analysis_type,
          data.data,
          'disp_order',
        ),
        dispGraph: fn.createAnalysisData(
          data.analysis_type,
          data.data,
          'disp_graph',
        ),
        data: fn.createAnalysisData(data.analysis_type, data.data, 'row'),
        common_axis_x: data.analysis_type.match(/multi/)
          ? data.visualization.common_axis_x
          : [],
      });
      setVisualization({ ...data.visualization });
      setAnalysisGraphInfo(createGraphItems(data.visualization));
      if (data.analysis_type.match(/none/)) {
        setIsOriginal(true);
      }
    };
    fetch()
      .then(() => changeLoadState(false))
      .catch((e) => {
        console.log(e);
        changeLoadState(false);
      });
    return () => {
      initializing();
      const plotlyElement = document.getElementById('js-plotly-tester');
      if (plotlyElement) {
        plotlyElement.remove();
      }
      return null;
    };
  }, [func_id, job_type, history_id, job_id]);

  return (
    <ModalProvider>
      <ResultModal
        title="Save History"
        open={historyOpen}
        ok={saveHistory}
        cancel={() => setHistoryOpen(false)}
        okText="Save"
      >
        <Form.Item label="Title" style={{ marginBottom: 0 }}>
          <Input
            value={historyName}
            onChange={(e) => setHistoryName(e.target.value)}
            maxLength="20"
          />
        </Form.Item>
      </ResultModal>
      <ResultModal
        title="Export"
        open={exportOpen}
        ok={executeExport}
        cancel={() => closeExport()}
        okText="Download"
        width={400}
      >
        <div
          css={[
            sg.exportModalWrapper,
            !isRenderGraph ? { gridTemplateColumns: 'auto' } : {},
          ]}
        >
          <input
            type="checkbox"
            id="table"
            checked={checkTable}
            onChange={() => setCheckTable(!checkTable)}
          />
          <label htmlFor="table">
            <svg viewBox="0 0 21 21">
              <polyline points="5 10.75 8.5 14.25 16 6" />
            </svg>
            <FontAwesomeIcon icon={faTable} size="2x" />
            <span>Table</span>
          </label>
          {isRenderGraph ? (
            <>
              <input
                type="checkbox"
                id="graph"
                checked={checkGraph}
                onChange={() => setCheckGraph(!checkGraph)}
              />
              <label htmlFor="graph">
                <svg viewBox="0 0 21 21">
                  <polyline points="5 10.75 8.5 14.25 16 6" />
                </svg>
                <FontAwesomeIcon icon={faChartBar} size="2x" />
                <span>Graph</span>
              </label>
            </>
          ) : (
            ''
          )}
        </div>
      </ResultModal>
      <div css={sg.mainWrapper} className={loadState ? 'loading' : ''}>
        <div css={sg.breadcrumbWrapper}>
          <Breadcrumb>
            <Breadcrumb.Item>
              <HomeOutlined /> Home
            </Breadcrumb.Item>
            <Breadcrumb.Item>Analysis</Breadcrumb.Item>
          </Breadcrumb>
        </div>
        <div css={sg.buttonWrapper}>
          <Button
            theme="white"
            style={{ fontWeight: 'normal' }}
            disabled={buttonDisableCheck()}
            onClick={clickData}
          >
            <SlidersFilled /> Show Data
          </Button>
          <Button
            theme="white"
            style={{ fontWeight: 'normal' }}
            onClick={() => setHistoryOpen(true)}
            disabled={Object.keys(analysisData.data).length === 0}
          >
            <SaveOutlined /> Save History
          </Button>
          <Button
            theme="white"
            style={{ fontWeight: 'normal' }}
            onClick={openExport}
            disabled={Object.keys(analysisData.data).length === 0}
          >
            <CloudDownloadOutlined /> Export
          </Button>
        </div>
        <Spin size="large" tip="Loading..." spinning={loadState}>
          <Tabs activeKey={activeTab} onChange={changeTab}>
            <Tabs.TabPane tab="Analysis" key="1">
              <div css={sg.tableWrapper}>
                <AnalysisTable
                  period={analysisData.period}
                  filter={analysisData.filter}
                  aggregation={analysisData.aggregation}
                  tableData={analysisData.data}
                  tableOrder={analysisData.dispOrder}
                  type={isOriginal ? 'data' : 'analysis'}
                  onLoad={changeLoadState}
                  detailType={analysisData.type}
                  useUpdate
                />
                <AnalysisGraph
                  rows={analysisData.data}
                  info={analysisGraphInfo}
                />
              </div>
            </Tabs.TabPane>
            {originalData.data !== undefined &&
            Object.keys(originalData.data).length > 0 ? (
              <Tabs.TabPane tab="Data" key="2">
                <div css={sg.tableWrapper}>
                  <AnalysisTable
                    period={originalData.period}
                    filter={originalData.filter}
                    aggregation={originalData.aggregation}
                    tableData={originalFilteredRows}
                    tableOrder={originalData.dispOrder}
                    type="data"
                    onLoad={changeLoadState}
                    useUpdate={false}
                  />
                  <AnalysisGraph
                    rows={originalFilteredRows}
                    info={originalGraphInfo}
                    type="data"
                  />
                </div>
              </Tabs.TabPane>
            ) : (
              ''
            )}
          </Tabs>
        </Spin>
      </div>
      <GraphModal />
    </ModalProvider>
  );
});
ResultMain.displayName = 'ResultMain';

const ResultModal = React.memo(
  ({ title, okText, open, ok, cancel, width, children }) => {
    return (
      <Modal
        title={title}
        visible={open}
        onOk={ok}
        onCancel={cancel}
        okText={okText ? okText : 'OK'}
        style={{ fontFamily: 'saira' }}
        width={width}
      >
        {children}
      </Modal>
    );
  },
);

ResultModal.displayName = 'ResultModal';
ResultModal.propTypes = {
  title: PropTypes.string.isRequired,
  okText: PropTypes.string,
  open: PropTypes.bool.isRequired,
  ok: PropTypes.func.isRequired,
  cancel: PropTypes.func.isRequired,
  width: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  children: PropTypes.node,
};

export default ResultMain;
