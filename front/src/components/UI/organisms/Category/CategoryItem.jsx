import React from 'react';
import PropTypes from 'prop-types';
import {
  MSG_BUTTON_MSG,
  MSG_LOCAL,
  MSG_REMOTE,
} from '../../../../lib/api/Define/Message';
import TitleBar from '../../molecules/TitleBar';
import MainPageItem from '../../molecules/MainPageItem';
import { css } from '@emotion/react';
import { Tooltip } from 'antd';

const itemWrapper = css`
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  grid-template-rows: auto;
  gap: 2rem;
  justify-items: center;
  margin: 2rem 0;
`;
const SubTextStyle = css`
  overflow: 'hidden';
  textoverflow: 'ellipsis';
  fontsize: '18px';
  cursor: 'default';
`;
const ItemSubText = (title, info) => {
  const SubTextMsg = `Source: ${info?.Source}\n${
    info?.Source === MSG_LOCAL
      ? `LogName: ${info?.['Log Name']}`
      : info?.Source === MSG_REMOTE
      ? `Table: ${info?.['Table']}`
      : ''
  }`;
  return (
    <Tooltip title={SubTextMsg}>
      <div css={SubTextStyle}>{SubTextMsg}</div>
    </Tooltip>
  );
};
const CategoryItem = ({ list, isFixed, isEdit, icon, itemClickHandler }) => {
  /*
  const changeCategory = (u_Category, value) => {
    console.log('[changeCategory]:', value);
    console.log('[changeCategory]:', u_Category);
  };

  const deleteCategory = (value) => {
    console.log('[deleteCategory]:', value);
  };
  */

  return (
    <div className="category-wrapper">
      <div>
        <TitleBar
          text={list.title}
          icon={isFixed ? icon : undefined}
          /* changeFunc={isEdit ? (e) => changeCategory(list, e) : undefined}
          deleteFunc={isEdit ? (e) => deleteCategory(list, e) : undefined} */
        />
        <div css={itemWrapper}>
          {list?.func.map((submenu, idx) => {
            return (
              <MainPageItem
                isEditMode={!isFixed ?? isEdit}
                key={`func_${idx}`}
                subText={
                  isFixed ? undefined : ItemSubText(submenu.title, submenu.info)
                }
                mainText={submenu.title}
                buttonText={MSG_BUTTON_MSG}
                onClick={() => itemClickHandler(submenu?.func_id ?? undefined)}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
};

CategoryItem.propTypes = {
  list: PropTypes.object,
  isFixed: PropTypes.bool,
  isEdit: PropTypes.bool,
  icon: PropTypes.node,
  itemClickHandler: PropTypes.func,
};

export default CategoryItem;
