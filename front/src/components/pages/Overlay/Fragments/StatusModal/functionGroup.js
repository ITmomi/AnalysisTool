import {
  get_Overlay_Local_ConvertStatus,
  get_Overlay_Analysis_Info,
} from '../../../../../lib/api/axios/useOverlayRequest';

export const getStatus = async (id, cat) => {
  return await get_Overlay_Local_ConvertStatus({ jobId: id, category: cat });
};

export const getAnalysisInfo = async (id, cat) => {
  return await get_Overlay_Analysis_Info(cat, id);
};
