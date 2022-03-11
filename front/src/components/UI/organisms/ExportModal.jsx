import React, { useEffect, useState } from 'react';
import { Modal } from '../../UI/atoms/Modal';
import PropTypes from 'prop-types';
import Button from '../../UI/atoms/Button';
import { css } from '@emotion/react';
import {
  getGraphImage,
  download,
  jsonToCSV,
} from '../../../lib/util/plotly-test';
import useAnalysisInfo from '../../../hooks/useAnalysisInfo';
import { Checkbox, Col, Row } from 'antd';
import { BarChartOutlined, TableOutlined } from '@ant-design/icons';

/*****************************************************************************
 *              ModalFooter
 *****************************************************************************/
const footerStyle = css`
  display: flex;
  justify-content: flex-end;
  align-items: center;
`;

const ModalFooter = ({ downloadFunc, closeFunc }) => {
  const [loading, setLoading] = useState(false);
  const onClickEvent = (e) => {
    if (loading === false) {
      setLoading(e);
      downloadFunc();
    }
  };
  return (
    <>
      <div css={footerStyle}>
        <Button
          theme={'white'}
          onClick={() => onClickEvent(!loading)}
          loading={loading}
          style={{ marginLeft: '8px', fontWeight: 400 }}
        >
          {loading ? 'Downloading' : 'Download'}
        </Button>
        <Button
          theme={'blue'}
          onClick={closeFunc}
          style={{ marginLeft: '8px', fontWeight: 400 }}
        >
          {'Cancel'}
        </Button>
      </div>
    </>
  );
};

ModalFooter.propTypes = {
  downloadFunc: PropTypes.func.isRequired,
  closeFunc: PropTypes.func.isRequired,
};

/*****************************************************************************
 *              ModalContents
 *****************************************************************************/
const ContentsStyle = css`
  display: contents;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  padding: 0px;
`;

const ModalContents = ({ changeFunc }) => {
  return (
    <>
      <div css={ContentsStyle}>
        <Checkbox.Group style={{ width: '100%' }} onChange={changeFunc}>
          <Row style={{ position: 'relative', left: '64px' }}>
            <Col style={{ display: 'inline-grid' }}>
              <Checkbox value="Table">Table</Checkbox>
              <TableOutlined style={{ fontSize: '64px' }} />
            </Col>
            <Col style={{ display: 'inline-grid', left: '64px' }}>
              <Checkbox value="Graph">Graph</Checkbox>
              <BarChartOutlined style={{ fontSize: '64px' }} />
            </Col>
          </Row>
        </Checkbox.Group>
      </div>
    </>
  );
};
ModalContents.propTypes = {
  changeFunc: PropTypes.func.isRequired,
};
/*****************************************************************************
 *              ExportModal
 *****************************************************************************/

const ExportModal = ({ isOpen, closeFunc }) => {
  const {
    SummaryData,
    DetailData,
    SummaryYAxis,
    DetailYAxis,
  } = useAnalysisInfo();
  const [checkedValues, setCheckedValues] = useState([]);
  const [graphData, setGraphData] = useState([]);
  useEffect(() => {
    if (isOpen === true) {
      const result = getGraphImage(SummaryYAxis, DetailYAxis);
      console.log('result', result);
      setGraphData(result);
    }
  }, [isOpen]);

  const getTableCsv = (data) => {
    const convertJson = [];
    data.dataSource.map((row) => {
      const tmp = {};
      data.column.map((obj) =>
        Object.assign(tmp, { [obj.title]: row[obj.dataIndex] }),
      );
      convertJson.push(tmp);
    });
    return jsonToCSV(convertJson);
  };

  const DownloadEvent = async () => {
    if (checkedValues.length > 0) {
      const form = new FormData();
      const isGraph = checkedValues.includes('Graph');
      const isTable = checkedValues.includes('Table');

      if (isGraph) {
        graphData.map((obj) =>
          form.append('files', new File([obj.url], obj.filename)),
        );
      }
      if (isTable) {
        if (SummaryData.dataSource.length > 0) {
          form.append(
            'files',
            new File([getTableCsv(SummaryData)], `summary.table.csv`),
          );
        }
        if (DetailData.dataSource.length > 0) {
          form.append(
            'files',
            new File([getTableCsv(DetailData)], `detail.table.csv`),
          );
        }
      }
      if (form) download(form);
      closeFunc();
    }
  };
  return (
    <>
      <Modal
        width={'400px'}
        isOpen={isOpen}
        header={<div>{'Export Plate Auto Focus Compensation.'}</div>}
        content={<ModalContents changeFunc={setCheckedValues} />}
        footer={
          <ModalFooter
            closeFunc={closeFunc}
            downloadFunc={() => DownloadEvent()}
          />
        }
        closeIcon={true}
      />
    </>
  );
};

ExportModal.propTypes = {
  isOpen: PropTypes.bool,
  closeFunc: PropTypes.func,
};

export default ExportModal;
