import useRuleSettingInfo from '../../../hooks/useRuleSettingInfo';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Collapse, Form, Table, Button, Checkbox, Tooltip } from 'antd';
import {
  MSG_COEFFICIENT_REGEXP,
  MSG_COMMON_REGEXP,
  MSG_DEFAULT_TYPE_REGEXP,
  MSG_ONLY_NUMBER_REGEXP,
  MSG_REFER_TO_TOOLTIP,
  MSG_REFER_TO_TOOLTIP2,
  MSG_REQUIRED_TOOLTIP,
  MSG_RULENAME_REGEXP,
  MSG_SELECT_COMBOBOX,
  MSG_STEP3_CONVERT_SCRIPT,
  MSG_STEP3_CUSTOM,
  MSG_STEP3_DEFINE,
  MSG_STEP3_HEADERS,
  MSG_STEP3_INFO,
  MSG_STEP3_LOG_DEFINE,
  MSG_STEP3_SELECT,
  MSG_TABLE_TITLE_COEFFICIENT,
  MSG_TABLE_TITLE_DATA,
  MSG_TABLE_TITLE_DEFAULT,
  MSG_TABLE_TITLE_DELETE,
  MSG_TABLE_TITLE_INDEX,
  MSG_TABLE_TITLE_NAME,
  MSG_TABLE_TITLE_OUTPUT,
  MSG_TABLE_TITLE_ROW,
  MSG_TABLE_TITLE_TYPE,
  MSG_TABLE_TITLE_UNIT,
  MSG_TABLE_NAME_REGEXP,
  MSG_UNIT_REGEXP,
  MSG_UPLOAD_SCRIPT,
  MSG_TABLE_TITLE_SKIP,
} from '../../../lib/api/Define/Message';
import InputForm from '../../UI/atoms/Input/InputForm';
import PropTypes from 'prop-types';
import { MenuOutlined } from '@ant-design/icons';
import update from 'immutability-helper';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { E_STEP_3, RESPONSE_OK } from '../../../lib/api/Define/etc';
import { css } from '@emotion/react';
import TableComponent from './TableComponents';
import { useDebouncedCallback } from 'use-debounce';
import {
  getFileName,
  getParseData,
  sortArrayOfObjects,
} from '../../../lib/util/Util';
import { getRequest } from '../../../lib/api/axios/requests';
import NotificationBox from '../../UI/molecules/NotificationBox/Notification';
import { URL_RESOURCE } from '../../../lib/api/Define/URL';
import {
  AnyRegex,
  coefRegex,
  CommonRegex,
  NumberRegex,
  RuleNameRegex,
  TableNameRegex,
} from '../../../lib/util/RegExp';
import QuestionCircleOutlined from '@ant-design/icons/lib/icons/QuestionCircleOutlined';

const { Panel } = Collapse;
const { Column } = Table;

const DEFINE_TYPE = 'DraggableBodyRow';
const DEFINE_INFO_TYPE = 'info';
const DEFINE_HEADER_TYPE = 'header';
const DEFINE_CUSTOM_TYPE = 'custom';
const CUSTOM_SELECT = 'custom';
const TEXT_SELECT = 'text';
const LAMBDA_SELECT = 'lambda';

const tableWrapper = css`
  display: flex;
  & table {
    font-size: 12px;
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
const formWrapper = css`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: auto;
  column-gap: 1rem;
  & > div > .ant-form {
    max-width: 637px;
  }
  & .ant-form-item-label {
    text-align: left;
  }
`;

const step3_convert_script_style = css`
  & > div {
    max-width: 100%;
  }
  & label.ant-form-item-required {
    margin-right: 8px;
  }
  & .ant-col.ant-col-8.ant-form-item-label {
    flex-basis: 114px;
  }
  & .ant-form-item-label {
    text-align: left;
    flex-basis: 114px;
  }
  & .ant-upload-list-item-info {
    width: fit-content;
    & span.ant-upload-list-item-name {
      width: fit-content;
      max-width: 1192px;
    }
  }
`;

const inputNumberWrapper = css`
  & .ant-form-item {
    margin-right: 0;
  }
