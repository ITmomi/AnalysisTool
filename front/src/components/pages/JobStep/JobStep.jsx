import React, { useEffect, useState } from 'react';
import { css } from '@emotion/react';
import Button2 from '../../UI/atoms/Button';
import Divider from '../../UI/atoms/Divider';
import { Button, Popconfirm, Spin, Steps } from 'antd';
import {
  MSG_CANCEL,
  MSG_CONFIRM_CANCEL,
  MSG_FINISHED,
  MSG_MULTI,
  MSG_NEXT,
  MSG_PREVIEW,
  MSG_PREVIOUS,
  MSG_PROGRESS,
  MSG_LOCAL,
  MSG_REMOTE,
  MSG_SAVE_SETTING,
  MSG_SQL,
  MSG_WAITING,
} from '../../../lib/api/Define/Message';
import {
  LeftCircleFilled,
  ReadFilled,
  RightCircleFilled,
  LineChartOutlined,
} from '@ant-design/icons';
import {
  getArray,
  getFormdataFiles,
  getParseJsonData,
} from '../../../lib/util/Util';
import StepSetting from './StepSetting';
import { MAIN, URL_RESOURCE_SCRIPT } from '../../../lib/api/Define/URL';
import {
  postRequestFormData,
  postRequestJsonData,
} from '../../../lib/api/axios/requests';
import {
  E_MULTI_TYPE,
  E_SINGLE_TYPE,
  E_STEP_1,
  E_STEP_2,
  E_STEP_3,
  E_STEP_4,
  E_STEP_5,
  E_STEP_6,
  RESPONSE_OK,
} from '../../../lib/api/Define/etc';
import useRuleSettingInfo from '../../../hooks/useRuleSettingInfo';
import useCommonJob from '../../../hooks/useBasicInfo';
import { useHistory, useParams } from 'react-router';

const { Step } = Steps;
import {
  SingleJobStepConf as steps,
  MultiJobStepConf as multiSteps,
} from '../../../hooks/useJobStepInfo';
import { QUERY_KEY } from '../../../lib/api/Define/QueryKey';
import { useQuery, useQueryClient } from 'react-query';
import GraphAddEdit from '../../UI/organisms/GraphAddEdit/GraphAddEdit';
import Step1_Setting from './Step1_Setting';
import Step2_Setting from './Step2_Setting';
import Step3_Setting from './Step3_Setting';
import Step4_Setting from './Step4_Setting';
import Step5_Setting from './Step5_Setting';
import Step2_Multi_Setting from './MultiAnalysis/Step2_Setting';
import Step3_Multi_Setting from './MultiAnalysis/Step3_Setting';
import Step4_Multi_Setting from './MultiAnalysis/Step4_Setting';
import useJobStepSettingInfo from '../../../hooks/useJobSetpSettingInfo';
import {
  getEditStep1Resource,
  getStep1Resource,
} from '../../../lib/api/axios/useJobStepRequest';
import { NotificationBox } from '../../UI/molecules/NotificationBox';

const MenuBarWrapper = css`
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
`;
const MenuButton = css`
  font-weight: 400;
  margin-left: 8px;
`;
const bodyFrame = css`
  background: #ffffff;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
  border-radius: 1px;

  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 12px;
  margin: 15px 0px;
`;

const dividerStyle = css`
  display: flex;
  border: 2px solid #8c8c8c;
`;
const StepFrameStyle = css`
  display: contents;
  justify-content: space-between;
  align-items: center;
  & span.ant-steps-icon {
    position: relative;
    top: -2px;
  }
`;

const directionButton = css`
  font-weight: 400;
  margin-left: 8px;
  box-sizing: border-box;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
  border-radius: 8px;
`;
const TitleFrameStyle = css`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;

  flex: none;
  order: 2;
  align-self: stretch;
  flex-grow: 0;

  margin-top: 10px;
  margin-bottom: 10px;
`;
const ContentsFrameStyle = css`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0px 4px 4px;

  flex: none;
  order: 2;
  align-self: stretch;
  flex-grow: 0;
  margin: 12px 0px;
  & .ant-form-item-label {
    text-align: left;
    max-width: 130px;
  }
`;

