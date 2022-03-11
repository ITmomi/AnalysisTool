import { OVERLAY_ADC_MEASUREMENT, OVERLAY_CORRECTION } from './URL';

export const fixedTopMenu = [
  {
    category_id: 0,
    title: 'OVERLAY',
    func: [
      {
        func_id: `${OVERLAY_ADC_MEASUREMENT}`,
        info: undefined,
        title: 'Overlay ADC Meas.',
      },
      {
        func_id: `${OVERLAY_CORRECTION}`,
        info: undefined,
        title: 'Overlay Correction Comp.',
      },
    ],
  },
];
