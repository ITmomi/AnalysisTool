import React, { useEffect, useState } from 'react';
import dayjs from 'dayjs';
import {
  Form,
  Select,
  DatePicker,
  Upload,
  Button,
  Input,
  Checkbox,
  Switch,
} from 'antd';
import { getParseData } from '../../../../lib/util/Util';
import PropTypes from 'prop-types';
import {
  FolderOpenFilled,
  LockOutlined,
  InboxOutlined,
  UploadOutlined,
} from '@ant-design/icons';
import { InputFormDateRegex } from '../../../../lib/util/RegExp';
import { usePrevious } from '../../../pages/JobAnalysis/AnalysisGraph/functionGroup';

const { RangePicker } = DatePicker;
const { Option, OptGroup } = Select;
const { Dragger } = Upload;

const InputForm = ({ children }) => {
  return <div>{children}</div>;
};

const layout = {
  labelCol: { span: 8 },
  wrapperCol: { span: 16 },
};

const layout2 = {
  wrapperCol: { span: 16, offset: 8 },
};

const SelectForm = ({
  formName,
  formLabel,
  changeFunc,
  options,
  optionNode,
  defaultV,
  required,
  disabled,
}) => {
  const [form] = Form.useForm();
  const [select, setSelected] = useState(undefined);
  const onFormLayoutChange = (e) => {
    const event = getParseData(e);
    changeFunc !== undefined
      ? changeFunc({ [formName]: event.value ?? '' })
      : console.log(e);
  };
  useEffect(() => {
    if (defaultV !== undefined) {
      const selectV = options.find((item) => (item?.id ?? item) === defaultV);
      form.setFieldsValue({ [formName]: selectV?.name ?? selectV ?? '' });
      setSelected(selectV);
    }
  }, [defaultV, options]);

  return (
    <>
      <Form
        {...(formLabel.length ? layout : layout2)}
        form={form}
        onValuesChange={onFormLayoutChange}
        initialValues={{ [formName]: select?.id ?? select ?? defaultV ?? '' }}
      >
        <Form.Item
          name={formName}
          label={formLabel}
          rules={[
            {
              required: required ?? true,
              message: `${formLabel} is required`,
            },
          ]}
        >
          {optionNode ?? (
            <Select
              allowClear={required !== undefined ? !required : false}
              disabled={disabled ?? false}
            >
              {
                // eslint-disable-next-line react/jsx-key
                options.map((item, idx) => {
                  return (
                    <Option key={idx} value={item?.id ?? item}>
                      {item?.name ?? item}
                    </Option>
                  );
                })
              }
            </Select>
          )}
        </Form.Item>
      </Form>
    </>
  );
};

SelectForm.propTypes = {
  formName: PropTypes.string,
  formLabel: PropTypes.string,
  changeFunc: PropTypes.func,
  options: PropTypes.array.isRequired,
  defaultV: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  required: PropTypes.bool,
  disabled: PropTypes.bool,
  optionNode: PropTypes.node,
};

const SelectOptionForm = ({
  formName,
  formLabel,
  changeFunc,
  treeData,
  values,
  required,
}) => {
  const [form] = Form.useForm();
  const [selected, setSelected] = useState(undefined);
  const onFormLayoutChange = (e) => {
    setSelected(e);
    changeFunc !== undefined
      ? changeFunc(e ?? { [formName]: '' })
      : console.log(e);
  };
  useEffect(() => {
    setSelected(values);
  }, [values]);

  return (
    <>
      <Form
        {...(formLabel?.length ?? false ? layout : layout2)}
        form={form}
        initialValues={{ [formName]: selected ?? '' }}
      >
        <Form.Item
          name={formName}
          label={formLabel}
          rules={[
            {
              required: required ?? true,
              message: `${formLabel} is required`,
            },
          ]}
        >
          <Select onSelect={onFormLayoutChange}>
            {treeData.map((group, i) => {
              return (
                <>
                  <OptGroup label={group.title} key={`group_${i}`}>
                    {group?.children?.map((child, j) => (
                      <Option key={`child_${i}_${j}`} value={child.value}>
                        {child.title}
                      </Option>
                    )) ?? <></>}
                  </OptGroup>
                </>
              );
            })}
          </Select>
        </Form.Item>
      </Form>
    </>
  );
};

