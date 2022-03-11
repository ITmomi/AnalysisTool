import React, { useState } from 'react';
import PropTypes from 'prop-types';
import Button from '../../atoms/Button';
import DataBaseInfo from './DataBaseInfo';
import {
  URL_SETTING_GET_LOCAL,
  URL_SETTING_GET_REMOTE,
} from '../../../../lib/api/Define/URL';
import { useMutation } from 'react-query';
import { QUERY_KEY } from '../../../../lib/api/Define/QueryKey';
import { Spin } from 'antd';
import { LOCAL_INFO } from '../../../../lib/api/Define/etc';
import { updateDBInfo } from '../../../../lib/api/axios/useMgmtRequest';
import { css } from '@emotion/react';

const DBSetting = ({ info, db_type }) => {
  const [edit, setEdit] = useState(false);
  const { mutate, isLoading } = useMutation(
    [QUERY_KEY.MGMT_DB_UPDATE],
    updateDBInfo,
    {
      onSuccess: () => {
        //update(items);
        setEdit(false);
      },
    },
  );

  const MgmtStyle = css`
    & button {
      position: relative;
      float: right;
      top: -54px;
    }
  `;

  const enableEdit = () => {
    setEdit(true);
  };
  return db_type === LOCAL_INFO ? (
    edit === false ? (
      <div css={MgmtStyle}>
        <Button onClick={enableEdit}>Edit</Button>
        <DataBaseInfo.view data={info.items} />
      </div>
    ) : (
      <Spin tip="Loading..." spinning={isLoading}>
        <DataBaseInfo.addEdit
          // title={info.title}
          data={info.items}
          applyFunc={(obj) =>
            mutate({
              items: obj,
              url:
                db_type === LOCAL_INFO
                  ? URL_SETTING_GET_LOCAL
                  : URL_SETTING_GET_REMOTE,
            })
          }
        />
      </Spin>
    )
  ) : (
    <DataBaseInfo.list
      // title={info.title}
      data={info.items}
      db_type={db_type}
      url={
        db_type === LOCAL_INFO ? URL_SETTING_GET_LOCAL : URL_SETTING_GET_REMOTE
      }
    />
  );
};

DBSetting.propTypes = {
  info: PropTypes.object,
  update: PropTypes.func,
  db_id: PropTypes.string,
  db_type: PropTypes.string,
};

export default DBSetting;