const PreviewFrameStyle = css`
  background: #fafafa;
  display: flex;
  flex-direction: column;

  flex: none;
  order: 3;
  align-self: stretch;
  flex-grow: 0;

  border: 1px solid #d9d9d9;
  box-sizing: border-box;
  border-radius: 8px;

  min-height: 300px;
`;
const PreviewTitleStyle = css`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-height: 32px;
  align-items: center;
  margin: 10px 10px 0px 10px;
  padding: 0px 10px 0px 10px;
`;
const graphFrameStyle = css`
  background-color: white;
  margin: 0;
  padding: 1rem;
  border-radius: 8px;
  min-height: 300px;
`;
const SINGLE_MAX_STEP = E_STEP_6;
const MULTI_MAX_STEP = E_STEP_4;

const getMaxStep = ({ type }) => {
  return type === E_SINGLE_TYPE ? SINGLE_MAX_STEP : MULTI_MAX_STEP;
};

const getVisualStep = ({ type }) => {
  return type === E_SINGLE_TYPE ? E_STEP_6 : E_STEP_4;
};
const JobStep = () => {
  const [current, setCurrent] = useState(0);
  const [data, setData] = useState(null);
  const [isEditMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isAddOpen, setIsAddOpen] = useState(false);
  const history = useHistory();
  let { func_id, category_id, type } = useParams();
  const { initialRuleSetting, updateFuncInfo } = useRuleSettingInfo();
  const {
    setRuleStepConfig,
    ruleStepConfig,
    convertStepInfo,
    filterStepInfo,
    analysisStepInfo,
    funcStepInfo,
    visualStepInfo,
  } = useRuleSettingInfo();
  const { MenuInfo } = useCommonJob();
  const {
    addNextStepConfig,
    addCurrentStepPreview,
    updateStepSetting,
    addStepPreviewAndNext,
  } = useJobStepSettingInfo();
  const queryClient = useQueryClient();

  useQuery(
    [QUERY_KEY.STEP1_NEW_INIT],
    () =>
      getStep1Resource({
        url:
          type === E_SINGLE_TYPE
            ? steps[current].new_init
            : multiSteps[current].new_init,
      }),
    {
      enabled: Boolean((category_id ?? false) && (type ?? false)),
      onSuccess: ({ info }) => {
        console.log('category_id', category_id);
        const Obj = {
          category: {
            options: info.category.options,
            selected: info.category?.selected ?? category_id,
          },
          title: info?.title ?? '',
          source_type: funcStepInfo.source_type,
        };
        updateFuncInfo(Obj);
        setRuleStepConfig([...ruleStepConfig, { step: current, config: Obj }]);
      },
      onError: (error) => {
        NotificationBox('ERROR', error.message);
      },
    },
  );

  useQuery(
    [QUERY_KEY.STEP1_EDIT_INIT],
    () =>
      getEditStep1Resource({
        url:
          type === E_SINGLE_TYPE
            ? `${steps[current].edit_init}/${func_id}`
            : `${multiSteps[current].edit_init}/${func_id}`,
      }),
    {
      enabled: Boolean((func_id ?? false) && (type ?? false)),
      onSuccess: ({ info }) => {
        console.log('func_id', func_id);
        setEditMode(true);
        updateFuncInfo(info);
        setRuleStepConfig([...ruleStepConfig, { step: current, config: info }]);
      },
      onError: (error) => {
        NotificationBox('ERROR', error.message);
      },
    },
  );

  const saveSetting = () => {
    console.log('saveSetting start');
    const postRequest = async () => {
      const convertTmp = { ...convertStepInfo };
      const analysisTmp = { ...analysisStepInfo };
      const filterTmp = [...filterStepInfo];
      const visualTmp = { ...visualStepInfo };
      const funcTemp = { ...funcStepInfo };
      const rule_id = isEditMode
        ? convertStepInfo?.log_define?.rule_id ?? undefined
        : undefined;
      console.log('rule_id', rule_id);

      const obj = Object.assign(
        {},
        {
          func:
            funcTemp.source_type === MSG_MULTI
              ? {
                  category_id: funcTemp.category.selected,
                  title: funcTemp.title,
                  source_type: MSG_MULTI,
                  info: funcTemp.list.map((o) => {
                    const formList = isEditMode
                      ? ruleStepConfig[E_STEP_2].config?.data?.formList ?? []
                      : [];
                    const form_id =
                      formList.find(
                        (obj) => obj.multi_info_id === o.multi_info_id,
                      )?.multi_info_id ?? null;
                    return o.source_type === MSG_LOCAL
                      ? {
                          func_id: o.sub_func_id,
                          tab_name: o.tab_name,
                          multi_info_id: isEditMode ? form_id : null,
                          fid: o.fid,
                          rid: o.rid,
                        }
                      : o.source_type === MSG_REMOTE
                      ? {
                          func_id: o.sub_func_id,
                          tab_name: o.tab_name,
                          multi_info_id: isEditMode ? form_id : null,
                          rid: o.rid,
                          db_id: o.info.db_id,
                          table_name: o.info.table_name,
                          equipment_name: o.info.equipment_name,
                          period_start: o.info.selected.start,
                          period_end: o.info.selected.end,
                        }
                      : o.source_type === MSG_SQL
                      ? {
                          func_id: o.sub_func_id,
                          tab_name: o.tab_name,
                          multi_info_id: isEditMode ? form_id : null,
                          rid: o.rid,
                          db_id: o.info.db_id,
                          sql: o.info.sql,
                        }
                      : {};
                  }),
                  use_org_analysis: funcTemp.use_org_analysis,
                }
              : {
                  category_id: funcTemp.category.selected,
                  title: funcTemp.title,
                  source_type: funcTemp.source_type,
                  info:
                    funcTemp.source_type === MSG_REMOTE
                      ? {
                          db_id: funcTemp.info.db_id,
                          table_name: funcTemp.info.table_name,
                          equipment_name: funcTemp.info.equipment_name,
                          period_start: funcTemp.info.selected.start,
                          period_end: funcTemp.info.selected.end,
                        }
                      : funcTemp.source_type === MSG_SQL
                      ? {
                          db_id: funcTemp.info.db_id,
                          sql: funcTemp.info.sql,
                        }
                      : {},
                  script: {
                    file_name: funcTemp?.script?.file_name ?? null,
                    use_script: funcTemp?.script?.use_script ?? false,
                  },
                },
          convert:
            funcTemp.source_type === MSG_MULTI
              ? {}
              : {
                  mode: convertStepInfo.mode,
                  log_define: convertStepInfo?.log_define,
                  info: getArray(convertTmp?.info ?? [], true, false),
                  header: getArray(convertTmp?.header ?? [], true, false),
                  custom: getArray(convertTmp?.custom ?? [], false, false),
                  script: {
                    file_name: convertTmp?.script?.file_name ?? null,
                    use_script: convertTmp?.script?.use_script ?? false,
                  },
                },
          filter:
            funcTemp.source_type === MSG_MULTI
              ? {}
              : {
                  items: getArray(filterTmp, false),
                },
          analysis: {
            type: analysisTmp?.type ?? 'setting',
            setting: {
              items:
                funcTemp.source_type === MSG_MULTI
                  ? getArray(analysisTmp?.items ?? [], false, true).map(
                      (obj) => ({
                        ...obj,
                        source_col: obj.source_col.map((obj2) =>
                          obj2.join('/'),
                        ),
                      }),
                    )
                  : getArray(analysisTmp.items, false, true) ?? [],
              filter_default: analysisTmp.filter_default ?? [],
              aggregation_default: analysisTmp.aggregation_default ?? {},
            },
            script: {
              db_id: analysisTmp?.script?.db_id ?? null,
              sql: analysisTmp?.script?.sql ?? null,
              file_name: analysisTmp?.script?.file_name ?? null,
              use_script: analysisTmp?.script?.use_script ?? false,
            },
          },
          visualization: {
            function_graph_type: visualTmp.function_graph_type,
            items:
              visualTmp.items.length === 0
                ? []
                : visualTmp.items
                    .filter((v) => v !== '')
                    .map((v) => {
                      return {
                        id: v.id,
                        title: v.title,
                        type: v.type,
                        x_axis: v.x_axis,
                        y_axis: v.y_axis.map((o) =>
                          Array.isArray(o) ? o.join('/') : o,
                        ),
                        z_axis: Array.isArray(v.z_axis)
                          ? v.z_axis.join('/')
                          : v.z_axis,
                        x_range_min: v.x_range_min,
                        x_range_max: v.x_range_max,
                        y_range_min: v.y_range_min,
                        y_range_max: v.y_range_max,
                        z_range_min: v.z_range_min,
                        z_range_max: v.z_range_max,
                      };
                    }),
          },
        },
      );
      try {
        console.log('isEditMode', isEditMode);
        const url = isEditMode
          ? (type === E_SINGLE_TYPE ? steps[current] : multiSteps[current])
              .edit_save
          : (type === E_SINGLE_TYPE ? steps[current] : multiSteps[current])
              .new_save;
        const { status, info } = await postRequestJsonData(
          isEditMode ? `${url}/${func_id}` : url,
          undefined,
          JSON.stringify(obj),
        );
        if (status.toString() === RESPONSE_OK) {
          console.log('info', info);
          const param = getParseJsonData({
            analysis:
              analysisTmp?.script?.file_name ?? false
                ? getFormdataFiles(data?.step5_script ?? null)
                : null,
            convert:
              convertTmp?.script?.file_name ?? false
                ? getFormdataFiles(data?.step3_script ?? null)
                : null,
            preprocess:
              funcTemp?.script?.file_name ?? false
                ? getFormdataFiles(data?.step2_script ?? null)
                : null,
          }).filter((obj) => obj.value !== null);
          const FormObj = new FormData();
          if (param.length > 0) {
            param.map((obj) => FormObj.append(obj.id, obj.value));
            const { status: status2 } = await postRequestFormData(
              `${URL_RESOURCE_SCRIPT}/${isEditMode ? func_id : info.func_id}`,
              FormObj,
            );
            if (status2.toString() === RESPONSE_OK) {
              queryClient
                .invalidateQueries([QUERY_KEY.MAIN_INIT])
                .then((_) => _);

              history.push({
                pathname: MAIN,
              });
              setLoading(false);
            }
          } else {
            queryClient.invalidateQueries([QUERY_KEY.MAIN_INIT]).then((_) => _);

            history.push({
              pathname: MAIN,
            });
            setLoading(false);
          }
        }
      } catch (e) {
        if (e.response) {
          const {
            data: { msg, err },
          } = e.response;
          console.log(e.response);
          NotificationBox('ERROR', msg ?? err);
        }
        setLoading(false);
      }
    };
    setLoading(true);
    postRequest().then((_) => _);
  };

  const nextButton = async () => {
    console.log('nextButton');
    let result = { next: undefined, info: undefined, preview: undefined };

    switch (current) {
      case E_STEP_1:
        result = await Step1_Setting.btn_next({ setLoading, func_id });
        break;
      case E_STEP_2:
        result =
          type === E_SINGLE_TYPE
            ? await Step2_Setting.btn_next({
                setLoading,
                func_id,
                convertStepInfo,
                funcStepInfo,
                data: { data: data, func: setData },
              })
            : await Step2_Multi_Setting.btn_next({
                setLoading,
                funcStepInfo,
                updateFuncInfo,
                func_id,
                data: { data: data, func: setData },
              });
        if (result?.info ?? false) {
          updateStepSetting({ info: result.info.config });
        }
        setLoading(false);
        break;
      case E_STEP_3:
        result =
          type === E_SINGLE_TYPE
            ? await Step3_Setting.btn_next({
                setLoading,
                convertStepInfo,
                data: { data: data, func: setData },
                func_id,
                originLog:
                  ruleStepConfig.find((obj) => obj.step === E_STEP_2)?.data ??
                  [],
              })
            : await Step3_Multi_Setting.btn_next({
                setLoading,
                analysisStepInfo,
                funcStepInfo,
                data: { data: data, func: setData },
                func_id,
                originLog:
                  ruleStepConfig.find((obj) => obj.step === E_STEP_2)?.data ??
                  [],
              });
        setLoading(false);
        break;
      case E_STEP_4:
        result = await Step4_Setting.btn_next({
          setLoading,
          filterStepInfo,
          data: { data: data, func: setData },
          originLog:
            ruleStepConfig.find((obj) => obj.step === E_STEP_3)?.data ?? [],
        });
        setLoading(false);
        break;
      case E_STEP_5:
        result = await Step5_Setting.btn_next({
          setLoading,
          analysisStepInfo,
          data: { data: data, func: setData },
          func_id,
          originLog:
            funcStepInfo.source_type === MSG_LOCAL
              ? ruleStepConfig.find((obj) => obj.step === E_STEP_4)?.data ?? []
              : ruleStepConfig.find((obj) => obj.step === E_STEP_2)?.data
                  ?.data ?? [],
        });
        setLoading(false);
        break;
      default:
        break;
    }
    console.log('result:::::::', result);
    if ((result?.preview ?? false) && (result?.next ?? false)) {
      const { preview } = result;
      console.log('preview', preview);
      addStepPreviewAndNext({
        next: result?.next ?? current + 1,
        preview: preview,
        info: result?.info ?? {},
      });
      setCurrent(result?.next ?? current + 1);
    } else if (result?.next ?? false) {
      addNextStepConfig({
        next: result?.next ?? current + 1,
        info: result?.info ?? {},
        setCurrent,
      });
    } else if (result?.preview ?? false) {
      const { preview } = result;
      console.log('preview', preview);
      addCurrentStepPreview({
        current: preview.current,
        info: preview.info,
      });
    } else {
      console.log('');
    }
  };

  const nextStepValid = () => {
    let ret = true;
    switch (current) {
      case E_STEP_1:
        ret = Step1_Setting.check_next(funcStepInfo, MenuInfo.body, func_id);
        break;
      case E_STEP_2:
        ret =
          type === E_SINGLE_TYPE
            ? Step2_Setting.check_next(
                funcStepInfo,
                convertStepInfo,
                isEditMode,
              )
            : Step2_Multi_Setting.check_next({ funcStepInfo });
        break;
      case E_STEP_3:
        ret =
          type === E_SINGLE_TYPE
            ? Step3_Setting.check_next(convertStepInfo)
            : Step3_Multi_Setting.check_next(analysisStepInfo);
        break;
      case E_STEP_4:
        ret =
          type === E_SINGLE_TYPE
            ? Step4_Setting.check_next(filterStepInfo)
            : Step4_Multi_Setting.check_next();
        break;
      case E_STEP_5:
        ret = Step5_Setting.check_next(analysisStepInfo);
        break;
      default:
        break;
    }
    return ret;
  };
  const onChange = (e) => {
    console.log('[jobStep ]', e);
    setData((prev) => {
      return { ...prev, ...e };
    });
  };
  const Enable_Preview = () => {
    let ret = true;
    switch (current) {
      case E_STEP_1:
        ret = Step1_Setting.check_preview();
        break;
      case E_STEP_2:
        ret =
          type === E_SINGLE_TYPE
            ? Step2_Setting.check_preview(funcStepInfo)
            : Step2_Multi_Setting.check_preview({ funcStepInfo });
        break;
      case E_STEP_3:
        ret =
          type === E_SINGLE_TYPE
            ? Step3_Setting.check_preview(convertStepInfo)
            : Step3_Multi_Setting.check_preview(analysisStepInfo);
        break;
      case E_STEP_4:
        ret = Step4_Setting.check_preview(filterStepInfo);
        break;
      case E_STEP_5:
        ret = Step5_Setting.check_preview(analysisStepInfo);
        break;
      default:
        if (steps[current].preview === undefined) {
          ret = false;
        }
        break;
    }
    return ret;
  };

  const PreviousOnClick = () => {
    let result = { status: '', step: 0 };
    console.log('steps[current].Previous');
    if (type === E_SINGLE_TYPE && current === E_STEP_5) {
      result = Step5_Setting.btn_previous(funcStepInfo);
    } else if (type === E_MULTI_TYPE && current === E_STEP_4) {
      result = Step4_Multi_Setting.btn_previous({ funcStepInfo });
    }
    if (result.status === 'pass') {
      setCurrent(result.step);
    } else {
      setCurrent(current - 1);
    }
  };
  const previewOnClick = () => {
    console.log('steps[current].preview', steps[current].preview);
    const previewRequest = async () => {
      switch (current) {
        case E_STEP_2:
          {
            const result =
              type === E_SINGLE_TYPE
                ? await Step2_Setting.btn_preview({
                    func_id,
                    funcStepInfo,
                    data,
                    setData,
                    enable: Step2_Setting.check_preview(funcStepInfo),
                  })
                : await Step2_Multi_Setting.btn_preview({
                    func_id,
                    funcStepInfo,
                    updateFuncInfo,
                    data,
                    setData,
                  });
            console.log('preview result', result);
            if (result?.data ?? false) {
              addCurrentStepPreview({
                current: result?.step ?? E_STEP_2,
                info: result.data,
              });
            }
          }
          break;
        case E_STEP_3:
          {
            const result =
              type === E_SINGLE_TYPE
                ? await Step3_Setting.btn_preview({
                    data,
                    setData,
                    convertStepInfo,
                    func_id,
                    originLog:
                      ruleStepConfig.find((obj) => obj.step === E_STEP_2)
                        ?.data ?? [],
                  })
                : await Step3_Multi_Setting.btn_preview({
                    funcStepInfo,
                    func_id,
                    analysisStepInfo,
                    setData,
                    data,
                    originLog:
                      ruleStepConfig.find((obj) => obj.step === E_STEP_2)?.data
                        .data ?? [],
                  });
            console.log('preview result', result);
            if (result?.data ?? false) {
              addCurrentStepPreview({
                current: result?.step ?? E_STEP_3,
                info: result.data,
              });
            }
          }
          break;
        case E_STEP_4:
          {
            const result = await Step4_Setting.btn_preview({
              setData,
              filterStepInfo,
              originLog:
                ruleStepConfig.find((obj) => obj.step === E_STEP_3)?.data ?? [],
            });
            console.log('preview result', result);
            if (result?.data ?? false) {
              addCurrentStepPreview({
                current: result?.step ?? E_STEP_4,
                info: result.data,
              });
            }
          }
          break;
        case E_STEP_5:
          {
            const result = await Step5_Setting.btn_preview({
              analysisStepInfo,
              func_id,
              data,
              setData,
              originLog:
                funcStepInfo.source_type === MSG_LOCAL
                  ? ruleStepConfig.find((obj) => obj.step === E_STEP_4)?.data ??
                    []
                  : ruleStepConfig.find((obj) => obj.step === E_STEP_2)?.data
                      ?.data ?? [],
            });
            console.log('preview result', result);
            if (result?.data ?? false) {
              addCurrentStepPreview({
                current: result?.step ?? E_STEP_5,
                info: result.data,
              });
            }
          }
          break;
        default:
          break;
      }
    };
    previewRequest().then((_) => _);
  };
  const addGraphData = () => {
    const PreviousStep =
      type === E_SINGLE_TYPE
        ? E_STEP_5
        : funcStepInfo.use_org_analysis
        ? E_STEP_2
        : E_STEP_3;
    const StepData = ruleStepConfig.find((obj) => obj.step === PreviousStep);

    return StepData.data;
  };
  useEffect(() => {
    console.log('UseEffect DATA', data);
  }, [data]);

  useEffect(() => {
    console.log('===============JobStep===============');
    updateFuncInfo({
      ...funcStepInfo,
      source_type: type === E_SINGLE_TYPE ? undefined : MSG_MULTI,
    });
    return () => {
      initialRuleSetting();
    };
  }, []);
  return (
    <>
      <div>
        <Spin
          spinning={loading && current === getMaxStep({ type })}
          tip="Applying..."
        >
          <div css={MenuBarWrapper}>
            <Popconfirm
              title={MSG_CONFIRM_CANCEL}
              onConfirm={() => history.goBack()}
            >
              <Button2 theme={'white'} style={MenuButton}>
                {MSG_CANCEL}
              </Button2>
            </Popconfirm>
            <Button2
              theme={'blue'}
              disabled={current !== getMaxStep({ type })}
              style={MenuButton}
              onClick={saveSetting}
            >
              {MSG_SAVE_SETTING}
            </Button2>
          </div>
          <div css={bodyFrame}>
            <Divider style={dividerStyle} />
            <div css={StepFrameStyle}>
              <Steps current={current} css={{ marginTop: '10px' }}>
                {(type === E_SINGLE_TYPE ? steps : multiSteps).map(
                  (item, idx) => {
                    return (
                      <Step
                        key={`STEP_${idx + 1}`}
                        title={
                          current === idx
                            ? MSG_PROGRESS
                            : current > idx
                            ? MSG_FINISHED
                            : MSG_WAITING
                        }
                        description={item.description}
                      />
                    );
                  },
                )}
              </Steps>
            </div>
            <Divider style={dividerStyle} />
            <div css={TitleFrameStyle}>
              <Button
                type="dashed"
                css={directionButton}
                onClick={PreviousOnClick}
                disabled={current === 0}
              >
                <LeftCircleFilled /> {MSG_PREVIOUS}
              </Button>
              <div
                css={{
                  textAlign: 'center',
                  fontSize: '24px',
                  lineHeight: '32px',
                }}
              >
                {type === E_SINGLE_TYPE
                  ? steps[current].description
                  : multiSteps[current].description}
              </div>
              <Button
                type="dashed"
                css={directionButton}
                onClick={nextButton}
                loading={loading && current !== getMaxStep({ type })}
                disabled={!nextStepValid() || current === steps.length - 1}
              >
                {MSG_NEXT} <RightCircleFilled />
              </Button>
            </div>
            <div css={ContentsFrameStyle}>
              <StepSetting.contents
                current={current}
                data={data}
                changeFunc={(e) => onChange(e)}
                type={type}
              />
            </div>
            <div css={PreviewFrameStyle}>
              <div
                css={PreviewTitleStyle}
                style={{ fontWeight: '500', textTransform: 'uppercase' }}
              >
                {MSG_PREVIEW}
                {current === getVisualStep({ type }) ? (
                  <Button
                    type="dashed"
                    icon={<LineChartOutlined />}
                    disabled={!!addGraphData?.row}
                    onClick={() => setIsAddOpen(true)}
                  >
                    Add Graph
                  </Button>
                ) : (
                  <Button
                    type="dashed"
                    icon={<ReadFilled />}
                    disabled={!Enable_Preview()}
                    onClick={previewOnClick}
                  >
                    {MSG_PREVIEW}
                  </Button>
                )}
              </div>
              <Divider
                height={'1'}
                type={'solid'}
                style={{ marginBottom: '0' }}
              />
              <div
                css={[
                  ContentsFrameStyle,
                  current === getVisualStep({ type }) ? graphFrameStyle : '',
                ]}
              >
                <StepSetting.preview
                  current={current}
                  data={data}
                  type={type}
                />
              </div>
            </div>
          </div>
        </Spin>
      </div>
      {current === getVisualStep({ type }) ? (
        <GraphAddEdit
          data={addGraphData()}
          closer={() => setIsAddOpen(false)}
          isOpen={isAddOpen}
        />
      ) : (
        ''
      )}
    </>
  );
};
export default JobStep;
