import { useCallback, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  getMgmtInfo,
  UpdateMgmtInfoReducer,
} from '../reducers/slices/BasicInfo';
export const dbSettingItems = {
  items: [
    { target: 'host', type: 'input', title: 'Host', content: '' },
    { target: 'port', type: 'input', title: 'Port', content: '' },
    {
      target: 'username',
      type: 'input',
      title: 'UserName',
      content: '',
    },
    {
      target: 'dbname',
      type: 'input',
      title: 'DBName',
      content: '',
    },
    {
      target: 'password',
      type: 'password',
      title: 'Password',
      content: '',
    },
  ],
};
const useMgmtInfo = () => {
  const [isUpdate, setUpdateFlag] = useState(false);
  const [DbList, setDbList] = useState([]);
  const dispatch = useDispatch();
  const ManagementInfo = useSelector(getMgmtInfo);

  const setMgmtInfo = useCallback(
    (value) => {
      dispatch(UpdateMgmtInfoReducer(value));
    },
    [dispatch],
  );

  const clearMgmtInfo = useCallback(() => {
    dispatch(UpdateMgmtInfoReducer([]));
  }, [dispatch]);

  const changeDBInfo = useCallback(() => {
    setUpdateFlag(true);
  }, [isUpdate]);

  const clearUpdateFlag = useCallback(() => {
    setUpdateFlag(false);
  }, []);

  return {
    setMgmtInfo,
    clearMgmtInfo,
    isUpdate,
    clearUpdateFlag,
    changeDBInfo,
    ManagementInfo,
    DbList,
    setDbList,
  };
};

export default useMgmtInfo;
