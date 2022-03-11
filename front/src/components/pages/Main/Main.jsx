import useCommonJob from '../../../hooks/useBasicInfo';
import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { useHistory } from 'react-router';
import { arrayUnshift } from '../../../lib/util/Util';
import { css } from '@emotion/react';
import { EDIT, NEW, URL_RESOURCE_FUNC } from '../../../lib/api/Define/URL';
import { message, Modal, Popconfirm, Spin } from 'antd';
import {
  MSG_BUTTON_MSG,
  MSG_CANCEL,
  MSG_CONFIRM_CANCEL,
  MSG_CONFIRM_DELETE,
  MSG_LOCAL,
  MSG_MULTI,
  MSG_REMOTE,
  MSG_SAVE_SETTING,
} from '../../../lib/api/Define/Message';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTrashAlt } from '@fortawesome/free-solid-svg-icons';
import {
  deleteRequest,
  updateCategoryList,
} from '../../../lib/api/axios/requests';
import {
  E_MULTI_TYPE,
  E_SINGLE_TYPE,
  RESPONSE_OK,
} from '../../../lib/api/Define/etc';
import { NotificationBox } from '../../UI/molecules/NotificationBox';
import ImportExport from '../../UI/organisms/ImportExport';
import Button from '../../UI/atoms/Button';
import TitleBar from '../../UI/molecules/TitleBar';
import MainPageItem from '../../UI/molecules/MainPageItem';
import Divider from '../../UI/atoms/Divider';
import { PlusCircleOutlined, BarChartOutlined } from '@ant-design/icons';
import { QUERY_KEY } from '../../../lib/api/Define/QueryKey';
import { useQueryClient } from 'react-query';
import { fixedTopMenu } from '../../../lib/api/Define/FixedMenu';
import { Category } from '../../UI/organisms/Category';
import PushpinOutlined from '@ant-design/icons/lib/icons/PushpinOutlined';
import GraphTwin from './GraphTwin';
import { AllMax30Regex } from '../../../lib/util/RegExp';

const MenuBarWrapper = css`
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
`;
const MenuButton = css`
  font-weight: 400;
  margin-left: 8px;
`;

const itemWrapper = css`
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  grid-template-rows: auto;
  gap: 2rem;
  justify-items: center;
  margin: 2rem 0;
`;
const deleteModalWrapper = css`
  height: 50px;
  display: flex;
  justify-content: center;
  padding: 15px;
`;
const itemiconStyle = css`
  position: absolute;
  top: 15px;
  left: 25px;
  & > span {
    color: black;
  }
  & > img {
    height: 32px;
  }
`;

