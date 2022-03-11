import {
  MSG_CUSTOM_STEP1,
  MSG_CUSTOM_STEP2,
  MSG_CUSTOM_STEP3,
  MSG_CUSTOM_STEP4,
  MSG_CUSTOM_STEP5,
  MSG_CUSTOM_STEP6,
  MSG_PROGRESS,
  MSG_WAITING,
} from '../lib/api/Define/Message';
import {
  URL_PREVIEW_ANALYSIS,
  URL_PREVIEW_CONVERT,
  URL_PREVIEW_FILTER,
  URL_PREVIEW_SAMPLELOG,
  URL_RESOURCE_EDIT,
  URL_RESOURCE_EDIT_INIT,
  URL_RESOURCE_EDIT_STEP1,
  URL_RESOURCE_EDIT_STEP2,
  URL_RESOURCE_EDIT_STEP3,
  URL_RESOURCE_EDIT_STEP4,
  URL_RESOURCE_EDIT_STEP5,
  URL_RESOURCE_NEW,
  URL_RESOURCE_NEW_INIT,
  URL_RESOURCE_NEW_STEP1,
  URL_RESOURCE_NEW_STEP2,
  URL_PREVIEW_ANALYSIS_MULTI,
} from '../lib/api/Define/URL';

export const SingleJobStepConf = [
  {
    //STEP 1
    title: MSG_PROGRESS,
    description: MSG_CUSTOM_STEP1,
    new_init: URL_RESOURCE_NEW_INIT, //init
    edit_init: URL_RESOURCE_EDIT_INIT, //init
    new: URL_RESOURCE_NEW_STEP1, //next
    edit: URL_RESOURCE_EDIT_STEP1, //next
  },
  {
    //STEP 2
    title: MSG_WAITING,
    description: MSG_CUSTOM_STEP2,
    new: URL_RESOURCE_NEW_STEP2, //next
    edit: URL_RESOURCE_EDIT_STEP2, //next
    preview: URL_PREVIEW_SAMPLELOG,
  },
  {
    //STEP 3
    title: MSG_WAITING,
    description: MSG_CUSTOM_STEP3,
    edit: URL_RESOURCE_EDIT_STEP3, //next
    preview: URL_PREVIEW_CONVERT,
  },
  {
    //STEP 4
    title: MSG_WAITING,
    description: MSG_CUSTOM_STEP4,
    edit: URL_RESOURCE_EDIT_STEP4, //next
    preview: URL_PREVIEW_FILTER,
  },
  {
    //STEP 5
    title: MSG_WAITING,
    description: MSG_CUSTOM_STEP5,
    edit: URL_RESOURCE_EDIT_STEP5, //next
    preview: URL_PREVIEW_ANALYSIS,
  },
  {
    //STEP 6
    title: MSG_WAITING,
    description: MSG_CUSTOM_STEP6,
    new_save: URL_RESOURCE_NEW,
    edit_save: URL_RESOURCE_EDIT,
  },
];

export const MultiJobStepConf = [
  {
    //STEP 1
    title: MSG_PROGRESS,
    description: MSG_CUSTOM_STEP1,
    new_init: URL_RESOURCE_NEW_INIT, //init
    edit_init: URL_RESOURCE_EDIT_INIT, //init
    new: URL_RESOURCE_NEW_STEP1, //next
    edit: URL_RESOURCE_EDIT_STEP1, //next
  },
  {
    //STEP 2
    title: MSG_WAITING,
    description: MSG_CUSTOM_STEP2,
    new: URL_RESOURCE_NEW_STEP2, //next
    edit: URL_RESOURCE_EDIT_STEP2, //next
    preview: URL_PREVIEW_SAMPLELOG,
  },
  {
    //STEP 3
    title: MSG_WAITING,
    description: MSG_CUSTOM_STEP5,
    edit: URL_RESOURCE_EDIT_STEP5, //next
    preview: URL_PREVIEW_ANALYSIS_MULTI,
  },
  {
    //STEP 4
    title: MSG_WAITING,
    description: MSG_CUSTOM_STEP6,
    new_save: URL_RESOURCE_NEW,
    edit_save: URL_RESOURCE_EDIT,
  },
];
