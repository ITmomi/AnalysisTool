import { Cascader, Checkbox, Form, Input, InputNumber, Select } from 'antd';
import { MSG_CONFIRM_DELETE } from '../../../lib/api/Define/Message';
import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { getParseData } from '../../../lib/util/Util';
import DeleteButton from '../../UI/molecules/PopConfirmButton/DeleteButton';
const { Option } = Select;

const CheckBoxComponent = ({
  record,
  target,
  checkHandler,
  disabled,
  type,
}) => {
  return (
    <>
      {' '}
      <Checkbox
        /*key,target, value ,type*/
        onChange={(e) =>
          checkHandler(record.key, target, e.target.checked, type)
        }
        checked={record?.[target] ?? false}
        disabled={disabled ?? false}
      />
    </>
  );
};
CheckBoxComponent.propTypes = {
  checkHandler: PropTypes.func,
  record: PropTypes.object,
  target: PropTypes.string,
  type: PropTypes.string,
  disabled: PropTypes.bool,
};

const DeleteComponent = ({ record, type, deleteHandler, disabled }) => {
  return (
    <>
      {' '}
      <DeleteButton
        deleteHandler={() => deleteHandler(record.key, type)}
        disabled={disabled ?? false}
        title={MSG_CONFIRM_DELETE}
      />
    </>
  );
};
DeleteComponent.propTypes = {
  deleteHandler: PropTypes.func,
  record: PropTypes.object,
  type: PropTypes.string,
  disabled: PropTypes.bool,
};

const InputComponent = ({
  record,
  target,
  type,
  onChange,
  onClick,
  disabled,
  size,
  regEx,
}) => {
  const [form] = Form.useForm();
  const [text, setText] = useState(null);

  const onclick = () => {
    if (onClick !== undefined) {
      onClick({ record, target, type });
    }
  };
  const onFormLayoutChange = (e) => {
    const event = getParseData(e);
    onChange({ record, target, type, value: event.value });
  };

  useEffect(() => {
    setText(record[target]);
    form.setFieldsValue({ [target]: record[target] });
  }, [record[target]]);
  return (
    <Form
      form={form}
      initialvalues={{ [target]: record[target] }}
      onValuesChange={onFormLayoutChange}
      layout="inline"
    >
      <Form.Item
        name={target}
        validateTrigger={['onChange']}
        validateStatus={
          regEx?.pattern.test(text) ?? true
            ? ''
            : text ?? false
            ? 'error'
            : 'warning'
        }
        style={{
          width: (size ?? 'small') === 'small' ? 120 : 200,
          marginRight: '0',
        }}
      >
        <Input disabled={disabled ?? false} onClick={onclick} />
      </Form.Item>
    </Form>
  );
};
InputComponent.propTypes = {
  onChange: PropTypes.func.isRequired,
  onClick: PropTypes.func,
  record: PropTypes.object.isRequired,
  target: PropTypes.string.isRequired,
  type: PropTypes.string,
  disabled: PropTypes.bool,
  size: PropTypes.string,
  regEx: PropTypes.object,
};

const InputNumberComponent = ({
  record,
  target,
  type,
  onChange,
  disabled,
  size,
  regEx,
}) => {
  const [form] = Form.useForm();

  const [sNumber, setNumber] = useState(0);
  const onNumberChange = (value) => {
    onChange({ record, target, type, value: value });
  };
  useEffect(() => {
    setNumber(record[target]);
    form.setFieldsValue({ [target]: record[target] });
  }, [record[target]]);
  return (
    <Form
      form={form}
      initialvalues={{ [target]: record[target] }}
      layout="inline"
    >
      <Form.Item
        validateTrigger={['onChange']}
        validateStatus={
          !disabled
            ? regEx?.pattern.test(sNumber) ?? true
              ? ''
              : sNumber ?? false
              ? 'error'
              : 'warning'
            : ''
        }
      >
        <InputNumber
          min={1}
          max={10000}
          value={sNumber}
          onChange={onNumberChange}
          bordered={true}
          required={!disabled ?? true}
          disabled={disabled ?? false}
          size={'small'}
          style={{
            width: (size ?? 'small') === 'small' ? 60 : 80,
          }}
        />
      </Form.Item>
    </Form>
  );
};
InputNumberComponent.propTypes = {
  onChange: PropTypes.func.isRequired,
  record: PropTypes.object.isRequired,
  target: PropTypes.string.isRequired,
  type: PropTypes.string,
  disabled: PropTypes.bool,
  size: PropTypes.string,
  regEx: PropTypes.object,
};