SelectOptionForm.propTypes = {
  formName: PropTypes.string,
  formLabel: PropTypes.string,
  changeFunc: PropTypes.func,
  treeData: PropTypes.array.isRequired,
  values: PropTypes.array,
  required: PropTypes.bool,
  disabled: PropTypes.bool,
  optionNode: PropTypes.node,
  multiple: PropTypes.bool,
};

const MultiSelectForm = ({
  formName,
  formLabel,
  changeFunc,
  options,
  subItem,
  defaultV,
  required,
  formStyle,
}) => {
  const [firstValue, setFirstValue] = useState(null);
  const [subOptions, setSubOptions] = useState(null);
  const [form] = Form.useForm();
  const enableSpan = formStyle === undefined ? layout : {};

  const onItemChange = (e) => {
    const event = getParseData(e);
    if (event.id === formName) {
      setFirstValue(event.value);
      form.setFieldsValue({ [subItem.target]: '' });
      if (changeFunc !== undefined)
        changeFunc({ [event.id]: event.value, [subItem.target]: '' });
    } else {
      changeFunc !== undefined ? changeFunc(e) : console.log(e);
    }
  };

  const getSubOptions = (select) => {
    const item =
      subItem.options !== null
        ? Array.isArray(subItem?.options)
          ? subItem.options.find((obj) => getParseData(obj).id === select)
          : subItem.options?.[select] ?? undefined
        : undefined;
    if (item !== undefined) {
      return Array.isArray(item) ? item : getParseData(item).value;
    }
    return null;
  };

  useEffect(() => {
    setSubOptions(getSubOptions(firstValue));
  }, [firstValue]);

  useEffect(() => {
    if (defaultV !== undefined) {
      form.setFieldsValue({ [formName]: defaultV });
      setSubOptions(getSubOptions(defaultV ? defaultV : options[0]));
      form.setFieldsValue({ [subItem.target]: subItem.selected });
    }
  }, [defaultV]);

  return (
    <>
      <Form
        {...enableSpan}
        layout={formStyle}
        form={form}
        initialvalues={{
          [formName]: defaultV,
          [subItem.target]: subItem.selected,
        }}
        onValuesChange={onItemChange}
      >
        <Form.Item
          name={formName}
          label={formLabel}
          rules={[
            {
              required: required !== undefined ? required : true,
              message: `${formLabel} is required`,
            },
          ]}
        >
          <Select allowClear={required !== undefined ? !required : false}>
            {
              // eslint-disable-next-line react/jsx-key
              (options ?? []).map((item, idx) => {
                return (
                  <Option key={idx} value={item}>
                    {item}
                  </Option>
                );
              })
            }
          </Select>
        </Form.Item>
        <Form.Item
          name={subItem.target}
          label={subItem.title}
          rules={[
            {
              required: required !== undefined ? required : true,
              message: `${subItem.title} is required`,
            },
          ]}
        >
          <Select allowClear={required !== undefined ? !required : false}>
            {subOptions &&
              // eslint-disable-next-line react/jsx-key
              subOptions.map((item, idx) => {
                return (
                  <Option key={idx} value={item}>
                    {item}
                  </Option>
                );
              })}
          </Select>
        </Form.Item>
      </Form>
    </>
  );
};

MultiSelectForm.propTypes = {
  formName: PropTypes.string,
  formLabel: PropTypes.string,
  changeFunc: PropTypes.func,
  options: PropTypes.array.isRequired,
  subItem: PropTypes.object.isRequired,
  required: PropTypes.bool,
  formStyle: PropTypes.string,
  defaultV: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
    PropTypes.object,
  ]),
};

