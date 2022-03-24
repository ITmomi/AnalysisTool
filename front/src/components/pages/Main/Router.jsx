import React, { useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBinoculars } from '@fortawesome/free-solid-svg-icons';
import AppLayout from '../../templates/mainLayout';
import NaviBar from '../../UI/molecules/Navibar/NaviBar';
import { css } from '@emotion/react';
import VersionInfo from '../../UI/atoms/Version';
import Button from '../../UI/atoms/Button/Button';
import MgmtPage from '../Mgmt';
import { Spin } from 'antd';
import { Switch, Route } from 'react-router-dom';
import Error from '../Error';
import useCommonJob from '../../../hooks/useBasicInfo';
import {
  ANALYSIS,
  EDIT,
  MAIN,
  NEW,
  OVERLAY,
  TACT,
} from '../../../lib/api/Define/URL';
import JobStep from '../JobStep/JobStep';
import ResultMain from '../JobAnalysis/ResultMain';
import MainPage from './Main';
import { useQuery } from 'react-query';
import { QUERY_KEY } from '../../../lib/api/Define/QueryKey';
import Job from '../JobSetting/job';
import {
  getMainResourceInfo,
  getMainVersionInfo,
} from '../../../lib/api/axios/useMainRequest';
import NotificationBox from '../../UI/molecules/NotificationBox/Notification';
import Overlay from '../Overlay/Overlay';
import TactStatusMonitor from "../TACT/StatusMonitor/TactStatusMonitor";

const titleStyle = css`
  color: black;
  z-index: 300;
  font-weight: 400;
  font-size: 44px;
  text-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
  margin-bottom: 22px;
  margin-top: 22px;
`;

const buttonWrapper = css`
  position: fixed;
  bottom: 110px;
  right: 50px;
  z-index: 300;
`;

const loadingWrapper = css`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
`;

const Router = () => {
  const {
    setBasicInfo,
    versionInfo,
    MenuInfo,
    showMgmt,
    openMgmtPage,
    closeMgmtPage,
    initCommonSetting,
    setSupportUrl,
    setCategories,
    categoryList,
    getUrl,
  } = useCommonJob();

  const {
    error: MainError,
    isLoading: isMainLoading,
    isFetching: isMainReLoading,
  } = useQuery([QUERY_KEY.MAIN_INIT], getMainResourceInfo, {
    onSuccess: (info) => {
      setSupportUrl(getUrl({ body: info.body }));
      setBasicInfo(null, info);
      setCategories(categoryList(info?.body));
    },
    onError: (error) => {
      NotificationBox('ERROR', error.message, 4.5);
    },
  });
  const { error: VersionError, isLoading: isVersionLoading } = useQuery(
    [QUERY_KEY.VERSION_INIT],
    getMainVersionInfo,
    {
      onSuccess: (info) => {
        setBasicInfo(info, null);
      },
      onError: (error) => {
        NotificationBox('ERROR', error.message, 4.5);
      },
    },
  );

  useEffect(() => {
    initCommonSetting();
  }, []);

  if (isVersionLoading || isMainLoading || isMainReLoading)
    return (
      <div css={loadingWrapper}>
        <Spin tip="Loading..." size="large" />
      </div>
    );

  if (MainError || VersionError)
    return (
      <div>
        <p>error occurred</p>
        <p>{VersionError?.message ?? MainError?.message ?? 'ERROR'}</p>
      </div>
    );

  if (versionInfo === '' || MenuInfo === '') return <div>no data</div>;

  const { title, footer } = MenuInfo;

  return (
    <>
      <AppLayout>
        <AppLayout.Header>
          <p css={titleStyle}>{title}</p>
          <NaviBar />
        </AppLayout.Header>
        <AppLayout.Content>
          <Switch>
            <Route exact path={MAIN} component={MainPage} />
            <Route path={ANALYSIS} component={ResultMain} />
            <Route
              path={[`${NEW}/:type/:category_id`, `${EDIT}/:type/:func_id`]}
              component={JobStep}
            />
            <Route path={OVERLAY} component={Overlay} />
            <Route path={TACT} component={TactStatusMonitor}/>
            <Route path={MAIN} component={Error.notfound} />
          </Switch>
        </AppLayout.Content>
        <AppLayout.Footer>
          <VersionInfo footer={footer} info={versionInfo} />
        </AppLayout.Footer>
        <div css={buttonWrapper}>
          <Button iconOnly size="md" onClick={openMgmtPage}>
            <FontAwesomeIcon icon={faBinoculars} />
          </Button>
        </div>
        <MgmtPage show={showMgmt} closeFunc={closeMgmtPage} />
        <Job />
      </AppLayout>
    </>
  );
};

export default Router;
