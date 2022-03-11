import React, { useEffect } from 'react';
import { Route, Switch } from 'react-router-dom';
import Correction from './Correction/Correction';
import Measurement from './Measurement/Measurement';
import ModalProvider from '../../../lib/util/modalControl/ModalProvider';
import { default as OverlayModal } from '../../../lib/util/modalControl/Modal';
import {
  OVERLAY_ADC_MEASUREMENT,
  OVERLAY_CORRECTION,
} from '../../../lib/api/Define/URL';
import useOverlaySettingInfo from '../../../hooks/useOverlaySettingInfo';

const Overlay = () => {
  const { initialOverlayInfo } = useOverlaySettingInfo();
  useEffect(() => {
    console.log('Overlay component mounted !');
    return () => {
      console.log('Overlay component unmounted !');
      initialOverlayInfo();
    };
  }, []);

  return (
    <ModalProvider>
      <Switch>
        <Route path={OVERLAY_CORRECTION} component={Correction} />
        <Route path={OVERLAY_ADC_MEASUREMENT} component={Measurement} />
      </Switch>
      <OverlayModal />
    </ModalProvider>
  );
};
export default Overlay;
