import { useCallback, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  getCurrentPath,
  getMenuInfo,
  getSupportUrl,
  getVersionInfo,
  getCategories,
  initialCommonAction,
  UpdateCurrentPathReducer,
  UpdateMenuInfoReducer,
  UpdateSupportJobUrlReducer,
  UpdateVersionInfoReducer,
  UpdateCategoriesReducer,
} from '../reducers/slices/BasicInfo';

const useCommonJob = () => {
  const dispatch = useDispatch();
  const [isEdit, setEdit] = useState(false);
  const [showMgmt, setMgmtshow] = useState(null);
  const currentPath = useSelector(getCurrentPath);
  const supportUrl = useSelector(getSupportUrl);
  const versionInfo = useSelector(getVersionInfo);
  const MenuInfo = useSelector(getMenuInfo);
  const categories = useSelector(getCategories);

  const setCurrentPath = useCallback(
    (value) => {
      dispatch(UpdateCurrentPathReducer(value));
    },
    [dispatch],
  );

  const setSupportUrl = useCallback(
    (value) => {
      dispatch(UpdateSupportJobUrlReducer(value));
    },
    [dispatch],
  );
  const setVersionInfo = useCallback(
    (value) => {
      dispatch(UpdateVersionInfoReducer(value));
    },
    [dispatch],
  );
  const setMenuInfo = useCallback(
    (value) => {
      dispatch(UpdateMenuInfoReducer(value));
    },
    [dispatch],
  );
  const setCategories = useCallback(
    (value) => {
      dispatch(UpdateCategoriesReducer(value));
    },
    [dispatch],
  );
  const initCommonSetting = useCallback(() => {
    dispatch(initialCommonAction());
  }, [dispatch]);

  const setBasicInfo = useCallback(
    (version, menu) => {
      if (version !== null) setVersionInfo(version);
      if (menu !== null) setMenuInfo(menu);
    },
    [MenuInfo, versionInfo],
  );
  const clearMenuInfo = useCallback(() => {
    setMenuInfo(null);
  }, [MenuInfo]);

  const openMgmtPage = () => {
    setMgmtshow(true);
  };

  const closeMgmtPage = () => {
    setMgmtshow(false);
  };

  const setEditPage = useCallback(
    (edit) => {
      console.log('setEditPage:', edit);
      setEdit(edit);
    },
    [setEdit],
  );

  const getUrl = ({ body }) => {
    let menuList = [];
    body.map((obj) => {
      obj.func.map((obj2) => {
        menuList.push({
          func: obj2.func_id,
          category: obj.title,
          func_name: obj2.title,
          path: `${obj.title}/${obj2.title}`,
          source: obj2?.info?.Source,
        });
      });
    });
    return menuList;
  };
  const categoryList = (info) => {
    const list = [];
    info.map((item, idx) =>
      list.push({ idx: idx, id: item.category_id, value: item.title }),
    );
    return list;
  };

  return {
    versionInfo,
    MenuInfo,
    setBasicInfo,
    clearMenuInfo,
    showMgmt,
    openMgmtPage,
    closeMgmtPage,
    currentPath,
    setCurrentPath,
    initCommonSetting,
    setSupportUrl,
    supportUrl,
    isEdit,
    setEditPage,
    setCategories,
    categories,
    getUrl,
    categoryList,
  };
};

export default useCommonJob;
