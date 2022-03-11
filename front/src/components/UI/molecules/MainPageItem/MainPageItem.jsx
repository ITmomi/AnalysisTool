import React from 'react';
import PropTypes from 'prop-types';
import { css } from '@emotion/react';
import ItemCard from '../../atoms/ItemCard/ItemCard';
import Button from '../../atoms/Button/Button';
import { Button as Button2, Menu, Dropdown } from 'antd';
import GraphTwin from '../../../pages/Main/GraphTwin';

import {
  DeleteOutlined,
  EditOutlined,
  MoreOutlined,
  PlusCircleOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import { E_MULTI_TYPE, E_SINGLE_TYPE } from '../../../../lib/api/Define/etc';
//import styled from '@emotion/styled';

const MainPageItem = ({
  isEditMode,
  mainText,
  subText,
  buttonText,
  onClick,
}) => {
  const EditMenu = (
    <Menu onClick={onClick} css={editMenuStyle}>
      <Menu.Item key="EDIT" icon={<EditOutlined />}>
        EDIT
      </Menu.Item>
      <Menu.Item key="DELETE" icon={<DeleteOutlined />}>
        DELETE
      </Menu.Item>
    </Menu>
  );
  const NewMenu = (
    <Menu onClick={onClick} css={newMenuStyle}>
      <Menu.Item key={E_SINGLE_TYPE} icon={<BarChartOutlined />}>
        Single Analysis
      </Menu.Item>
      <Menu.Item key={E_MULTI_TYPE} icon={<GraphTwin />}>
        Multi Analysis
      </Menu.Item>
    </Menu>
  );

  return isEditMode === true ? (
    <div>
      <ItemCard
        style={
          mainText === null
            ? {
                justifyContent: 'center',
                boxShadow: 'none',
                background: 'transparent',
              }
            : {}
        }
      >
        {mainText !== null ? (
          <>
            <div css={contentStyle}>
              <Dropdown overlay={EditMenu}>
                <Button2
                  type="dashed"
                  css={Button2Style}
                  icon={<MoreOutlined />}
                />
              </Dropdown>
              <div css={mainTextStyle}>{mainText}</div>
              <div css={subTextStyle}>{subText}</div>
            </div>
            <Button width={'80%'} style={buttonTextStyle} disabled>
              {buttonText}
            </Button>
          </>
        ) : (
          <>
            <Dropdown overlay={NewMenu} placement="bottomCenter" arrow>
              <PlusCircleOutlined
                style={{ fontSize: '70px' }}
                css={newButtonStyle}
              />
            </Dropdown>
          </>
        )}
      </ItemCard>
    </div>
  ) : (
    <ItemCard>
      <div css={contentStyle}>
        <div css={mainTextStyle}>{mainText}</div>
        <div css={subTextStyle}>{subText}</div>
      </div>
      <Button width={'80%'} onClick={onClick} style={buttonTextStyle}>
        {buttonText}
      </Button>
    </ItemCard>
  );
};

MainPageItem.displayName = 'MainPageItem';
MainPageItem.propTypes = {
  isEditMode: PropTypes.bool,
  mainText: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  subText: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number,
    PropTypes.node,
  ]),
  buttonText: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onClick: PropTypes.func,
};
MainPageItem.defaultProps = {
  mainText: 'Main text',
  buttonText: 'Button',
};

const contentStyle = css`
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  flex-basis: 190px;
  flex-shrink: 0;
  width: 100%;
  padding: 0 25px;
  text-align: center;
  & > div {
    font-weight: 600;
    &:first-of-type {
      width: 85%;
      margin: 0 auto;
      word-break: break-word;
      cursor: default;
    }
  }
  & li {
    &:hover {
      background: #69c0ff;
      color: white;
    }
`;

const mainTextStyle = css`
  font-size: 18px;
  color: #002766;
`;

const subTextStyle = css`
  font-size: 18px;
  color: #1890ff;
`;

const buttonTextStyle = css`
  font-weight: 400;
`;

const Button2Style = css`
  position: absolute;
  right: 0.5rem;
  top: 0.5rem;
  border-radius: 1rem;
  border-color: #1890ff;
  color: #2f54eb;
`;

const newButtonStyle = css`
  & svg {
    &:hover {
      filter: drop-shadow(4px 4px 7px rgba(0, 0, 0, 0.4));
      color: #1890ff;
    }
  }
`;

const editMenuStyle = css`
  & li {
    &:hover {
      background: #69c0ff;
      color: white;
    }
  }
`;
const newMenuStyle = css`
  & li {
    &:hover {
      background: #69c0ff;
      color: white;
    }
    &:first-of-type {
      & > span:last-of-type {
        margin-left: 12px;
      }
    }
  }
`;

/*const Button3 = styled.button`
  position: relative;
  background: transparent;
  border: transparent;
  transition: box-shadow 0.1s ease, transform 0.1s ease;
  border-radius: 50%;
  padding: 1rem;
  &:hover {
    cursor: pointer;
    box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.4);
  }
  &:active {
    box-shadow: none;
    transform: translateY(2px);
  }
  & svg {
    filter: drop-shadow(2px 4px 4px rgba(0, 0, 0, 0.4));
  }
`;*/
export default MainPageItem;
