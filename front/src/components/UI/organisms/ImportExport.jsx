import React, { useEffect, useState } from 'react';
import { FormCard } from '../../UI/atoms/Modal';

import Button from '../../UI/atoms/Button';
import { css } from '@emotion/react';
import {
  MSG_APPLY,
  MSG_DOWNLOAD,
  MSG_EXPORT,
  MSG_IMPORT,
  MSG_IMPORT_EXPORT,
} from '../../../lib/api/Define/Message';
import { Modal, TreeSelect, message } from 'antd';
import PropTypes from 'prop-types';
import useCommonJob from '../../../hooks/useBasicInfo';
import InputForm from '../atoms/Input/InputForm';
import { getFileName, getFileType, getParseData } from '../../../lib/util/Util';
import {
  getRequestJsonExport,
  postRequestFormData,
} from '../../../lib/api/axios/requests';
import {
  URL_EXPORT_FUNCTIONS,
  URL_IMPORT_FUNCTIONS,
} from '../../../lib/api/Define/URL';
import { RESPONSE_OK } from '../../../lib/api/Define/etc';
import { useQueryClient } from 'react-query';
import { QUERY_KEY } from '../../../lib/api/Define/QueryKey';
const { ALL } = TreeSelect;
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
const ModalContents = ({ closeFunc }) => {
  const [treeData, setTreeData] = useState([]);
  const [selectValue, setSelectValue] = useState([]);
  const [uFileInfo, setUploadFileInfo] = useState({
    form_data: null,
    file_name: undefined,
  });
  const queryClient = useQueryClient();
  const { MenuInfo } = useCommonJob();
  const TreeListUpdate = () => {
    setTreeData(
      MenuInfo.body
        ?.filter(
          (obj1) =>
            obj1?.func.length > 0 &&
            obj1.func.filter((o) => o.info.Source !== 'multi').length > 0,
        )
        .map((category) => {
          return {
            title: category.title,
            value: `category_${category.category_id}`,
            key: `category_${category.category_id}`,
            children: category.func
              ?.filter((o) => o.info.Source !== 'multi')
              .map((func) => {
                return {
                  title: func.title,
                  value: func.func_id,
                  key: func.func_id,
                };
              }),
          };
        }),
    );
  };
  const tProps = {
    treeData,
    value: selectValue,
    onChange: setSelectValue,
    treeCheckable: true,
    showCheckedStrategy: ALL,
    placeholder: 'Please select',
    style: {
      width: '100%',
    },
  };
  const onChangeFunc = (e) => {
    const item = getParseData(e);
    console.log('onChangeFunc', item);
    if (item.value != null) {
      setUploadFileInfo({
        form_data: item.value,
        file_name: item.value != null ? getFileName(item.value) : undefined,
      });
    }
  };
  const importFunc = () => {
    const key = 'updatable';
    const execute = async () => {
      try {
        const { status } = await postRequestFormData(
          URL_IMPORT_FUNCTIONS,
          uFileInfo.form_data,
        );
        if (status.toString() === RESPONSE_OK) {
          message.success({
            content: 'Import success',
            key,
            duration: 100,
            className: 'custom-class',
            style: { marginTop: '12%' },
          });
          closeFunc();
          queryClient.invalidateQueries([QUERY_KEY.MAIN_INIT]).then((_) => _);
        }
      } catch (e) {
        console.log('ERROR OCCUR: ', e);
      }
    };
    if (getFileType(uFileInfo?.form_data ?? null) !== 'application/json') {
      message
        .error({
          content: `${getFileName(uFileInfo?.form_data)} is not a json file`,
          className: 'custom-class',
          style: { marginTop: '12%' },
        })
        .then(
          console.log('File Type:', getFileType(uFileInfo?.form_data ?? null)),
        );
    } else {
      execute().then(
        message.loading({
          content: 'Import in progress..',
          key,
          className: 'custom-class',
          style: { marginTop: '12%' },
        }),
      );
    }
  };
  const exportFunc = () => {
    const key = 'updatable';
    const execute = async () => {
      try {
        const { status } = await getRequestJsonExport(
          URL_EXPORT_FUNCTIONS,
          selectValue.map((obj) => {
            return `func_id=${obj}`;
          }),
        );
        if (status.toString() === RESPONSE_OK) {
          message.success({
            content: 'Export success',
            key,
            duration: 100,
            className: 'custom-class',
            style: { marginTop: '12%' },
          });
        }
      } catch (e) {
        console.log('ERROR OCCUR: ', e);
      }
    };
    execute().then(
      message.loading({
        content: 'Export in progress..',
        key,
        className: 'custom-class',
        style: { marginTop: '12%' },
      }),
    );
  };
  const import_file_style = css`
    & .ant-upload-list-item-info {
      width: fit-content;
    }
    & span.ant-upload-list-item-name {
      max-width: 375px;
      flex: none;
      width: fit-content;
    }
  `;

  useEffect(() => {
    TreeListUpdate();
  }, []);
  return (
    <>
      <div css={ContentsStyle}>
        <div css={{ width: '450px' }}>
          <div css={{ paddingBottom: '10px' }}>
            <FormCard
              title={
                <div
                  style={{
                    fontSize: '16px',
                    display: 'flex',
                    justifyContent: 'space-between',
                  }}
                >
                  1. {MSG_EXPORT}
                  <Button
                    theme={'blue'}
                    style={{ marginLeft: '8px', fontWeight: 400 }}
                    disabled={selectValue.length === 0}
                    onClick={() => exportFunc()}
                  >
                    {MSG_DOWNLOAD}
                  </Button>
                </div>
              }
            >
              <TreeSelect {...tProps} />
            </FormCard>
          </div>
          <div css={import_file_style}>
            <FormCard
              title={
                <div
                  style={{
                    fontSize: '16px',
                    fontWeight: '600',
                    display: 'flex',
                    justifyContent: 'space-between',
                  }}
                >
                  2. {MSG_IMPORT}
                  <Button
                    theme={'blue'}
                    style={{ marginLeft: '8px', fontWeight: 400 }}
                    disabled={!!uFileInfo.file_name === false}
                    onClick={() => importFunc()}
                  >
                    {MSG_APPLY}
                  </Button>
                </div>
              }
            >
              <InputForm.file
                formName={'form_data'}
                file={
                  uFileInfo.file_name !== undefined
                    ? [
                        {
                          uid: 1,
                          name: uFileInfo.file_name,
                          status: 'done',
                        },
                      ]
                    : []
                }
                changeFunc={onChangeFunc}
              />
            </FormCard>
          </div>
        </div>
      </div>
    </>
  );
};
ModalContents.propTypes = {
  closeFunc: PropTypes.func,
};
/*****************************************************************************
 *              ExportModal
 *****************************************************************************/

const ImportExport = ({ isOpen, closeable }) => {
  return (
    <>
      <Modal
        title={MSG_IMPORT_EXPORT}
        width={'500px'}
        footer={null}
        centered
        maskClosable={false}
        visible={isOpen}
        onCancel={() => closeable(false)}
      >
        <ModalContents closeFunc={() => closeable(false)} />
      </Modal>
    </>
  );
};
ImportExport.propTypes = {
  isOpen: PropTypes.bool,
  closeable: PropTypes.func,
};

export default ImportExport;