const dateFormat = 'YYYY-MM-DD';

const DateSelectForm = ({
  formName,
  formLabel,
  changeFunc,
  start,
  end,
  period,
  disabled,
}) => {
  const [form] = Form.useForm();
  const onFormLayoutChange = (e) => {
    const event = getParseData(e);
    const start = dayjs(e[event.id][0]).format('YYYY-MM-DD');
    const end = dayjs(e[event.id][1]).format('YYYY-MM-DD');
    changeFunc !== undefined
      ? changeFunc({ [event.id]: { start: start, end: end } })
      : console.log(e);
  };
  useEffect(() => {
    const isValid = InputFormDateRegex.test(start);
    form.setFieldsValue({
      [formName]: [
        start === ''
          ? start
          : isValid
          ? dayjs(start, dateFormat)
          : dayjs().startOf('month'),
        end === ''
          ? end
          : isValid
          ? dayjs(end, dateFormat)
          : dayjs().endOf('month'),
      ],
    });
  }, [start, end]);

  const disabledDate = (current) => {
    // Can not select days before today and today
    const isValid =
      InputFormDateRegex.test(period?.start ?? start) &&
      InputFormDateRegex.test(period?.end ?? end);
    return !isValid
      ? false
      : current &&
          (dayjs(current).isBefore(dayjs(period?.start ?? start), 'd') ||
            dayjs(current).isAfter(dayjs(period?.end ?? end), 'd'));
  };

  return (
    <>
      <Form {...layout} form={form} onValuesChange={onFormLayoutChange}>
        <Form.Item
          name={formName}
          label={formLabel ? formLabel : ' '}
          rules={[
            {
              required: true,
              message: `${formLabel ?? formName} is required`,
            },
          ]}
        >
          <RangePicker
            disabledDate={disabledDate}
            format={dateFormat}
            value={[
              start === '' ? 0 : dayjs(start, dateFormat),
              end === '' ? 0 : dayjs(end, dateFormat),
            ]}
            disabled={disabled ? [1, 1] : [!start & true, !end & true]}
            inputReadOnly
            allowClear={false}
          />
        </Form.Item>
      </Form>
    </>
  );
};

DateSelectForm.propTypes = {
  formName: PropTypes.string,
  formLabel: PropTypes.string,
  start: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  end: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  changeFunc: PropTypes.func,
  disabled: PropTypes.bool,
  period: PropTypes.object,
};

const DirectoryForm = ({ formName, formLabel, changeFunc }) => {
  const [fileList, setFileList] = useState([]);
  const [tmpFileList, setTmpFileList] = useState([]);

  const onFormLayoutChange = (e) => {
    const event = getParseData(e);
    const formData = new FormData();
    fileList.map((obj) => {
      formData.append('files', obj);
    });

    changeFunc !== undefined
      ? changeFunc({ [event.id]: formData })
      : console.log('onFormLayoutChange2', e);
  };

  const BeforeProps = {
    name: 'files',
    multiple: true,
    action: '',
    fileList: fileList,
    beforeUpload: (file) => {
      setTmpFileList((prev) => [...prev, file]);
      console.log('beforeUpload', file);
      return false;
    },
    onRemove: (file) => {
      setFileList((fileList) => {
        const index = fileList.indexOf(file);
        const newFileList = fileList.slice();
        newFileList.splice(index, 1);
        return newFileList;
      });
    },
    onChange: (info) => {
      console.log('onChange', info.file);
      if (tmpFileList.length > 0) {
        setFileList(tmpFileList);
        setTmpFileList([]);
      }
    },
  };

  return (
    <>
      <Form {...layout} onValuesChange={onFormLayoutChange}>
        <Form.Item
          name={formName}
          label={formLabel}
          rules={[
            {
              required: true,
              message: `${formLabel ?? formName} is required`,
            },
          ]}
        >
          <Upload {...BeforeProps} directory>
            <Button icon={<FolderOpenFilled />}>Upload Directory</Button>
          </Upload>
        </Form.Item>
      </Form>
    </>
  );
};

