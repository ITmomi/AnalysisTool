import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import useRuleSettingInfo from '../../../hooks/useRuleSettingInfo';
import useCommonJob from '../../../hooks/useBasicInfo';
import MainPageItem from '../../UI/molecules/MainPageItem';
import { css } from '@emotion/react';
import {
  MSG_ALL_STRING_REGEXP,
  MSG_BUTTON_MSG,
  MSG_STEP1_CATEGORY,
  MSG_STEP1_MAIN_TITLE,
} from '../../../lib/api/Define/Message';
import { useParams } from 'react-router';
import { E_STEP_1, E_STEP_2, R_OK } from '../../../lib/api/Define/etc';
import { getParseData } from '../../../lib/util/Util';
import InputForm from '../../UI/atoms/Input/InputForm';
import { E_JOB_STEP } from '../../../lib/api/Define/JobStepEnum';
import { SingleJobStepConf as steps } from '../../../hooks/useJobStepInfo';
import { getRequest, getRequestParam } from '../../../lib/api/axios/requests';
import { NotificationBox } from '../../UI/molecules/NotificationBox';
import { AllMax30Regex } from '../../../lib/util/RegExp';

const itemWrapper = css`
  word-break: break-word;
  margin: 2rem 0;
  display: flex;
  & > div + div {
    margin-left: 4.9rem;
  }
`;
const nextRequest = async ({ setLoading, func_id }) => {
  try {
    const { info, status } =
      func_id !== undefined
        ? await getRequestParam(steps[E_STEP_1].edit, func_id)
        : await getRequest(steps[E_STEP_1].new);
    setLoading(false);
    if (status === R_OK) {
      return { info: { config: info }, next: E_STEP_2 };
    }
  } catch (e) {
    NotificationBox('ERROR', e.response.message);
    return { info: undefined, next: undefined };
  }
};

const NextButtonEvent = ({ setLoading, func_id }) => {
  setLoading(true);
  return nextRequest({ setLoading, func_id }).then((_) => _);
};
const PreviewButtonEvent = () => {};
const PreviousButtonEvent = () => {
  return false;
};
const nextEnableCheck = (funcStepInfo, menuInfo, func_id) => {
  const isValid =
    AllMax30Regex.test(funcStepInfo?.title ?? '') &&
    !duplicateCheck(menuInfo, funcStepInfo?.title ?? '', func_id);
  return Boolean((funcStepInfo?.category?.selected ?? false) && isValid);
};
const previewEnableCheck = () => false;

const duplicateCheck = (data, v, index) => {
  let i = 0,
    isDuplicate = false;

  while (i < data.length) {
    const currentData = data[i].func.find((x) => x.title === v);

    if (
      currentData &&
      (index === undefined || currentData.func_id !== Number(index))
    ) {
      isDuplicate = true;
      break;
    }

    i++;
  }

  return isDuplicate;
};

const ContentsForm = ({ onChange }) => {
  const { updateFuncInfo, funcStepInfo, ruleStepConfig } = useRuleSettingInfo();
  const { MenuInfo } = useCommonJob();
  const [stepInfo, setStepInfo] = useState({});
  const [categories, setCategories] = useState({});
  const { category_id, func_id } = useParams();

  useEffect(() => {
    const clone = { ...funcStepInfo };
    const ruleConfig = ruleStepConfig.find((item) => item.step === E_STEP_1);

    if (ruleConfig?.config ?? false) {
      if (Object.keys(stepInfo).length === 0) {
        const { category } = ruleConfig.config;
        const category_selected =
          category?.selected ?? category_id ?? category.options[0].category_id;
        if (Object.keys(clone).length === 0) {
          console.log('clone empty', clone);
        } else {
          setStepInfo(clone);
        }
        const findObj = category.options.find(
          (item) => item.category_id === parseInt(category_selected),
        );
        setCategories({
          original: category.options,
          options: category.options.map((obj) => obj.title),
          title: findObj?.title ?? category.options[0].title,
        });
        if (findObj) onChange({ category_id: findObj.title });
      }
    }
  }, [ruleStepConfig]);

  useEffect(() => {
    updateFuncInfo(stepInfo);
  }, [stepInfo]);

  const ChangeFunc = (e) => {
    const obj = getParseData(e);
    if (obj.id === E_JOB_STEP.STEP1_CATEGORY_ID) {
      const { original } = categories;
      console.log('ChangeFunc', e);
      const findObj = original?.find((item) => item.title === obj.value) ?? {};

      if (findObj.title !== categories.title || (stepInfo?.selected ?? true)) {
        setStepInfo((prevState) => ({
          ...prevState,
          category: {
            ...prevState.category,
            selected: parseInt(findObj.category_id),
          },
        }));
        setCategories((prevState) => ({
          ...prevState,
          title: obj.value,
        }));
      }
    } else {
      setStepInfo({ ...stepInfo, ...e });
    }
  };

  const titleDuplicateCheck = (v) => {
    return !duplicateCheck(MenuInfo.body, v, func_id)
      ? Promise.resolve()
      : Promise.reject(new Error('Main title is duplicated.'));
  };

  if (
    Object.keys(categories).length === 0 ||
    Object.keys(funcStepInfo).length === 0
  )
    return <></>;

  return (
    <div style={{ width: '400px', margin: '26px 0px' }}>
      <InputForm.select
        formName={E_JOB_STEP.STEP1_CATEGORY_ID}
        formLabel={MSG_STEP1_CATEGORY}
        options={categories?.options ?? []}
        defaultV={categories?.title ?? ''}
        changeFunc={(e) => ChangeFunc(e)}
        required={true}
      />
      <InputForm.input
        formName={E_JOB_STEP.STEP1_TITLE}
        formLabel={MSG_STEP1_MAIN_TITLE}
        changeFunc={(e) => ChangeFunc(e)}
        required={true}
        value={funcStepInfo?.title ?? ''}
        regExp={{ pattern: AllMax30Regex, message: MSG_ALL_STRING_REGEXP }}
        checkFunc={titleDuplicateCheck}
      />
    </div>
  );
};
ContentsForm.propTypes = {
  onChange: PropTypes.func,
};

const PreviewForm = () => {
  const { funcStepInfo } = useRuleSettingInfo();
  if (funcStepInfo === undefined) return <></>;

  return (
    <div css={itemWrapper}>
      <MainPageItem
        isEditMode={false}
        mainText={funcStepInfo?.title ?? ''}
        subText={''}
        buttonText={MSG_BUTTON_MSG}
        onClick={(e) => e.preventDefault()}
      />
    </div>
  );
};
const Step1_Setting = ({ children }) => {
  return <div>{children}</div>;
};

Step1_Setting.propTypes = {
  children: PropTypes.node,
};
Step1_Setting.btn_next = NextButtonEvent;
Step1_Setting.btn_previous = PreviousButtonEvent;
Step1_Setting.btn_preview = PreviewButtonEvent;
Step1_Setting.check_next = nextEnableCheck;
Step1_Setting.check_preview = previewEnableCheck;
Step1_Setting.view_contents = ContentsForm;
Step1_Setting.view_preview = PreviewForm;

export default Step1_Setting;
