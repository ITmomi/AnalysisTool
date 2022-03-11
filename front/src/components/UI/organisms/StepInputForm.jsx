import InputForm from '../atoms/Input/InputForm';
import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import {
  MSG_ADD_NEW,
  MSG_DISABLE,
  MSG_UPLOAD_SCRIPT,
} from '../../../lib/api/Define/Message';
import { Button, Popconfirm, Select, Spin } from 'antd';
import { DeleteOutlined, LoadingOutlined } from '@ant-design/icons';
import useRuleSettingInfo from '../../../hooks/useRuleSettingInfo';
import { css } from '@emotion/react';
import dayjs from 'dayjs';
import { rand } from '../../../lib/util/Util';
const { Option } = Select;

const Contents = ({ options, target, defaultV, actionFunc }) => {
  const [loading, setLoading] = useState(false);
  const onClickEvent = (value, type) => {
    actionFunc({ [type]: value });
    if (type === 'DELETE') {
      setLoading(true);
    }
  };
  useEffect(() => {
    if (loading) setLoading(false);
  }, [options]);
  if (options.length === 0) return <></>;
  return (
    <>
      <Spin
        tip="Deleting..."
        indicator={<LoadingOutlined style={{ fontSize: 24 }} spin />}
        spinning={loading}
      >
        <Select
          value={defaultV ?? '0'}
          onChange={(e) => {
            onClickEvent(
              options.find(
                (obj) => (e === '0' && obj.id === null) || obj.id === e,
              ),
              target,
            );
          }}
        >
          {options.map((item, idx) => {
            return (
              <Option key={idx} value={item.id ?? '0'}>
                {
                  <>
                    {''}
                    {item.rule_name}
                    {item.rule_name === MSG_ADD_NEW ? (
                      <></>
                    ) : (
                      <Popconfirm
                        title={`Are you sure to delete Rule ${item.rule_name}`}
                        onConfirm={(e) => {
                          e.stopPropagation();
                          onClickEvent(item, 'DELETE');
                        }}
                      >
                        <Button
                          type="text"
                          icon={<DeleteOutlined />}
                          style={{ float: 'right' }}
                          onClick={(e) => e.stopPropagation()}
                        />
                      </Popconfirm>
                    )}
                  </>
                }
              </Option>
            );
          })}
        </Select>
      </Spin>
    </>
  );
};
Contents.propTypes = {
  options: PropTypes.array,
  defaultV: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  target: PropTypes.string,
  actionFunc: PropTypes.func,
};
export const StepInputForm = ({ item, data, changeFunc }) => {
  const { title, type, mode } = item;
  const [selectOptions, setSelectOptions] = useState([]);
  const { convertStepInfo, funcStepInfo } = useRuleSettingInfo();
  const changeEvent = (e) => {
    console.log('changeEvent:', e);
    changeFunc(e);
  };
  const period = { start: '', end: '' };
  const selected = { start: '', end: '' };
  if (type.toLowerCase() === 'datepicker') {
    selected.start =
      funcStepInfo?.info?.selected?.start ??
      data?.info?.selected?.start ??
      item.options?.selected?.start ??
      '';
    selected.end =
      funcStepInfo?.info?.selected?.end ??
      data?.info?.selected?.end ??
      item.options?.selected?.end ??
      '';
    period.start =
      funcStepInfo?.info?.period?.start ??
      data?.info?.period?.start ??
      item.options?.period.start ??
      '';
    period.end =
      funcStepInfo?.info?.period?.end ??
      data?.info?.period?.end ??
      item.options?.period.end ??
      '';
  }

  useEffect(() => {
    if (
      (convertStepInfo?.rule_list?.length ?? 0) !== (selectOptions?.length ?? 0)
    ) {
      setSelectOptions(convertStepInfo.rule_list);
    }
  }, [convertStepInfo.rule_list]);

  const contentsStyle = css`
    & .ant-form-item-label {
      text-align: left;
      flex-basis: 130px;
    }
    & .ant-form-item {
      margin-bottom: 10px;
    }
    & .ant-upload-list {
      max-height: 100px;
      overflow-y: auto;
    }

    & .ant-upload-list-item-info {
      width: fit-content;
      & span.ant-upload-list-item-name {
        flex: none;
        max-width: 266px;
        width: fit-content;
      }
    }
    & .ant-col.ant-col-16.ant-col-offset-8.ant-form-item-control {
      position: relative;
      left: -25px;
    }
    & .ant-picker-range-separator {
      position: relative;
      left: -19px;
    }
    & .ant-picker.ant-picker-disabled {
      width: 100%;
    }
    & .ant-picker.ant-picker-range {
      width: 100%;
    }
  `;
  return (
    <div css={contentsStyle}>
      {type === 'select' ? (
        mode === 'singular' ? (
          item.target === 'rule_name' ? (
            <InputForm.select
              formLabel={title}
              formName={item.target}
              options={selectOptions.length > 0 ? selectOptions : item.options}
              optionNode={
                <Contents
                  options={
                    selectOptions.length > 0 ? selectOptions : item.options
                  }
                  defaultV={
                    convertStepInfo?.log_define?.rule_id ??
                    item.selected ??
                    null
                  }
                  actionFunc={changeEvent}
                  target={item.target}
                />
              }
              changeFunc={changeEvent}
              defaultV={
                convertStepInfo?.log_define?.rule_id ?? item.selected ?? null
              }
            />
          ) : item.target === 'table_name' ? (
            <InputForm.select
              formLabel={title}
              formName={item.target}
              options={data?.[item.target] ?? []}
              changeFunc={changeEvent}
              defaultV={
                funcStepInfo?.info?.[item.target] ??
                data?.info?.[item.target] ??
                ''
              }
            />
          ) : item.target === 'source' ? (
            <InputForm.select
              formLabel={title}
              formName={item.target}
              options={item.options}
              changeFunc={changeEvent}
              defaultV={funcStepInfo?.source_type ?? item?.selected ?? ''}
            />
          ) : (
            <InputForm.select
              formLabel={title}
              formName={item.target}
              options={item.options}
              changeFunc={changeEvent}
              defaultV={
                funcStepInfo?.info?.[item.target] ??
                data?.info?.[item.target] ??
                data?.[item.target] ??
                item?.selected ??
                ''
              }
            />
          )
        ) : mode === 'subItem' ? (
          <>
            <InputForm.subItem
              formLabel={title}
              formName={item.target}
              options={data?.[item.target] ?? item.options}
              subItem={{
                ...item.subItem,
                options: data?.[item.subItem.target] ?? item.subItem.option,
                selected:
                  funcStepInfo?.info?.[item.subItem.target] ??
                  data?.info?.[item.subItem.target] ??
                  item?.subItem.selected ??
                  '',
              }}
              changeFunc={changeEvent}
              defaultV={
                funcStepInfo?.info?.[item.target] ??
                data?.info?.[item.target] ??
                item?.selected ??
                ''
              }
            />
          </>
        ) : (
          <></>
        )
      ) : type === 'file' ? (
        <InputForm.file
          formLabel={title}
          formName={item.target}
          file={
            funcStepInfo?.[item.target] ??
            funcStepInfo?.script?.[item.target] ??
            item?.file_name ??
            false
              ? [
                  {
                    uid: rand(1, 100),
                    name:
                      funcStepInfo?.[item.target] ??
                      funcStepInfo?.script?.[item.target] ??
                      item?.file_name,
                    status: 'done',
                  },
                ]
              : []
          }
          changeFunc={changeFunc}
          btnMsg={item.target === 'file_name' ? MSG_UPLOAD_SCRIPT : undefined}
        />
      ) : type === 'files' ? (
        <InputForm.files
          formLabel={title}
          formName={item.target}
          files={
            data?.file_name !== undefined
              ? data?.file_name?.getAll('files').map((o) => o) ?? undefined
              : item?.file_name?.length > 0 ?? false
              ? item.file_name.map((obj, i) => {
                  return {
                    uid: i + 1,
                    name: obj,
                    status: 'done',
                  };
                })
              : undefined
          }
          defaultFiles={
            item?.file_name?.length > 0 ?? false
              ? item.file_name.map((obj, i) => {
                  return {
                    uid: i + 1,
                    name: obj,
                    status: 'done',
                  };
                })
              : undefined
          }
          enable={item?.enable ?? true}
          changeFunc={changeFunc}
          btnMsg={item.target === 'file_name' ? MSG_UPLOAD_SCRIPT : undefined}
        />
      ) : type === 'checkbox' ? (
        <InputForm.checkbox
          formName={item.target}
          context={title}
          changeFunc={changeFunc}
          value={data?.[item.target] === true}
          disabled={data?.[item.target] === MSG_DISABLE}
        />
      ) : type === 'text' ? (
        <InputForm.text
          formLabel={title}
          formName={item.target}
          changeFunc={changeFunc}
          value={item.content}
        />
      ) : type === 'input' ? (
        <InputForm.input
          formLabel={title}
          formName={item.target}
          disabled={item?.enable ?? false}
          changeFunc={changeFunc}
          value={data?.[item.target] ?? item.content}
        />
      ) : type.toLowerCase() === 'datepicker' ? (
        <InputForm.datePicker
          formLabel={title}
          formName={item.target}
          start={
            selected.start === ''
              ? selected.start
              : dayjs(selected.start).format('YYYY-MM-DD')
          }
          end={
            selected.end === ''
              ? selected.end
              : dayjs(selected.end).format('YYYY-MM-DD')
          }
          period={{
            start:
              period.start === ''
                ? period.start
                : dayjs(period.start).format('YYYY-MM-DD'),
            end:
              period.end === ''
                ? period.end
                : dayjs(period.end).format('YYYY-MM-DD'),
          }}
          changeFunc={changeEvent}
          disabled={item?.enable === false ?? false}
        />
      ) : type === 'switch' ? (
        <InputForm.switch
          formLabel={title}
          formName={item.target}
          changeFunc={changeEvent}
          value={funcStepInfo?.script?.use_script ?? false}
          disable={
            funcStepInfo?.script?.file_name === undefined ||
            funcStepInfo.script.file_name === null
          }
        />
      ) : type === 'textarea' ? (
        <InputForm.textarea
          formName={item.target}
          changeFunc={changeEvent}
          value={
            funcStepInfo?.info?.[item.target] ??
            data?.info?.[item.target] ??
            item?.content ??
            ''
          }
          disabled={(item?.enable ?? true) === false}
        />
      ) : (
        <div>{title}</div>
      )}
    </div>
  );
};

StepInputForm.propTypes = {
  data: PropTypes.object,
  item: PropTypes.object.isRequired,
  changeFunc: PropTypes.func.isRequired,
};