DirectoryForm.propTypes = {
  formName: PropTypes.string,
  formLabel: PropTypes.string,
  changeFunc: PropTypes.func,
  defaultV: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
};
const FilesForm = ({
  formName,
  formLabel,
  changeFunc,
  enable,
  files,
  defaultFiles,
}) => {
  const [fileList, setFileList] = useState(files ?? defaultFiles ?? []);
  const previousFileList = usePrevious(fileList);

  const props = {
    name: 'files',
    action: '', //backend server
    fileList: files,
    multiple: true,
    disabled: !enable ?? false,
    onChange: (e) => {
      console.log('valid onChange', e);
      if (e.file.status !== 'removed') {
        const currentUid = e.file.uid;
        if (currentUid === e.fileList[e.fileList.length - 1].uid) {
          const filteringFileList =
            fileList.length === 0
              ? e.fileList
              : e.fileList.filter((v) =>
                  defaultFiles
                    ? defaultFiles.find((x) => x.uid === v.uid) === undefined
                    : true,
                );
          setFileList(filteringFileList.map((v) => v.originFileObj ?? v));
        }
      }
    },
    onRemove: (e) => {
      setFileList(fileList.filter((v) => v.uid !== e.uid));
    },
    beforeUpload: () => false,
  };

  useEffect(() => {
    console.log('[useEffect] fileList', fileList);
    if (previousFileList) {
      const formData = new FormData();
      fileList.forEach((obj) => {
        formData.append('files', obj);
      });
      changeFunc({ src_file: fileList.length === 0 ? null : formData });
    }
  }, [fileList]);

  return (
    <>
      <Form {...layout}>
        <Form.Item
          name={formName}
          label={formLabel}
          rules={[
            {
              required: true,
              message: `${formLabel ?? formName} is required`,
            },
          ]}
        >
          <Dragger
            {...props}
            style={
              !enable ?? false
                ? { opacity: '0.3', height: '100px', width: '300px' }
                : { height: '100px', width: '300px' }
            }
          >
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">
              Click or drag file to this area to upload
            </p>
          </Dragger>
        </Form.Item>
      </Form>
    </>
  );
};

FilesForm.propTypes = {
  formName: PropTypes.string,
  formLabel: PropTypes.string,
  changeFunc: PropTypes.func,
  enable: PropTypes.bool,
  files: PropTypes.array,
  defaultFiles: PropTypes.array,
};
const FileForm = ({
  formName,
  formLabel,
  file,
  changeFunc,
  btnMsg,
  layout,
}) => {
  const [uploadedFile, setUploadedFile] = useState([]);
  const ButtonMsg = btnMsg ?? 'Select File';

  const onFormLayoutChange = (e) => {
    const event = getParseData(e);
    const formData = new FormData();
    uploadedFile.map((obj) => formData.append('files', obj));
    changeFunc !== undefined
      ? changeFunc({ [event.id]: uploadedFile.length === 0 ? null : formData })
      : console.log('onFormLayoutChange2', e);
  };
  useEffect(() => {
    console.log('useEffect: ', formName, ' : ', file);
    setUploadedFile(file);
  }, []);

  const props = {
    name: 'files',
    action: '', //backend server
    fileList: uploadedFile,
    beforeUpload: (f) => {
      console.log('valid beforeUpload', f);
      setUploadedFile([f]);
      return false;
    },
    onRemove: () => {
      setUploadedFile([]);
    },
  };

  return (
    <>
      <Form {...layout} onValuesChange={onFormLayoutChange}>
        <Form.Item
          name={formName}
          label={formLabel}
          rules={[
            {
              required: true,
              message: `${formLabel ?? formName} is required`,
            },
          ]}
        >
          <Upload {...props}>
            <Button icon={<UploadOutlined />}>{ButtonMsg}</Button>
          </Upload>
        </Form.Item>
      </Form>
    </>
  );
};

