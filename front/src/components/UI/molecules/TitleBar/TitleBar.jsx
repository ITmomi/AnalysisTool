import React from 'react';
import PropTypes from 'prop-types';
import { css } from '@emotion/react';
import Divider from '../../atoms/Divider/Divider';
import { BulbTwoTone } from '@ant-design/icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTimes } from '@fortawesome/free-solid-svg-icons';
import { Form, Input, Popconfirm } from 'antd';
import { AllMax30Regex } from '../../../../lib/util/RegExp';

const TitleBar = ({
  icon,
  text,
  isEditMode,
  changeFunc,
  deleteFunc,
  style,
}) => {
  const [form] = Form.useForm();
  const onFormLayoutChange = (value) => {
    console.log('changeEvent:', value);
    changeFunc(value.Category);
  };

  const Title_Bar_Style = css`
    & .ant-form-item-has-error {
      & input.ant-input,
      & input.ant-input:hover,
      & input.ant-input:focus {
        border: 3px solid #ff4d4f !important;
        box-shadow: 2px 2px 6px #ff4d4f;
      }
    }
  `;
  return (
    <div css={Title_Bar_Style}>
      {isEditMode === true ? (
        <Form
          form={form}
          initialvalues={{ Category: text }}
          onValuesChange={onFormLayoutChange}
        >
          <Form.Item
            name={'Category'}
            validateTrigger={['onChange']}
            validateStatus={AllMax30Regex.test(text) ?? true ? '' : 'error'}
          >
            <div css={[wrapperStyle, style]}>
              <div css={iconTextStyle}>
                {icon}
                <Input value={text} placeholder="Category" bordered={false} />
                <Popconfirm
                  title="Are you sure you want to delete this category?"
                  onConfirm={deleteFunc}
                >
                  <button>
                    <FontAwesomeIcon icon={faTimes} size="sm" />
                  </button>
                </Popconfirm>
              </div>
              <Divider style={{ height: 0 }} />
            </div>
          </Form.Item>
        </Form>
      ) : (
        <div css={[wrapperStyle, style]}>
          <div css={iconTextStyle}>
            {icon}
            <label css={labelStyle}>{text}</label>
          </div>
          <Divider style={{ height: 0 }} />
        </div>
      )}
    </div>
  );
};

TitleBar.displayName = 'TitleBar';
TitleBar.propTypes = {
  changeFunc: PropTypes.func,
  deleteFunc: PropTypes.func,
  isEditMode: PropTypes.bool,
  icon: PropTypes.element,
  text: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  style: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
};
TitleBar.defaultProps = {
  icon: (
    <BulbTwoTone
      style={{ fontSize: '30px', display: 'flex', alignItems: 'center' }}
    />
  ),
  text: 'Title',
};

const wrapperStyle = css`
  font-family: Saira, 'Nurito Sans';
  display: flex;
  align-items: center;
  position: relative;
  margin: 1rem 0;
`;

const iconTextStyle = css`
  position: absolute;
  background: #f0f2f5;
  display: flex;
  align-items: center;
  & input[type='text'],
  & input[type='text']:hover,
  & input[type='text']:focus {
    border: 3px solid #1890ff !important;
    border-radius: 4px;
    font-size: 20px;
    font-weight: 600;
    color: #096dd9;
    box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.4);
    margin: 0 1rem;
  }
  & span:first-of-type > svg {
    filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.4));
  }
  & > button {
    display: flex;
    align-items: center;
    text-align: center;
    margin-right: 1rem;
    border: none;
    background: white;
    border-radius: 50%;
    height: 20px;
    width: 20px;
    color: #1890ff;
    transition: transform 0.1s ease;
    &:hover {
      cursor: pointer;
    }
    &:active {
      transform: scale(0.8);
    }
  }
`;

const labelStyle = css`
  padding: 0 3.5rem;
  color: #096dd9;
  font-size: 30px;
  font-weight: 600;
  text-shadow: 0 3px 2px rgba(0, 0, 0, 0.2);
`;

export default TitleBar;