const MainPage = () => {
  const {
    currentPath,
    setCurrentPath,
    MenuInfo,
    isEdit,
    setEditPage,
    categories,
  } = useCommonJob();
  const { body } = MenuInfo;
  const [category, updateCategory] = useState([]);
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [visible, setVisible] = useState(false);
  const history = useHistory();
  const queryClient = useQueryClient();
  const jobSelect = (id) => {
    setCurrentPath(arrayUnshift(currentPath, id));
  };

  useEffect(() => {
    if (body !== undefined) {
      updateCategory(categories);
      console.log('[init - updateCategory]:', categories);
    }
  }, []);
  const addCategory = () => {
    updateCategory((category) => [
      ...category,
      {
        idx: Math.max(...category.map((obj) => obj.idx)) + 1,
        id: null,
        value: '',
      },
    ]);
  };

  const deleteCategory = (d_Category) => {
    updateCategory(
      category
        .filter((v) =>
          d_Category.id === null
            ? v.idx !== d_Category.idx
            : v.id !== d_Category.id,
        )
        .map((obj, index) => {
          return { ...obj, idx: index };
        }),
    );
  };

  const changeCategory = (u_Category, value) => {
    console.log('[changeCategory]:', value);
    console.log('[changeCategory]:', u_Category);
    if (value !== undefined) {
      const tempCategory = category.map((item) => {
        return (
          u_Category.id === null
            ? item.idx === u_Category.idx
            : item.id === u_Category.id
        )
          ? { ...item, value: value }
          : item;
      });
      updateCategory(tempCategory);
      console.log('[updateCategory]:', tempCategory);
    }
  };

  const ClickEventByItem = ({ mode, type, id }) => {
    switch (mode.key) {
      case E_SINGLE_TYPE:
        history.push({ pathname: `${NEW}/${E_SINGLE_TYPE}/${id}` });
        break;
      case E_MULTI_TYPE:
        history.push({ pathname: `${NEW}/${E_MULTI_TYPE}/${id}` });
        break;
      case 'EDIT':
        history.push({ pathname: `${EDIT}/${type}/${id}` });
        break;
      case 'DELETE':
        Modal.confirm({
          title: MSG_CONFIRM_DELETE,
          content: (
            <div css={deleteModalWrapper}>
              <FontAwesomeIcon icon={faTrashAlt} size="2x" />
            </div>
          ),
          okButtonProps: { loading: confirmLoading },
          onOk() {
            const deleteItem = async (item) => {
              const { status, info } = await deleteRequest(
                URL_RESOURCE_FUNC,
                item,
              );
              if (status.toString() === RESPONSE_OK) {
                setConfirmLoading(false);
                queryClient
                  .invalidateQueries([QUERY_KEY.MAIN_INIT])
                  .then((_) => _);
              } else {
                message.error(info);
              }
            };
            deleteItem(id).then((_) => _);
          },
        });
        break;
      default:
        break;
    }
  };
  const saveSetting = () => {
    let isError = false,
      i = 0;

    while (i < category.length) {
      if (!AllMax30Regex.test(category[i].value)) {
        isError = true;
        break;
      }
      i++;
    }

    if (isError) {
      NotificationBox(
        'Save failed',
        'Category name is not valid. Please check the category name.',
      );
      return;
    }

    const reqInfos = async (categories) => {
      try {
        const { menu, status } = await updateCategoryList(categories);
        console.log('[saveSetting]:', menu);
        if (status === 'OK') {
          queryClient.invalidateQueries([QUERY_KEY.MAIN_INIT]).then((_) => _);
          setEditPage(false);
        }
      } catch (e) {
        if (e.response) {
          const { data } = e.response;
          NotificationBox(data.status, data.msg);
        }
      }
      setConfirmLoading(false);
    };
    if (isEdit === true) {
      const afterCategory = category.filter((item) => item.value !== '');
      if (JSON.stringify(categories) !== JSON.stringify(afterCategory)) {
        let list = [];
        setConfirmLoading(true);
        afterCategory.map((item) =>
          list.push({ category_id: item.id, title: item.value }),
        );
        reqInfos({ ['category']: list }).then();
      } else {
        setEditPage(false);
      }
    }
  };
  console.log('category', category);
  return (
    <>
      <Spin spinning={confirmLoading} tip="Applying...">
        <div css={MenuBarWrapper}>
          {isEdit === false ? (
            <>
              <ImportExport isOpen={visible} closeable={setVisible} />
              <Button
                theme={'white'}
                style={MenuButton}
                onClick={() => setVisible(true)}
              >
                {'Import/export'}
              </Button>
              <Button
                theme={'blue'}
                style={MenuButton}
                onClick={() => setEditPage(true)}
              >
                {'Add/Edit'}
              </Button>
            </>
          ) : (
            <>
              <Popconfirm
                title={MSG_CONFIRM_CANCEL}
                onConfirm={() => {
                  if (JSON.stringify(categories) !== JSON.stringify(category)) {
                    updateCategory(categories);
                  }
                  setEditPage(false);
                }}
              >
                <Button theme={'white'} style={MenuButton}>
                  {MSG_CANCEL}
                </Button>
              </Popconfirm>
              <Button theme={'blue'} style={MenuButton} onClick={saveSetting}>
                {MSG_SAVE_SETTING}
              </Button>
            </>
          )}
        </div>
        <div>
          {fixedTopMenu.map((obj) => {
            return (
              <>
                <Category
                  list={obj}
                  isEdit={false}
                  icon={
                    <PushpinOutlined
                      style={{
                        fontSize: '30px',
                        display: 'flex',
                        alignItems: 'center',
                      }}
                    />
                  }
                  isFixed={true}
                  itemClickHandler={(e) => history.push({ pathname: e })}
                />
              </>
            );
          })}
          {category.map((item, i) => {
            const menu = body.find((obj) => obj.category_id === item.id);
            return menu !== undefined ? (
              <div className="category-wrapper" key={`category_${i}`}>
                <div>
                  <TitleBar
                    text={item.value}
                    isEditMode={isEdit}
                    changeFunc={(value) => changeCategory(item, value)}
                    deleteFunc={() => deleteCategory(item ?? undefined)}
                  />
                  {isEdit === true ? (
                    <div css={itemWrapper}>
                      {menu.func.map((submenu, idx) => {
                        const tableStr =
                          submenu.info?.Source === MSG_LOCAL
                            ? `LogName: ${submenu.info?.['Log Name']}`
                            : submenu.info?.Source === MSG_REMOTE
                            ? `Table: ${submenu.info?.['Table']}`
                            : '';
                        return (
                          <MainPageItem
                            isEditMode={true}
                            key={`func_${idx}`}
                            mainText={submenu.title}
                            subText={
                              <div
                                title={`Source: ${submenu.info?.Source}\n${tableStr}`}
                              >
                                <div
                                  css={{
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis',
                                    fontSize: '18px',
                                    cursor: 'default',
                                  }}
                                >
                                  Source: {submenu.info?.Source}
                                </div>
                                <RenderItemIcon source={submenu.info?.Source} />
                                <div
                                  css={{
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis',
                                    fontSize: '16px',
                                    cursor: 'default',
                                  }}
                                >
                                  {tableStr === '' ? '\u00A0' : tableStr}
                                </div>
                              </div>
                            }
                            buttonText={MSG_BUTTON_MSG}
                            onClick={(e) =>
                              ClickEventByItem({
                                mode: e,
                                type:
                                  (submenu.info?.Source ?? MSG_LOCAL) ===
                                  MSG_MULTI
                                    ? E_MULTI_TYPE
                                    : E_SINGLE_TYPE,
                                id: submenu.func_id,
                              })
                            }
                          />
                        );
                      })}
                      <MainPageItem
                        isEditMode={true}
                        key={`func_new`}
                        mainText={null}
                        onClick={(e) =>
                          ClickEventByItem({
                            mode: e,
                            type: undefined,
                            id: menu.category_id,
                          })
                        }
                      />
                    </div>
                  ) : (
                    <div css={itemWrapper}>
                      {menu.func.map((submenu, idx) => {
                        const tableStr =
                          submenu.info?.Source === MSG_LOCAL
                            ? `LogName: ${submenu.info?.['Log Name']}`
                            : submenu.info?.Source === MSG_REMOTE
                            ? `Table: ${submenu.info?.['Table']}`
                            : '';
                        return (
                          <MainPageItem
                            isEditMode={false}
                            key={idx}
                            mainText={submenu.title}
                            subText={
                              <div
                                title={`Source: ${submenu.info?.Source}\n${tableStr}`}
                              >
                                <div
                                  css={{
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis',
                                    fontSize: '18px',
                                    cursor: 'default',
                                  }}
                                >
                                  Source: {submenu.info?.Source}
                                </div>
                                <RenderItemIcon source={submenu.info?.Source} />
                                <div
                                  css={{
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis',
                                    fontSize: '16px',
                                    cursor: 'default',
                                  }}
                                >
                                  {tableStr === '' ? '\u00A0' : tableStr}
                                </div>
                              </div>
                            }
                            buttonText={MSG_BUTTON_MSG}
                            onClick={() => jobSelect(submenu.func_id)}
                          />
                        );
                      })}
                    </div>
                  )}
                </div>
                <Divider />
              </div>
            ) : (
              <div key={`category_${i}`}>
                <TitleBar
                  style={{ marginTop: '3rem', marginBottom: '2rem' }}
                  text={item.value}
                  isEditMode={isEdit}
                  changeFunc={(value) => changeCategory(item, value)}
                  deleteFunc={() => deleteCategory(item ?? undefined)}
                />
                <Divider />
              </div>
            );
          })}
          {isEdit === true ? (
            <Button
              iconOnly
              size="md"
              theme={'white'}
              onClick={addCategory}
              style={{ marginTop: '1rem' }}
            >
              <PlusCircleOutlined />
            </Button>
          ) : (
            <></>
          )}
        </div>
      </Spin>
    </>
  );
};

/*
#=========================================#
| Single & Multi icon 추가 Gray            |
#=========================================#
*/
const RenderItemIcon = ({ source }) => {
  return (
    <div>
      <div css={itemiconStyle}>
        {source === MSG_MULTI ? (
          <GraphTwin width="32" height="32" fill="black" />
        ) : (
          <BarChartOutlined />
        )}
      </div>
    </div>
  );
};
RenderItemIcon.propTypes = {
  source: PropTypes.string.isRequired,
};

export default MainPage;
