import useRuleSettingInfo from '../../../hooks/useRuleSettingInfo';
import React, { useEffect, useState } from 'react';
import { Collapse, Form, Table, Button, Tooltip } from 'antd';
import {
  MSG_ANYCHARACTER_REGEXP,
  MSG_COMMON_REGEXP,
  MSG_PREVIOUS_TABLE,
  MSG_SELECT_COMBOBOX,
  MSG_STEP4_FILTER,
  MSG_TABLE_TITLE_DELETE,
  MSG_TABLE_TITLE_FILTER_CONDITION,
  MSG_TABLE_TITLE_FILTER_NAME,
  MSG_TABLE_TITLE_FILTER_TYPE,
  MSG_TABLE_TITLE_INDEX,
} from '../../../lib/api/Define/Message';
import PropTypes from 'prop-types';
import { E_STEP_3 } from '../../../lib/api/Define/etc';
import { css } from '@emotion/react';
import { useDebouncedCallback } from 'use-debounce';
import TableComponent from './TableComponents';
import QuestionCircleOutlined from '@ant-design/icons/lib/icons/QuestionCircleOutlined';
import { AnyRegex, CommonRegex } from '../../../lib/util/RegExp';

const { Panel } = Collapse;
const { Column } = Table;
const tableWrapper = css`
  display: flex;
  & table {
    &:first-of-type > thead > tr > th {
      background: #f0f5ff;
    }
  }
  & table > tbody > tr {
    & > td {
      &:first-of-type {
        text-align: center;
      }
      &:last-of-type {
        text-align: center;
      }
    }
  }
`;

const FilterTable = ({ dataSource, deleteHandler, options, onChangeText }) => {
  return (
    <div>
      <Table
        bordered
        pagination={false}
        size="small"
        rowKey="key"
        dataSource={dataSource}
        scroll={{ x: 'max-content' }}
      >
        <Column
          title={MSG_TABLE_TITLE_INDEX}
          dataIndex="idx"
          key="idx"
          render={(_, row, index) => {
            return <>{index + 1}</>;
          }}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_COMMON_REGEXP}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_FILTER_NAME}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="name"
          key="name"
          render={(_, record) => (
            <TableComponent.input
              target={'name'}
              record={record}
              onChange={onChangeText}
              size={'middle'}
              regEx={{ pattern: CommonRegex, message: '' }}
            />
          )}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_SELECT_COMBOBOX}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_FILTER_TYPE}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="type"
          key="type"
          render={(_, record) => (
            <TableComponent.select
              target={'type'}
              record={record}
              options={options}
              onChange={onChangeText}
              size={'middle'}
              regEx={{ pattern: AnyRegex, message: '' }}
            />
          )}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_ANYCHARACTER_REGEXP}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_FILTER_CONDITION}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="condition"
          key="condition"
          render={(_, record) => (
            <TableComponent.input
              target={'condition'}
              record={record}
              onChange={onChangeText}
              size={'middle'}
              regEx={{ pattern: AnyRegex, message: '' }}
            />
          )}
        />
        <Column
          title={MSG_TABLE_TITLE_DELETE}
          dataIndex="delete"
          key="delete"
          render={(_, record) => (
            <TableComponent.delete
              record={record}
              deleteHandler={deleteHandler}
              type={'custom'}
            />
          )}
        />
      </Table>
    </div>
  );
};
FilterTable.propTypes = {
  dataSource: PropTypes.array,
  deleteHandler: PropTypes.func,
  options: PropTypes.array,
  onChangeText: PropTypes.func,
};

const FilterSetting = ({ data }) => {
  const {
    ruleStepConfig,
    updateFilterInfo,
    filterStepInfo,
  } = useRuleSettingInfo();
  const [config, setConfig] = useState(null);
  const [filterData, setFilterData] = useState([]);
  const { convert_header, convert_data } = data;
  const newData = { ['key']: '', name: '', type: '', condition: '' };
  const [form] = Form.useForm();
  const setDeboundcedText = useDebouncedCallback(
    ({ target, record, value }) => onInputChange(target, record, value),
    100,
  );

  useEffect(() => {
    console.log('[useEffect]filterData: ', filterData);
    updateFilterInfo(filterData);
  }, [filterData]);

  const handleDelete = (key) => {
    setFilterData(filterData.filter((item) => item.key !== key));
  };
  const handleAdd = () => {
    newData.key =
      filterData.length === 0 ? 1 : filterData[filterData.length - 1].key + 1;
    setFilterData([...filterData, newData]);
  };
  const onChangeText = ({ record, target, value }) => {
    setDeboundcedText({ record, target, value });
  };

  const onInputChange = (target, record, value) => {
    setFilterData(
      filterData.map((obj) =>
        obj.key === record.key ? { ...obj, [target]: value } : obj,
      ),
    );
  };

  useEffect(() => {
    console.log('[STEP4]data: ', data);
    const ruleConfig = ruleStepConfig.find((item) => item.step === E_STEP_3);
    console.log('[STEP4]ruleConfig: ', ruleConfig);
    setConfig(ruleConfig?.config?.filter);
    setFilterData(filterStepInfo);
  }, []);

  if (config === null) return <></>;
  console.log('filterStepInfo', filterStepInfo);

  return (
    <div css={{ maxWidth: '85%', minWidth: '75%' }}>
      <Collapse defaultActiveKey={[1, 2]}>
        <Panel header={MSG_PREVIOUS_TABLE} key="1">
          {convert_header !== undefined ? (
            <div
              style={{
                fontWeight: '14px',
                margin: '10px',
                display: 'flex',
                justifyContent: 'center',
              }}
            >
              <Table
                bordered
                pagination={false}
                columns={convert_header ?? []}
                dataSource={convert_data ?? []}
                size="middle"
                rowKey="key"
                scroll={{ x: 'max-content' }}
              />
            </div>
          ) : (
            <div />
          )}
        </Panel>
        <Panel header={MSG_STEP4_FILTER} key="2">
          <Form form={form} layout="vertical">
            <Button
              onClick={() => handleAdd()}
              type="primary"
              style={{
                marginBottom: 16,
              }}
            >
              Add a row
            </Button>
            <div css={tableWrapper} style={{ fontWeight: '12px' }}>
              <FilterTable
                options={config?.filter_type ?? []}
                deleteHandler={handleDelete}
                dataSource={filterData}
                onChangeText={onChangeText}
              />
            </div>
          </Form>
        </Panel>
      </Collapse>
    </div>
  );
};
FilterSetting.propTypes = {
  data: PropTypes.object,
};
export default FilterSetting;