const SelectComponent = ({
  record,
  target,
  options,
  onChange,
  disabled,
  size,
  type,
  regEx,
}) => {
  const [selectV, setSelected] = useState(null);
  const [form] = Form.useForm();
  const onFormLayoutChange = (event) => {
    console.log('event', event);
    onChange({ record, target, value: event[target], type });
  };
  useEffect(() => {
    setSelected(record[target]);
    form.setFieldsValue({ [target]: record[target] });
  }, [record[target]]);
  return (
    <Form
      form={form}
      initialvalues={{ [target]: record[target] }}
      onValuesChange={onFormLayoutChange}
      layout="inline"
    >
      <Form.Item
        name={target}
        validateTrigger={['onChange']}
        validateStatus={
          regEx?.pattern.test(selectV) ?? true
            ? ''
            : selectV ?? false
            ? 'error'
            : 'warning'
        }
        style={{
          width: (size ?? 'small') === 'small' ? 120 : 200,
          marginRight: '0',
        }}
      >
        <Select disabled={disabled ?? false}>
          {options?.map((item, idx) => {
            return (
              <Option key={idx} value={item}>
                {item}
              </Option>
            );
          }) ?? <></>}
        </Select>
      </Form.Item>
    </Form>
  );
};

SelectComponent.propTypes = {
  onChange: PropTypes.func.isRequired,
  record: PropTypes.object.isRequired,
  options: PropTypes.array,
  target: PropTypes.string.isRequired,
  type: PropTypes.string,
  disabled: PropTypes.bool,
  size: PropTypes.string,
  regEx: PropTypes.object,
};

const CascaderComponent = ({
  record,
  target,
  options,
  onChange,
  disabled,
  size,
  type,
  multiple,
  selectV,
}) => {
  const [form] = Form.useForm();
  const onFormLayoutChange = (event) => {
    console.log('event', event);
    onChange({ record, target, value: event[target], type });
  };
  useEffect(() => {
    form.setFieldsValue({ [target]: selectV });
  }, [selectV]);
  return (
    <Form
      form={form}
      initialvalues={{ [target]: selectV }}
      onValuesChange={onFormLayoutChange}
      layout="inline"
    >
      <Form.Item
        name={target}
        style={{
          width: (size ?? 'small') === 'small' ? 120 : 200,
          marginRight: '0',
        }}
      >
        <Cascader
          disabled={disabled ?? false}
          options={options}
          value={selectV}
          multiple={multiple}
          maxTagCount="responsive"
        />
      </Form.Item>
    </Form>
  );
};

CascaderComponent.propTypes = {
  onChange: PropTypes.func.isRequired,
  record: PropTypes.object.isRequired,
  options: PropTypes.array,
  target: PropTypes.string.isRequired,
  type: PropTypes.string,
  disabled: PropTypes.bool,
  size: PropTypes.string,
  multiple: PropTypes.bool,
  selectV: PropTypes.oneOfType([PropTypes.string, PropTypes.array]),
};

const TableComponent = ({ children }) => {
  return <>{children}</>;
};

TableComponent.propTypes = {
  children: PropTypes.node,
};

TableComponent.cascade = CascaderComponent;
TableComponent.select = SelectComponent;
TableComponent.delete = DeleteComponent;
TableComponent.checkbox = CheckBoxComponent;
TableComponent.input = InputComponent;
TableComponent.inputNumber = InputNumberComponent;
export default TableComponent;
