import { MSG_LOCAL, MSG_REMOTE } from './Message';
import {
  AlignLeftOutlined,
  BarChartOutlined,
  DotChartOutlined,
  TableOutlined,
} from '@ant-design/icons';
import React from 'react';
import {
  E_CPVS_ADC_MEASUREMENT,
  E_CPVS_CORRECTION,
  E_OVERLAY_ANOVA,
  E_OVERLAY_COMPONENT,
  E_OVERLAY_IMAGE,
  E_OVERLAY_MAP,
  E_OVERLAY_REPRODUCIBILITY,
  E_OVERLAY_VARIATION,
} from './etc';

export const overlay_source = [MSG_LOCAL, MSG_REMOTE];

export const OVERLAY_MAP = {
  id: E_OVERLAY_MAP,
  title: 'Map',
  icon: <TableOutlined />,
};

export const OVERLAY_VARIATION = {
  id: E_OVERLAY_VARIATION,
  title: 'Variation',
  icon: <DotChartOutlined />,
};
export const OVERLAY_REPRODUCIBILITY = {
  id: E_OVERLAY_REPRODUCIBILITY,
  title: 'Reproducibility',
  icon: <BarChartOutlined />,
};
export const OVERLAY_ANOVA = {
  id: E_OVERLAY_ANOVA,
  title: 'Anova',
  icon: <AlignLeftOutlined />,
};
export const OVERLAY_IMAGE_MAP = {
  id: E_OVERLAY_IMAGE,
  title: 'Correction Image Map',
  icon: <TableOutlined />,
};
export const OVERLAY_COMPONENT_MAP = {
  id: E_OVERLAY_COMPONENT,
  title: 'Correction Component Map',
  icon: <TableOutlined />,
};

export const OVERLAY_CPVS_ADC_MEASUREMENT = {
  id: E_CPVS_ADC_MEASUREMENT,
  title: 'ADC Measurement',
  icon: undefined,
};

export const OVERLAY_CPVS_CORRECTION = {
  id: E_CPVS_CORRECTION,
  title: 'Correction component of exposure',
  icon: undefined,
};

export const OVERLAY_ADC_TYPE_LIST = [
  OVERLAY_MAP,
  OVERLAY_VARIATION,
  OVERLAY_REPRODUCIBILITY,
  OVERLAY_ANOVA,
];
export const OVERLAY_CORRECTION_TYPE_LIST = [
  OVERLAY_IMAGE_MAP,
  OVERLAY_COMPONENT_MAP,
];

export const OVERLAY_CORRECTION_CPVS_LIST = [
  OVERLAY_CPVS_ADC_MEASUREMENT,
  OVERLAY_CPVS_CORRECTION,
];
export const CPVS_MODE = {
  FROM_LOG: 'from_log',
  EACH: 'each_shot',
  SAME: 'reflect_all',
};
export const CPVS_DISP = {
  P1_P2_P3: 'P1&P2&P3',
  P1_P2: 'P1&P2',
  P2_P3: 'P2&P3',
  P2_ONLY: 'P2 Only',
  NONE: 'None',
};
export const CP_VS_DISPLAY_LIST = [
  CPVS_DISP.P1_P2_P3,
  CPVS_DISP.P1_P2,
  CPVS_DISP.P2_P3,
  CPVS_DISP.P2_ONLY,
  CPVS_DISP.NONE,
];

export const CP_VS_DISPLAY_OPTION = {
  [CPVS_DISP.P1_P2_P3]: 0,
  [CPVS_DISP.P1_P2]: 1,
  [CPVS_DISP.P2_P3]: 2,
  [CPVS_DISP.P2_ONLY]: 3,
  [CPVS_DISP.NONE]: 4,
};

export const OVERLAY_OFFSET_RESET = {
  x: 0,
  y: 0,
};
