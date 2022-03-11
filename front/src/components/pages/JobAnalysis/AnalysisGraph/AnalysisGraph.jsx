import React, { useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { Button, Empty } from 'antd';
import { LineChartOutlined } from '@ant-design/icons';
import { drawGraph, usePrevious } from './functionGroup';
import GraphAddEdit from '../../../UI/organisms/GraphAddEdit/GraphAddEdit';
import useModal from '../../../../lib/util/modalControl/useModal';
import useResultInfo from '../../../../hooks/useResultInfo';
import GraphComponent from './Fragments/GraphComponent';
import * as sg from './styleGroup';

const AnalysisGraph = ({ rows, info, type }) => {
  const { openModal } = useModal();
  const {
    visualization,
    analysisGraphInfo,
    originalGraphInfo,
    setAnalysisGraphInfo,
    setOriginalGraphInfo,
  } = useResultInfo();
  const previousInfo = usePrevious(info);
  const previousRows = usePrevious(rows);

  const handleClick = useCallback((idx, mode) => {
    openModal(GraphAddEdit, {
      isOpen: true,
      mode: mode,
      index: idx,
      type: type,
    });
  }, []);

  const onDelete = useCallback(
    (idx) => {
      if (type === 'analysis') {
        setAnalysisGraphInfo(
          analysisGraphInfo.map((v, i) => {
            return i === idx ? '' : v;
          }),
        );
      } else {
        setOriginalGraphInfo(
          originalGraphInfo.map((v, i) => {
            return i === idx ? '' : v;
          }),
        );
      }
    },
    [analysisGraphInfo, originalGraphInfo],
  );

  useEffect(() => {
    const rowChanged = JSON.stringify(previousRows) !== JSON.stringify(rows);
    const infoChanged = JSON.stringify(previousInfo) !== JSON.stringify(info);

    if ((rowChanged || infoChanged) && Object.keys(rows).length > 0) {
      info.forEach((v, i) => {
        const isChange =
          previousInfo === undefined ||
          JSON.stringify(previousInfo[i]) !== JSON.stringify(v) ||
          rowChanged;
        if (isChange && v !== '') {
          drawGraph(rows, v, visualization, type, i);
        }
      });
    }
  }, [rows, info]);

  if (Object.keys(rows).length === 0) return '';

  return (
    <>
      <div css={sg.mainWrapper}>
        <div>
          <span>Visualization</span>
          <Button
            type="dashed"
            icon={<LineChartOutlined />}
            onClick={() => handleClick(null, 'add')}
          >
            Add Graph
          </Button>
        </div>
        <div>
          <div
            css={
              info.length > 0 && info.filter((v) => v !== '').length > 0
                ? sg.graphBodyStyle
                : sg.emptyWrapper
            }
          >
            {info.length > 0 && info.filter((v) => v !== '').length > 0 ? (
              info.map((k, i) => {
                return k !== '' ? (
                  <GraphComponent
                    key={i}
                    index={i}
                    editFunc={handleClick}
                    deleteFunc={onDelete}
                    type={type}
                  />
                ) : (
                  ''
                );
              })
            ) : (
              <Empty description="No graphs to display." />
            )}
          </div>
        </div>
      </div>
    </>
  );
};

AnalysisGraph.propTypes = {
  rows: PropTypes.object.isRequired,
  info: PropTypes.array.isRequired,
  type: PropTypes.string,
};
AnalysisGraph.defaultProps = {
  type: 'analysis',
};
AnalysisGraph.displayName = 'AnalysisGraph';

export default AnalysisGraph;