FileForm.propTypes = {
  formName: PropTypes.string,
  formLabel: PropTypes.string,
  changeFunc: PropTypes.func,
  btnMsg: PropTypes.string,
  file: PropTypes.array,
  layout: PropTypes.object,
};

const InputTextForm = ({
  formName,
  formLabel,
  changeFunc,
  value,
  disabled,
  formStyle,
  maxLength,
  regExp,
  tooltip,
  checkFunc,
  required,
}) => {
  const [form] = Form.useForm();
  const onFormLayoutChange = (e) => {
    changeFunc !== undefined ? changeFunc(e) : console.log(e);
  };
  const enableSpan = formStyle === undefined ? layout : {};

  useEffect(() => {
    form.setFieldsValue({ [formName]: value });
  }, [value]);

  return (
    <>
      <Form
        {...enableSpan}
        layout={formStyle}
        form={form}
        onValuesChange={onFormLayoutChange}
      >
        <Form.Item
          name={formName}
          label={formLabel}
          tooltip={tooltip ?? undefined}
          initialvalues={{ [formName]: value }}
          rules={[
            {
              required: required ?? true,
              message: `${formLabel ?? formName} is required`,
            },
            regExp === undefined
              ? {}
              : {
                  pattern: regExp.pattern,
                  message: `${regExp.message}`,
                },
            checkFunc
              ? {
                  validator: (_, v) => checkFunc(v),
                }
              : {},
          ]}
        >
          <Input
            allowClear
            disabled={disabled ?? false}
            maxLength={maxLength}
          />
        </Form.Item>
      </Form>
    </>
  );
};

InputTextForm.propTypes = {
  formName: PropTypes.string,
  formLabel: PropTypes.string,
  changeFunc: PropTypes.func,
  value: PropTypes.string,
  disabled: PropTypes.bool,
  formStyle: PropTypes.string,
  maxLength: PropTypes.number,
  regExp: PropTypes.object,
  tooltip: PropTypes.string,
  checkFunc: PropTypes.func,
  required: PropTypes.bool,
};

const TextForm = ({ formName, formLabel, value }) => {
  const [form] = Form.useForm();

  return (
    <>
      <Form {...(formLabel?.length ?? false ? layout : layout2)} form={form}>
        <Form.Item
          name={formName}
          label={formLabel}
          rules={[
            {
              required: true,
              message: `${formLabel ?? formName} is required`,
            },
          ]}
        >
          {value}
        </Form.Item>
      </Form>
    </>
  );
};

TextForm.propTypes = {
  formName: PropTypes.string,
  formLabel: PropTypes.string,
  changeFunc: PropTypes.func,
  value: PropTypes.string,
};

const TextAreaForm = ({ formName, formLabel, changeFunc, value, disabled }) => {
  const [form] = Form.useForm();
  const [text, setText] = useState(null);

  useEffect(() => {
    setText(value);
    form.setFieldsValue({ [formName]: value });
  }, []);
  const onFormLayoutChange = (e) => {
    changeFunc !== undefined ? changeFunc(e) : console.log(e);
  };

  return (
    <>
      <Form
        {...(formLabel ? layout : { wrapperCol: { offset: 0.5 } })}
        onValuesChange={onFormLayoutChange}
        form={form}
      >
        <Form.Item
          name={formName}
          label={formLabel}
          rules={[
            {
              required: true,
              message: `${formLabel ?? formName} is required`,
            },
          ]}
        >
          <Input.TextArea value={text} disabled={disabled ?? false} />
        </Form.Item>
      </Form>
    </>
  );
};

TextAreaForm.propTypes = {
  formName: PropTypes.string,
  formLabel: PropTypes.string,
  changeFunc: PropTypes.func,
  value: PropTypes.string,
  disabled: PropTypes.bool,
};

