import { getRequest } from './requests';
import { URL_RESOURCE_ABOUT, URL_RESOURCE_MAIN } from '../Define/URL';

export const getMainResourceInfo = async () => {
  const { info } = await getRequest(URL_RESOURCE_MAIN);
  console.log('getMainResourceInfo: ', info);
  return info;
};

export const getMainVersionInfo = async () => {
  const { info } = await getRequest(URL_RESOURCE_ABOUT);
  console.log('getMainVersionInfo: ', info);
  return info;
};