`;

const DraggableBodyRow = ({
  index,
  moveRow,
  className,
  style,
  ...restProps
}) => {
  const ref = useRef();
  const [{ isOver, dropClassName }, drop] = useDrop({
    accept: DEFINE_TYPE,
    collect: (monitor) => {
      const { index: dragIndex } = monitor.getItem() || {};
      if (dragIndex === index) {
        return {};
      }
      return {
        isOver: monitor.isOver(),
        dropClassName:
          dragIndex < index ? ' drop-over-downward' : ' drop-over-upward',
      };
    },
    drop: (item) => {
      moveRow(item.index, index);
    },
  });
  const [, drag] = useDrag({
    type: DEFINE_TYPE,
    item: { index },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });
  drop(drag(ref));

  return (
    <tr
      ref={ref}
      className={`${className}${isOver ? dropClassName : ''}`}
      style={{ cursor: 'move', ...style }}
      {...restProps}
    />
  );
};
DraggableBodyRow.propTypes = {
  index: PropTypes.number,
  moveRow: PropTypes.func,
  className: PropTypes.string,
  style: PropTypes.object,
};
const SelectDisable = (record, type) => {
  switch (record[type]) {
    case CUSTOM_SELECT:
    case TEXT_SELECT:
    case LAMBDA_SELECT:
      return false;
  }
  return true;
};

const InfoConvertTable = ({
  dataSource,
  deleteHandler,
  checkHandler,
  dataOptions,
  typeOptions,
  columnOptions,
  onChangeText,
  moveInfoRow,
  components,
  log_data,
  isEdit,
}) => {
  return (
    <div>
      <Table
        bordered
        components={components}
        pagination={false}
        size="small"
        rowKey="key"
        dataSource={dataSource}
        scroll={{ x: 'max-content' }}
        onRow={(record, index) => ({
          index,
          moveRow: moveInfoRow,
        })}
      >
        <Column
          title={'Sort'}
          dataIndex="sort"
          key="idx"
          width="30"
          className="drag-visible"
          render={() => (
            <MenuOutlined style={{ cursor: 'grab', color: '#999' }} />
          )}
        />
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
              title={MSG_ONLY_NUMBER_REGEXP}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_ROW}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="row_index"
          key="row_index"
          render={(_, record) => (
            <div css={inputNumberWrapper}>
              <TableComponent.inputNumber
                target={'row_index'}
                record={record}
                onChange={onChangeText}
                type={DEFINE_INFO_TYPE}
                regEx={{ pattern: NumberRegex, message: MSG_REFER_TO_TOOLTIP2 }}
                disabled={!!record?.skip}
              />
            </div>
          )}
        />
        <Column
          title={MSG_TABLE_TITLE_DATA}
          dataIndex="data"
          key="data"
          render={(_, row, index) => {
            return <>{log_data?.[`data_${index + 1}`] ?? ''}</>;
          }}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_COMMON_REGEXP}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_NAME}
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
              type={DEFINE_INFO_TYPE}
              regEx={{ pattern: CommonRegex, message: MSG_REFER_TO_TOOLTIP2 }}
              disabled={!!record?.skip}
            />
          )}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_COMMON_REGEXP}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_OUTPUT}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="output_column"
          key="output_column"
          render={(_, record) =>
            isEdit ? (
              <div css={{ display: 'flex', columnGap: '4px' }}>
                <TableComponent.input
                  target={'output_column'}
                  record={record}
                  type={DEFINE_INFO_TYPE}
                  onChange={onChangeText}
                  disabled={
                    !(
                      record.rec_type === 'DB' &&
                      record.output_column_val === 'custom'
                    ) || !!record?.skip
                  }
                  regEx={{
                    pattern: CommonRegex,
                    message: MSG_REFER_TO_TOOLTIP2,
                  }}
                />
                <TableComponent.select
                  target={'output_column_val'}
                  record={record}
                  type={DEFINE_INFO_TYPE}
                  onChange={onChangeText}
                  options={columnOptions}
                  regEx={{ pattern: AnyRegex, message: MSG_REFER_TO_TOOLTIP2 }}
                  disabled={!!record?.skip}
                />
              </div>
            ) : (
              <TableComponent.input
                target={'output_column'}
                record={record}
                type={DEFINE_INFO_TYPE}
                onChange={onChangeText}
                size={'middle'}
                regEx={{ pattern: CommonRegex, message: MSG_REFER_TO_TOOLTIP2 }}
                disabled={!!record?.skip}
              />
            )
          }
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_SELECT_COMBOBOX}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_TYPE}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="data_type"
          key="data_type"
          render={(_, record) => (
            <TableComponent.select
              target={'data_type'}
              record={record}
              options={dataOptions}
              onChange={onChangeText}
              type={DEFINE_INFO_TYPE}
              disabled={
                (isEdit &&
                  !(
                    record?.rec_type === 'DB' &&
                    record.output_column_val === 'custom'
                  )) ||
                !!record?.skip
              }
              regEx={{ pattern: AnyRegex, message: MSG_REFER_TO_TOOLTIP2 }}
            />
          )}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_DEFAULT_TYPE_REGEXP}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_DEFAULT}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="def_type"
          key="def_type"
          render={(_, record) => (
            <div css={{ display: 'flex', columnGap: '4px' }}>
              <TableComponent.input
                target={'def_val'}
                record={record}
                onChange={onChangeText}
                type={DEFINE_INFO_TYPE}
                disabled={SelectDisable(record, 'def_type') || !!record?.skip}
                regEx={{ pattern: AnyRegex, message: MSG_REFER_TO_TOOLTIP2 }}
              />
              <TableComponent.select
                target={'def_type'}
                record={record}
                options={typeOptions}
                onChange={onChangeText}
                type={DEFINE_INFO_TYPE}
                regEx={{ pattern: AnyRegex, message: MSG_REFER_TO_TOOLTIP2 }}
                disabled={!!record?.skip}
              />
            </div>
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
              type={DEFINE_INFO_TYPE}
              disabled={!!record?.skip}
            />
          )}
        />
        <Column
          title={MSG_TABLE_TITLE_SKIP}
          dataIndex="skip"
          key="skip"
          render={(_, record) => (
            <TableComponent.checkbox
              record={record}
              target={'skip'}
              checkHandler={checkHandler}
              type={DEFINE_INFO_TYPE}
            />
          )}
        />
      </Table>
    </div>
  );
};
InfoConvertTable.propTypes = {
  dataSource: PropTypes.array,
  deleteHandler: PropTypes.func,
  checkHandler: PropTypes.func,
  dataOptions: PropTypes.array,
  typeOptions: PropTypes.array,
  onChangeText: PropTypes.func,
  moveInfoRow: PropTypes.func,
  components: PropTypes.object,
  log_data: PropTypes.array,
  columnOptions: PropTypes.array,
  isEdit: PropTypes.bool,
};
const HeaderConvertTable = ({
  dataSource,
  deleteHandler,
  checkHandler,
  dataOptions,
  typeOptions,
  columnOptions,
  onChangeText,
  moveHeaderRow,
  components,
  log_data,
  isEdit,
}) => {
  const enableCoefficient = (record) => {
    return record.data_type === 'float' || record.data_type === 'integer';
  };
  return (
    <div>
      <Table
        bordered
        components={components}
        pagination={false}
        size="small"
        rowKey="key"
        dataSource={dataSource}
        scroll={{ x: 'max-content' }}
        onRow={(record, index) => ({
          index,
          moveRow: moveHeaderRow,
        })}
      >
        <Column
          title={'Sort'}
          dataIndex="sort"
          key="idx"
          width="30"
          className="drag-visible"
          render={() => (
            <MenuOutlined style={{ cursor: 'grab', color: '#999' }} />
          )}
        />
        <Column
          title={MSG_TABLE_TITLE_INDEX}
          dataIndex="idx"
          key="idx"
          render={(_, row, index) => {
            return <>{index + 1}</>;
          }}
        />
        <Column
          title={MSG_TABLE_TITLE_DATA}
          dataIndex="data"
          key="data"
          render={(_, row, index) => {
            return <>{log_data?.[`data_${index + 1}`] ?? ''}</>;
          }}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_COMMON_REGEXP}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_NAME}
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
              type={DEFINE_HEADER_TYPE}
              regEx={{ pattern: CommonRegex, message: MSG_REFER_TO_TOOLTIP2 }}
              disabled={!!record?.skip}
            />
          )}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_COMMON_REGEXP}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_OUTPUT}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="output_column"
          key="output_column"
          render={(_, record) =>
            isEdit ? (
              <div css={{ display: 'flex', columnGap: '4px' }}>
                <TableComponent.input
                  target={'output_column'}
                  record={record}
                  type={DEFINE_HEADER_TYPE}
                  onChange={onChangeText}
                  disabled={
                    !(
                      record.rec_type === 'DB' &&
                      record.output_column_val === 'custom'
                    ) || !!record?.skip
                  }
                  regEx={{
                    pattern: CommonRegex,
                    message: MSG_REFER_TO_TOOLTIP2,
                  }}
                />
                <TableComponent.select
                  target={'output_column_val'}
                  record={record}
                  type={DEFINE_HEADER_TYPE}
                  onChange={onChangeText}
                  options={columnOptions}
                  disabled={!!record?.skip}
                  regEx={{ pattern: AnyRegex, message: MSG_REFER_TO_TOOLTIP2 }}
                />
              </div>
            ) : (
              <TableComponent.input
                target={'output_column'}
                record={record}
                type={DEFINE_HEADER_TYPE}
                onChange={onChangeText}
                size={'middle'}
                disabled={!!record?.skip}
                regEx={{ pattern: CommonRegex, message: MSG_REFER_TO_TOOLTIP2 }}
              />
            )
          }
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_SELECT_COMBOBOX}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_TYPE}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="data_type"
          key="data_type"
          render={(_, record) => (
            <TableComponent.select
              target={'data_type'}
              record={record}
              options={dataOptions}
              onChange={onChangeText}
              type={DEFINE_HEADER_TYPE}
              disabled={
                (isEdit &&
                  !(
                    record?.rec_type === 'DB' &&
                    (record?.output_column_val ?? '') === 'custom'
                  )) ||
                !!record?.skip
              }
              regEx={{ pattern: AnyRegex, message: MSG_REFER_TO_TOOLTIP2 }}
            />
          )}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_DEFAULT_TYPE_REGEXP}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_DEFAULT}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="def_type"
          key="def_type"
          render={(_, record) => (
            <div css={{ display: 'flex', columnGap: '4px' }}>
              <TableComponent.input
                target={'def_val'}
                record={record}
                disabled={SelectDisable(record, 'def_type') || !!record?.skip}
                onChange={onChangeText}
                type={DEFINE_HEADER_TYPE}
                regEx={{ pattern: AnyRegex, message: MSG_REFER_TO_TOOLTIP2 }}
              />
              <TableComponent.select
                target={'def_type'}
                record={record}
                options={typeOptions}
                onChange={onChangeText}
                type={DEFINE_HEADER_TYPE}
                disabled={record?.skip}
                regEx={{ pattern: AnyRegex, message: MSG_REFER_TO_TOOLTIP2 }}
              />
            </div>
          )}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_COEFFICIENT_REGEXP}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_COEFFICIENT}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="coef"
          key="coef"
          render={(_, record) => (
            <TableComponent.input
              target={'coef'}
              record={record}
              onChange={onChangeText}
              type={DEFINE_HEADER_TYPE}
              disabled={!enableCoefficient(record) || !!record?.skip}
              regEx={{ pattern: coefRegex, message: '' }}
            />
          )}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_UNIT_REGEXP}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_UNIT}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="unit"
          key="unit"
          render={(_, record) => (
            <TableComponent.input
              target={'unit'}
              record={record}
              onChange={onChangeText}
              type={DEFINE_HEADER_TYPE}
              disabled={!!record?.skip}
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
              type={DEFINE_HEADER_TYPE}
              disabled={!!record?.skip}
            />
          )}
        />
        <Column
          title={MSG_TABLE_TITLE_SKIP}
          dataIndex="skip"
          key="skip"
          render={(_, record) => (
            <TableComponent.checkbox
              record={record}
              target={'skip'}
              checkHandler={checkHandler}
              type={DEFINE_HEADER_TYPE}
            />
          )}
        />
      </Table>
    </div>
  );
};
HeaderConvertTable.propTypes = {
  dataSource: PropTypes.array,
  deleteHandler: PropTypes.func,
  checkHandler: PropTypes.func,
  dataOptions: PropTypes.array,
  typeOptions: PropTypes.array,
  onChangeText: PropTypes.func,
  moveHeaderRow: PropTypes.func,
  components: PropTypes.object,
  log_data: PropTypes.array,
  col_data: PropTypes.object,
  columnOptions: PropTypes.array,
  isEdit: PropTypes.bool,
};
const CustomConvertTable = ({
  dataSource,
  deleteHandler,
  checkHandler,
  dataOptions,
  typeOptions,
  columnOptions,
  onChangeText,
  isEdit,
}) => {
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
              {MSG_TABLE_TITLE_NAME}
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
              type={DEFINE_CUSTOM_TYPE}
              onChange={onChangeText}
              size={'middle'}
              regEx={{ pattern: CommonRegex, message: MSG_REFER_TO_TOOLTIP2 }}
              disabled={!!record?.skip}
            />
          )}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_COMMON_REGEXP}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_OUTPUT}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="output_column"
          key="output_column"
          render={(_, record) =>
            isEdit ? (
              <div css={{ display: 'flex', columnGap: '4px' }}>
                <TableComponent.input
                  target={'output_column'}
                  record={record}
                  type={DEFINE_CUSTOM_TYPE}
                  onChange={onChangeText}
                  disabled={
                    !(
                      record.rec_type === 'DB' &&
                      record.output_column_val === 'custom'
                    ) || !!record?.skip
                  }
                  regEx={{
                    pattern: CommonRegex,
                    message: MSG_REFER_TO_TOOLTIP2,
                  }}
                />
                <TableComponent.select
                  target={'output_column_val'}
                  record={record}
                  type={DEFINE_CUSTOM_TYPE}
                  onChange={onChangeText}
                  options={columnOptions}
                  regEx={{ pattern: AnyRegex, message: MSG_REFER_TO_TOOLTIP2 }}
                  disabled={!!record?.skip}
                />
              </div>
            ) : (
              <TableComponent.input
                target={'output_column'}
                record={record}
                type={DEFINE_CUSTOM_TYPE}
                onChange={onChangeText}
                size={'middle'}
                regEx={{ pattern: CommonRegex, message: MSG_REFER_TO_TOOLTIP2 }}
                disabled={!!record?.skip}
              />
            )
          }
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_SELECT_COMBOBOX}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_TYPE}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="data_type"
          key="data_type"
          render={(_, record) => (
            <TableComponent.select
              target={'data_type'}
              record={record}
              options={dataOptions}
              type={DEFINE_CUSTOM_TYPE}
              onChange={onChangeText}
              disabled={
                (isEdit &&
                  !(
                    record?.rec_type === 'DB' &&
                    record.output_column_val === 'custom'
                  )) ||
                !!record?.skip
              }
              regEx={{ pattern: AnyRegex, message: MSG_REFER_TO_TOOLTIP2 }}
            />
          )}
        />
        <Column
          title={
            <Tooltip
              placement="topLeft"
              title={MSG_DEFAULT_TYPE_REGEXP}
              arrowPointAtCenter
            >
              {MSG_TABLE_TITLE_DEFAULT}
              <QuestionCircleOutlined
                style={{ marginLeft: '4px', color: 'rgb(24 144 255)' }}
              />
            </Tooltip>
          }
          dataIndex="def_type"
          key="def_type"
          render={(_, record) => (
            <div css={{ display: 'flex', columnGap: '4px' }}>
              <TableComponent.input
                target={'def_val'}
                record={record}
                type={DEFINE_CUSTOM_TYPE}
                onChange={onChangeText}
                disabled={SelectDisable(record, 'def_type') || !!record?.skip}
                regEx={{ pattern: AnyRegex, message: MSG_REFER_TO_TOOLTIP2 }}
              />
              <TableComponent.select
                target={'def_type'}
                record={record}
                options={typeOptions}
                type={DEFINE_CUSTOM_TYPE}
                onChange={onChangeText}
                regEx={{ pattern: AnyRegex, message: MSG_SELECT_COMBOBOX }}
                disabled={!!record?.skip}
              />
            </div>
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
              type={DEFINE_CUSTOM_TYPE}
              disabled={!!record?.skip}
            />
          )}
        />
        <Column
          title={MSG_TABLE_TITLE_SKIP}
          dataIndex="skip"
          key="skip"
          render={(_, record) => (
            <TableComponent.checkbox
              record={record}
              target={'skip'}
              checkHandler={checkHandler}
              type={DEFINE_CUSTOM_TYPE}
            />
          )}
        />
      </Table>
    </div>
  );
};
CustomConvertTable.propTypes = {
  dataSource: PropTypes.array,
  deleteHandler: PropTypes.func,
  checkHandler: PropTypes.func,
  dataOptions: PropTypes.array,
  typeOptions: PropTypes.array,
  onChangeText: PropTypes.func,
  columnOptions: PropTypes.array,
  isEdit: PropTypes.bool,
};
const custom_Basic = [
  'name',
  'output_column',
  'output_column_val',
  //  'data_type',
  //  'def_val',
  //  'def_type',
].reduce(
  (obj, cur) => {
    return { ...obj, [cur]: '' };
    //}, {});    ymkwon 임시 작업 ==== data type /default value를 임시로 넣어 두기
  },
  { def_val: 'null', def_type: 'null', data_type: 'text', skip: false },
);
const info_Basic = [
  'name',
  'output_column',
  'output_column_val',
  // 'data_type',
  // 'def_val',
  // 'def_type',
  'row_index',
].reduce(
  (obj, cur) => {
    return { ...obj, [cur]: '' };
    //}, {});    ymkwon 임시 작업 ==== data type /default value를 임시로 넣어 두기
  },
  { def_val: 'null', def_type: 'null', data_type: 'text', skip: false },
);

const headerBasic = [
  'name',
  'output_column',
  'output_column_val',
  // 'data_type',
  'coef',
  // 'def_val',
  // 'def_type',
  'unit',
].reduce(
  (obj, cur) => {
    return { ...obj, [cur]: '' };
    //}, {});  ymkwon 임시 작업 ==== data type /default value를 임시로 넣어 두기
  },
  { def_val: 'null', def_type: 'null', data_type: 'text', skip: false },
);
const basicColumn = (type) =>
  type === DEFINE_HEADER_TYPE
    ? headerBasic
    : type === DEFINE_INFO_TYPE
    ? info_Basic
    : custom_Basic;

const ConvertSetting = ({ data, onChange }) => {
  const {
    ruleStepConfig,
    updateConvertInfo,
    convertStepInfo,
  } = useRuleSettingInfo();
  const [config, setConfig] = useState(null);
  const { log_header, log_data } = data;
  const [form] = Form.useForm();
  const [selectRows, setSelectRows] = useState(undefined);
  const [ruleBase, setRuleBase] = useState({});
  const [columnOptions, setColumnOptions] = useState({
    info: [],
    header: [],
    custom: [],
  });

  const setDeboundcedText = useDebouncedCallback(
    ({ target, record, value, type }) =>
      onInputChange({ target, record, value, type }),
    100,
  );

  const onChangeText = ({ record, target, value, type }) => {
    setDeboundcedText({ record, target, value, type });
  };
  const handleCheck = (record, type) => {
    let tmpDataSource = [];
    if (record.key !== selectRows[type]) {
      let fIdx = 0;
      tmpDataSource = Object.values(record)
        .map((item, idx) => {
          fIdx = type === DEFINE_INFO_TYPE && item === null ? fIdx : idx;
          return type === DEFINE_HEADER_TYPE
            ? { ['key']: idx, ...basicColumn(type) }
            : {
                ...basicColumn(type),
                ['row_index']: parseInt(record.key) + 1,
                ['key']: idx,
              };
        })
        .filter((item, idx) => idx > 0 && fIdx >= idx);
      setSelectRows((prev) => ({ ...prev, [type]: record.key }));
    } else {
      setSelectRows((prev) => ({ ...prev, [type]: '' }));
    }
    updateConvertInfo({
      ...convertStepInfo,
      [type]: tmpDataSource,
      selectRows: {
        ...convertStepInfo.selectRows,
        [type]: record.key !== selectRows[type] ? record.key : '',
      },
    });
  };
  const CheckHandler = (key, target, value, type) => {
    const modified = convertStepInfo[type].map((item) =>
      item.key === key ? { ...item, [target]: value } : item,
    );
    updateConvertInfo({
      ...convertStepInfo,
      [type]: modified,
    });
  };

  const handleDelete = (key, type) => {
    const modified = convertStepInfo[type].filter((item) => item.key !== key);
    updateConvertInfo({
      ...convertStepInfo,
      [type]: modified,
    });
  };
  const handleAdd = (type) => {
    const newData = { ['key']: '', ...basicColumn(type) };
    const keyList = convertStepInfo[type]?.map((obj) => obj.key);
    const maxKeyValue =
      keyList.length === 0
        ? 0
        : Math.max(...convertStepInfo[type]?.map((obj) => obj.key));
    newData.key = maxKeyValue + 1;
    //ymkwon 임시 작업 ==== data type /default value를 임시로 넣어 두기
    newData.data_type = 'text';
    newData.def_val = newData.def_type = 'null';
    //=============================================================
    updateConvertInfo({
      ...convertStepInfo,
      [type]: [...convertStepInfo[type], newData],
    });
  };
  const checkBox = (record, type) => {
    return (
      <Checkbox
        checked={selectRows[type] === record.key}
        onChange={() => handleCheck(record, type)}
        style={{ width: 30, margin: '0 8px' }}
      />
    );
  };
  const onInputChange = ({ target, record, value, type }) => {
    const clone = { ...convertStepInfo };
    const updateColumn =
      target === 'output_column_val'
        ? config.columns?.find((obj) => obj.column_name === value) ?? undefined
        : undefined;
    const modifiedDataSource =
      type === 'log_define'
        ? { ...clone[type], [target]: value }
        : clone[type].map((obj) =>
            obj.key === record.key
              ? target === 'def_type' &&
                value !== 'custom' &&
                value !== 'text' &&
                value !== 'lambda'
                ? { ...obj, ['def_val']: value, [target]: value }
                : target === 'output_column_val'
                ? {
                    ...obj,
                    ['rec_type']: updateColumn === undefined ? '' : 'DB',
                    [target]: value,
                    ['output_column']: value === 'custom' ? '' : value,
                    ['data_type']:
                      value === 'custom'
                        ? ''
                        : updateColumn?.data_type ?? record.data_type,
                  }
                : { ...obj, [target]: value }
              : obj,
          );
    updateConvertInfo({
      ...convertStepInfo,
      [type]: modifiedDataSource,
    });
    if (target === 'rule_selected') {
      const request = async (findObj) => {
        try {
          const { info, status } = await getRequest(
            `${URL_RESOURCE}/${log_name}/${findObj.id}`,
          );

          if (status.toString() === RESPONSE_OK) {
            updateConvertInfo({
              ...convertStepInfo,
              info:
                sortArrayOfObjects(info?.convert?.info ?? [], 'col_index').map(
                  (obj, index) => {
                    return { ...obj, key: index + 1 };
                  },
                ) ?? [],
              header:
                sortArrayOfObjects(
                  info?.convert?.header ?? [],
                  'col_index',
                ).map((obj, index) => {
                  return { ...obj, key: index + 1 };
                }) ?? [],
              custom:
                info?.convert?.custom?.map((obj, index) => {
                  return { ...obj, key: index + 1 };
                }) ?? [],
            });
            setConfig((prev) => ({
              ...prev,
              data_type: info.convert?.data_type ?? [],
              def_type: info.convert?.def_type ?? [],
              script: info.convert?.script ?? {
                file_name: null,
                use_script: false,
              },
              columns: info.convert?.columns ?? [],
            }));
            console.log(info);
          }
        } catch (e) {
          if (e.response) {
            const {
              data: { msg },
            } = e.response;
            console.log(e.response);
            NotificationBox('ERROR', msg, 4.5);
          }
        }
      };
      const { log_name } = convertStepInfo.log_define;
      if (log_name ?? false) {
        const findObj = convertStepInfo?.log_define?.rule_base?.find(
          (obj) => obj.rule_name === value,
        );
        if (findObj !== undefined) request(findObj).then((_) => _);
      }
      setRuleBase((prevState) => ({
        ...prevState,
        selected: value,
      }));
    }
  };
  const samplelogColumns = [
    {
      title: MSG_STEP3_INFO,
      dataIndex: 'info',
      key: 'info',
      // eslint-disable-next-line react/display-name
      render: (_, record) => checkBox(record, DEFINE_INFO_TYPE),
    },
    {
      title: MSG_STEP3_HEADERS,
      dataIndex: 'header',
      key: 'header',
      // eslint-disable-next-line react/display-name
      render: (_, record) => checkBox(record, DEFINE_HEADER_TYPE),
    },
  ];
  const ChangeEvent = (e) => {
    const item = getParseData(e);
    if (item.id === 'file_name') {
      const fileName = getFileName(item.value);
      updateConvertInfo({
        ...convertStepInfo,
        script: {
          file_name: fileName,
          use_script: item.value !== null,
        },
      });
      onChange({ step3_script: item.value });
    } else if (item.id === 'use_script') {
      updateConvertInfo({
        ...convertStepInfo,
        script: {
          ...convertStepInfo.script,
          use_script: item.value,
        },
      });
    }
  };
  useEffect(() => {
    console.log('[STEP3]data: ', data);
    const step3 = ruleStepConfig.find((item) => item.step === E_STEP_3);
    setConfig(step3.config.convert);
    setColumnOptions({
      info: [
        ...(step3.config?.convert?.info?.map((obj) => {
          return { column_name: obj.output_column, data_type: obj.data_type };
        }) ?? []),
        { column_name: 'custom', data_type: '' },
      ],
      header: [
        ...(step3.config?.convert?.header?.map((obj) => {
          return { column_name: obj.output_column, data_type: obj.data_type };
        }) ?? []),
        { column_name: 'custom', data_type: '' },
      ],
      custom: [
        ...(step3.config?.convert?.custom?.map((obj) => {
          return { column_name: obj.output_column, data_type: obj.data_type };
        }) ?? []),
        { column_name: 'custom', data_type: '' },
      ],
    });
    if (convertStepInfo?.selectRows ?? false) {
      setSelectRows(convertStepInfo.selectRows);
    } else {
      setSelectRows({ DEFINE_INFO_TYPE: '', DEFINE_HEADER_TYPE: '' });
    }
    setRuleBase({
      options:
        convertStepInfo?.log_define?.rule_base?.map((opt) => opt.rule_name) ??
        [],
      selected: convertStepInfo?.log_define?.rule_selected ?? '',
    });
    if (convertStepInfo?.script?.use_script === undefined)
      updateConvertInfo({
        ...convertStepInfo,
        script: step3.config?.convert?.script ?? {
          use_script: false,
          file_name: null,
        },
      });
  }, []);

  const moveHeaderRow = useCallback(
    (dragIndex, hoverIndex) => {
      const copy = { ...convertStepInfo };
      const dragRow = copy.header[dragIndex];
      updateConvertInfo(
        update(copy, {
          header: {
            $splice: [
              [dragIndex, 1],
              [hoverIndex, 0, dragRow],
            ],
          },
        }),
      );
    },
    [convertStepInfo],
  );
  const moveInfoRow = useCallback(
    (dragIndex, hoverIndex) => {
      const copy = { ...convertStepInfo };
      const dragRow = copy.info[dragIndex];
      updateConvertInfo(
        update(copy, {
          info: {
            $splice: [
              [dragIndex, 1],
              [hoverIndex, 0, dragRow],
            ],
          },
        }),
      );
    },
    [convertStepInfo],
  );
  const components = {
    body: {
      row: DraggableBodyRow,
    },
  };
  if (config === null) return <></>;
  return (
    <div css={{ maxWidth: '85%', minWidth: '75%' }}>
      <Collapse
        defaultActiveKey={
          convertStepInfo.mode !== 'empty' ? [1, 2, 3, 4] : [1, 2, 3]
        }
      >
        <Panel header={MSG_STEP3_LOG_DEFINE} key="1">
          <div css={formWrapper}>
            <div>
              <InputForm.input
                formLabel={'Log Name'}
                formName={'log_name'}
                disabled={(convertStepInfo?.mode ?? 'new') !== 'new'}
                changeFunc={(e) =>
                  onChangeText({
                    target: 'log_name',
                    type: 'log_define',
                    value: getParseData(e).value,
                  })
                }
                tooltip={MSG_COMMON_REGEXP}
                value={convertStepInfo.log_define?.log_name ?? ''}
                regExp={{ pattern: CommonRegex, message: MSG_REFER_TO_TOOLTIP }}
              />
            </div>
            <div>
              <InputForm.input
                formLabel={'Table Name'}
                formName={'table_name'}
                disabled={(convertStepInfo?.mode ?? 'new') !== 'new'}
                changeFunc={(e) =>
                  onChangeText({
                    target: 'table_name',
                    type: 'log_define',
                    value: getParseData(e).value,
                  })
                }
                tooltip={MSG_TABLE_NAME_REGEXP}
                value={convertStepInfo.log_define?.table_name ?? ''}
                regExp={{
                  pattern: TableNameRegex,
                  message: MSG_REFER_TO_TOOLTIP,
                }}
              />
            </div>
            {convertStepInfo.mode !== 'empty' ? (
              <>
                <div>
                  <InputForm.input
                    formLabel={'Rule Name'}
                    formName={'rule_name'}
                    changeFunc={(e) =>
                      onChangeText({
                        target: 'rule_name',
                        type: 'log_define',
                        value: getParseData(e).value,
                      })
                    }
                    tooltip={MSG_RULENAME_REGEXP}
                    value={convertStepInfo.log_define?.rule_name ?? ''}
                    regExp={{
                      pattern: RuleNameRegex,
                      message: MSG_REFER_TO_TOOLTIP,
                    }}
                  />
                </div>
                <div>
                  {convertStepInfo.mode === 'add' ? (
                    <InputForm.select
                      formLabel={'Rule Base'}
                      formName={'rule_base'}
                      options={ruleBase?.options ?? []}
                      required={false}
                      disabled={(convertStepInfo?.mode ?? 'new') === 'edit'}
                      changeFunc={(e) =>
                        onChangeText({
                          target: 'rule_selected',
                          type: 'log_define',
                          value: getParseData(e).value,
                        })
                      }
                      defaultV={ruleBase?.selected ?? ''}
                    />
                  ) : (
                    <></>
                  )}
                </div>
              </>
            ) : (
              <></>
            )}
          </div>
        </Panel>
        <Panel header={MSG_STEP3_SELECT} key="2">
          {log_header !== undefined ? (
            <div
              style={{
                fontWeight: '14px',
                margin: '10px',
                display: 'flex',
                justifyContent: 'space-around',
              }}
            >
              <Table
                bordered
                pagination={false}
                columns={
                  convertStepInfo.mode !== 'empty'
                    ? [...samplelogColumns, ...log_header]
                    : log_header
                }
                dataSource={log_data ?? []}
                size="small"
                rowKey="key"
                scroll={{ x: true }}
              />
            </div>
          ) : (
            <div />
          )}
        </Panel>
        {convertStepInfo.mode !== 'empty' ? (
          <Panel header={MSG_STEP3_DEFINE} key="3">
            <Form form={form} layout="vertical">
              <Form.Item label={MSG_STEP3_INFO}>
                <Button
                  onClick={() => handleAdd(DEFINE_INFO_TYPE)}
                  type="primary"
                  style={{
                    marginBottom: 16,
                  }}
                >
                  Add a row
                </Button>
                <div css={tableWrapper}>
                  <DndProvider backend={HTML5Backend}>
                    <InfoConvertTable
                      dataSource={convertStepInfo.info}
                      typeOptions={config?.def_type ?? []}
                      dataOptions={config?.data_type ?? []}
                      columnOptions={
                        columnOptions?.info.map((obj) => obj.column_name) ?? []
                      }
                      moveInfoRow={moveInfoRow}
                      components={components}
                      deleteHandler={handleDelete}
                      checkHandler={CheckHandler}
                      onChangeText={onChangeText}
                      isEdit={Boolean(convertStepInfo.mode === 'edit')}
                      log_data={log_data?.find(
                        (row) => row.key === selectRows[DEFINE_INFO_TYPE],
                      )}
                    />
                  </DndProvider>
                </div>
              </Form.Item>
              <Form.Item
                label={MSG_STEP3_HEADERS}
                required
                tooltip={MSG_REQUIRED_TOOLTIP}
              >
                <Button
                  onClick={() => handleAdd(DEFINE_HEADER_TYPE)}
                  type="primary"
                  style={{
                    marginBottom: 16,
                  }}
                >
                  Add a row
                </Button>
                <div css={tableWrapper}>
                  <DndProvider backend={HTML5Backend}>
                    <HeaderConvertTable
                      dataSource={convertStepInfo.header}
                      typeOptions={config?.def_type ?? []}
                      dataOptions={config?.data_type ?? []}
                      columnOptions={
                        columnOptions?.header.map((obj) => obj.column_name) ??
                        []
                      }
                      moveHeaderRow={moveHeaderRow}
                      components={components}
                      deleteHandler={handleDelete}
                      checkHandler={CheckHandler}
                      onChangeText={onChangeText}
                      log_data={log_data?.find(
                        (row) => row.key === selectRows[DEFINE_HEADER_TYPE],
                      )}
                      isEdit={Boolean(convertStepInfo.mode === 'edit')}
                    />
                  </DndProvider>
                </div>
              </Form.Item>
              <Form.Item label={MSG_STEP3_CUSTOM}>
                <Button
                  onClick={() => handleAdd(DEFINE_CUSTOM_TYPE)}
                  type="primary"
                  style={{
                    marginBottom: 16,
                  }}
                >
                  Add a row
                </Button>
                <div css={tableWrapper}>
                  <CustomConvertTable
                    dataSource={convertStepInfo.custom}
                    typeOptions={config?.def_type ?? []}
                    dataOptions={config?.data_type ?? []}
                    columnOptions={
                      columnOptions?.custom.map((obj) => obj.column_name) ?? []
                    }
                    checkHandler={CheckHandler}
                    deleteHandler={handleDelete}
                    onChangeText={onChangeText}
                    isEdit={Boolean(convertStepInfo.mode === 'edit')}
                  />
                </div>
              </Form.Item>
            </Form>
          </Panel>
        ) : (
          <></>
        )}
        <Panel
          header={MSG_STEP3_CONVERT_SCRIPT}
          key={convertStepInfo.mode !== 'empty' ? '4' : '3'}
        >
          <div css={step3_convert_script_style}>
            <div
              css={{
                display: 'flex',
                flexDirection: 'column',
                maxWidth: '270px',
              }}
            >
              <InputForm.file
                btnMsg={MSG_UPLOAD_SCRIPT}
                changeFunc={ChangeEvent}
                formLabel={'script File: '}
                formName={'file_name'}
                file={
                  convertStepInfo?.script?.file_name ??
                  config?.script?.file_name ??
                  false
                    ? [
                        {
                          uid: 1,
                          name:
                            convertStepInfo?.script?.file_name ??
                            config?.script?.file_name,
                          status: 'done',
                        },
                      ]
                    : []
                }
                layout={{
                  labelAlign: 'left',
                }}
              />
              <InputForm.switch
                formName={'use_script'}
                formLabel={'use Script'}
                changeFunc={ChangeEvent}
                value={convertStepInfo?.script?.use_script ?? false}
                disable={
                  convertStepInfo?.script?.file_name === null ??
                  config?.script?.file_name ??
                  true
                }
              />
              {convertStepInfo?.script?.use_script ? (
                <InputForm.text
                  value={
                    'Using script will ignore data filter define settings. '
                  }
                />
              ) : (
                ''
              )}
            </div>
          </div>
        </Panel>
      </Collapse>
    </div>
  );
};
ConvertSetting.propTypes = {
  data: PropTypes.object,
  onChange: PropTypes.func,
};
export default ConvertSetting;