const PasswordForm = ({ formName, formLabel, changeFunc, value }) => {
  const [form] = Form.useForm();

  const onFormLayoutChange = (e) => {
    changeFunc !== undefined ? changeFunc(e) : console.log(e);
  };

  useEffect(() => {
    form.setFieldsValue({ [formName]: value });
  }, [value]);

  return (
    <>
      <Form {...layout} form={form} onValuesChange={onFormLayoutChange}>
        <Form.Item
          name={formName}
          label={formLabel}
          rules={[
            {
              required: true,
              message: `${formLabel ?? formName} is required`,
            },
          ]}
        >
          <Input
            prefix={<LockOutlined className="site-form-item-icon" />}
            type="password"
            value={value}
            placeholder="Password"
            allowClear
          />
        </Form.Item>
      </Form>
    </>
  );
};

PasswordForm.propTypes = {
  formName: PropTypes.string,
  formLabel: PropTypes.string,
  changeFunc: PropTypes.func,
  value: PropTypes.string,
};

const CheckBoxForm = ({
  formName,
  formLabel,
  context,
  changeFunc,
  value,
  disabled,
}) => {
  const [form] = Form.useForm();

  const onFormLayoutChange = (e) => {
    changeFunc !== undefined ? changeFunc(e) : console.log(e);
  };

  useEffect(() => {
    form.setFieldsValue({ [formName]: value });
  }, [value]);

  return (
    <>
      <Form
        {...layout}
        form={form}
        initialValues={{ [formName]: value }}
        onValuesChange={onFormLayoutChange}
      >
        <Form.Item
          name={formName}
          label={formLabel}
          valuePropName="checked"
          wrapperCol={formLabel === undefined ? { offset: 8, span: 16 } : {}}
          rules={[
            {
              required: false,
            },
          ]}
        >
          <Checkbox disabled={disabled}>{context}</Checkbox>
        </Form.Item>
      </Form>
    </>
  );
};

CheckBoxForm.propTypes = {
  formName: PropTypes.string,
  formLabel: PropTypes.string,
  context: PropTypes.string,
  changeFunc: PropTypes.func,
  value: PropTypes.bool,
  disabled: PropTypes.bool,
};

const SwitchForm = ({
  formName,
  formLabel,
  changeFunc,
  value,
  disable,
  custom,
}) => {
  const [form] = Form.useForm();

  const onFormLayoutChange = (e) => {
    changeFunc !== undefined ? changeFunc(e) : console.log(e);
  };

  return (
    <>
      <Form {...layout} form={form} onValuesChange={onFormLayoutChange}>
        <Form.Item
          name={formName}
          label={formLabel}
          wrapperCol={formLabel === undefined ? { offset: 8, span: 16 } : {}}
          rules={[
            {
              required: true,
            },
          ]}
        >
          <Switch
            disabled={disable}
            checked={value}
            checkedChildren={custom?.checkedChildren ?? undefined}
            unCheckedChildren={custom?.unCheckedChildren ?? undefined}
          />
        </Form.Item>
      </Form>
    </>
  );
};

SwitchForm.propTypes = {
  formName: PropTypes.string,
  formLabel: PropTypes.string,
  changeFunc: PropTypes.func,
  value: PropTypes.bool,
  disable: PropTypes.bool,
  custom: PropTypes.object,
};

InputForm.propTypes = {
  children: PropTypes.node,
};

InputForm.select = SelectForm;
InputForm.subItem = MultiSelectForm;
InputForm.directory = DirectoryForm;
InputForm.datePicker = DateSelectForm;
InputForm.file = FileForm;
InputForm.files = FilesForm;
InputForm.input = InputTextForm;
InputForm.text = TextForm;
InputForm.password = PasswordForm;
InputForm.checkbox = CheckBoxForm;
InputForm.switch = SwitchForm;
InputForm.textarea = TextAreaForm;
InputForm.selectOption = SelectOptionForm;

export default InputForm;
