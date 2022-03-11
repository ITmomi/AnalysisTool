import React, { useCallback, useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import dayjs from 'dayjs';
import { Button, Checkbox, Input, Select, DatePicker } from 'antd';
import { SettingOutlined, SyncOutlined } from '@ant-design/icons';
import { useLocation } from 'react-router';
import { displayNotification, createAnalysisData } from '../../functionGroup';
import { default as Btn } from '../../../../UI/atoms/Button';
import useResultInfo from '../../../../../hooks/useResultInfo';
import { DATE_FORMAT } from '../../../../../lib/api/Define/etc';
import { getAnalysisData } from '../../../../../lib/api/axios/requests';
import * as fn from '../functionGroup';
import * as sg from '../styleGroup';

const HeaderSetting = ({
  period,
  filter,
  aggregation,
  type,
  loadingSet,
  useUpdate,
}) => {
  const { func_id, job_id } = useLocation().state;
  const {
    originalData,
    analysisData,
    setAnalysisInfo,
    setOriginalInfo,
    setOriginalFilteredRows,
    setSavedAnalysisAggregation,
  } = useResultInfo();
  const [periodVal, setPeriodVal] = useState(['', '']);
  const [showPopup, setShowPopup] = useState(false);
  const [filterVal, setFilterVal] = useState({});
  const [aggregationVal, setAggregationVal] = useState({});
  const [beforeInfo, setBeforeInfo] = useState({
    filter: {},
    aggregation: {},
  });

  const closeRangePicker = () => {
    if (showPopup) {
      setShowPopup(false);
    }
  };

  const closePopup = () => {
    setShowPopup(false);
    setFilterVal(beforeInfo.filter);
    setAggregationVal(beforeInfo.aggregation);
  };

  const changeFilter = (key, val) => {
    setFilterVal((prevState) => {
      return {
        ...prevState,
        [key]: val,
      };
    });
  };

  const changeAggregation = (key, val) => {
    setAggregationVal((prevState) => {
      if (key === 'main' && val.toLowerCase().indexOf('all') === -1) {
        return {
          main: val,
          sub: aggregation.subItem[val].selected,
        };
      } else {
        return {
          ...prevState,
          [key]: val,
        };
      }
    });
  };

  const changeAll = (key, index) => {
    if (filterVal[key] === undefined) {
      changeFilter(key, filter[index].options);
    } else {
      filterVal[key].length === filter[index].options.length
        ? changeFilter(key, [])
        : changeFilter(key, filter[index].options);
    }
  };

  const changePeriod = (date) => {
    setPeriodVal(date);
  };

  const applyFilter = async () => {
    let description = '';

    setShowPopup(false);
    loadingSet(true);

    if (type === 'analysis' || useUpdate) {
      let isAggError = false;

      if (
        Object.keys(aggregation).length > 0 &&
        aggregationVal.main.indexOf('all') === -1 &&
        (aggregationVal.sub === null || aggregationVal.sub === '')
      ) {
        isAggError = true;
      }

      if (isAggError) {
        displayNotification({
          message: 'Filter Setting Error',
          description:
            'There are some items that have not been set yet. Please check the item.',
          duration: 3,
          style: { borderLeft: '5px solid red' },
        });
      } else {
        const param = {
          fId: func_id,
          rId: job_id,
          start:
            periodVal === null || periodVal[0].length === 0
              ? period.start
              : periodVal[0].format(DATE_FORMAT),
          end:
            periodVal === null || periodVal[1].length === 0
              ? period.end
              : periodVal[1].format(DATE_FORMAT),
          agMain: aggregationVal.main,
          agSub: aggregationVal.sub,
          filter: filterVal,
        };

        const { data, option, message } = await getAnalysisData(
          param,
          analysisData.type,
        );

        if (message === '') {
          setOriginalFilteredRows({});
          setOriginalInfo({
            period: {},
            filter: [],
            aggregation: {},
            dispOrder: [],
            dispGraph: [],
            data: {},
          });
          setAnalysisInfo({
            ...analysisData,
            period: option.period,
            filter: option.filter,
            aggregation: option.aggregation ?? {},
            dispOrder: createAnalysisData(
              analysisData.type,
              data,
              'disp_order',
            ),
            dispGraph: createAnalysisData(
              analysisData.type,
              data,
              'disp_graph',
            ),
            data: createAnalysisData(analysisData.type, data, 'row'),
          });
        } else {
          description = message;
        }
      }
    } else {
      setOriginalFilteredRows(
        fn.createGraphData(
          originalData.data,
          filterVal,
          !Array.isArray(originalData.dispOrder),
        ),
      );
    }

    setBeforeInfo({
      filter: filterVal,
      aggregation: aggregationVal,
    });

    loadingSet(false);

    if (description !== '') {
      displayNotification({
        message: 'Update failed',
        description: description,
        duration: 3,
        style: { borderLeft: '5px solid red' },
      });
    }
  };

  const disabledDate = useCallback(
    (v) => {
      return Object.keys(period).length === 0
        ? false
        : v &&
            (dayjs(v).isBefore(dayjs(period.start), 'd') ||
              dayjs(v).isAfter(dayjs(period.end), 'd'));
    },
    [JSON.stringify(period)],
  );

  useEffect(() => {
    setPeriodVal(fn.initPeriod(period));
  }, [period]);

  useEffect(() => {
    const newFilter = fn.initFilterValue(filter);
    setFilterVal(newFilter);
    setBeforeInfo((prevState) => {
      return {
        ...prevState,
        filter: newFilter,
      };
    });
  }, [filter]);

  useEffect(() => {
    const newAgg = fn.initAggregation(aggregation);
    setAggregationVal(newAgg);
    setBeforeInfo((prevState) => {
      return {
        ...prevState,
        aggregation: newAgg,
      };
    });
    if (type === 'analysis') {
      setSavedAnalysisAggregation(newAgg);
    }
  }, [aggregation]);

  useEffect(() => {
    return () => {
      if (type !== 'analysis') {
        setOriginalFilteredRows({});
        setOriginalInfo({});
      }
      return null;
    };
  }, []);

  return (
    <div className="header-wrapper">
      <div className="popup-wrapper">
        <span>Period:</span>
        <DatePicker.RangePicker
          value={periodVal}
          onOpenChange={closeRangePicker}
          onChange={changePeriod}
          disabledDate={disabledDate}
          disabled={!useUpdate}
          showTime
          placeholder={[period.start, period.end]}
          inputReadOnly
          allowClear={false}
        />
        {filter !== undefined &&
        filter.length === 0 &&
        aggregation !== undefined &&
        Object.keys(aggregation).length === 0 ? (
          ''
        ) : (
          <>
            <div className="filter-component">
              <Button
                type="dashed"
                shape="circle"
                icon={<SettingOutlined />}
                onClick={() => setShowPopup(true)}
              />
              <div>Filter Setting</div>
              <div
                css={[
                  sg.popupBackground,
                  showPopup ? { display: 'block' } : '',
                ]}
                onClick={() => closePopup()}
                onKeyDown={() => closePopup()}
                role="button"
                tabIndex="0"
              />
              <div css={[sg.popupStyle, showPopup ? { display: 'block' } : '']}>
                <div>Filter Setting</div>
                <div>
                  {Array.isArray(filter) &&
                    filter.map((v, i) => {
                      return (
                        <div key={v.target}>
                          <div>{v.title + ':'}</div>
                          <div css={sg.selectWrapper}>
                            <Select
                              mode={v.mode === 'plural' ? 'multiple' : ''}
                              showArrow
                              maxTagCount="responsive"
                              value={filterVal[v.target]}
                              onChange={(val) => changeFilter(v.target, val)}
                              style={{ fontSize: '12px', width: '100%' }}
                            >
                              {v.options.map(fn.RenderSelectOptions)}
                            </Select>
                            {v.mode === 'plural' ? (
                              <Checkbox
                                checked={
                                  filterVal[v.target] === undefined ||
                                  filterVal[v.target] === null
                                    ? false
                                    : filterVal[v.target].length ===
                                      filter[i].options.length
                                }
                                onChange={() => changeAll(v.target, i)}
                              >
                                All
                              </Checkbox>
                            ) : (
                              ''
                            )}
                          </div>
                        </div>
                      );
                    })}
                  {aggregation !== undefined &&
                  Object.keys(aggregation).length > 0 &&
                  Object.keys(aggregationVal).length > 0 ? (
                    <div>
                      <div>{aggregation.title + ':'}</div>
                      <div
                        css={
                          aggregationVal.main.toLowerCase().indexOf('all') !==
                          -1
                            ? sg.aggSingleItemWrapper
                            : sg.aggregationWrapper
                        }
                      >
                        <Select
                          value={aggregationVal.main}
                          style={{ fontSize: '12px', width: '100%' }}
                          onChange={(val) => changeAggregation('main', val)}
                        >
                          {aggregation.options.map(fn.RenderSelectOptions)}
                        </Select>
                        {aggregationVal.main.toLowerCase().indexOf('all') ===
                          -1 &&
                        aggregation.subItem[aggregationVal.main] !==
                          undefined ? (
                          aggregation.subItem[aggregationVal.main].type ===
                          'select' ? (
                            <Select
                              value={aggregationVal.sub}
                              style={{
                                fontSize: '12px',
                                width: '100%',
                                marginLeft: '0.5rem',
                              }}
                              onChange={(val) => changeAggregation('sub', val)}
                            >
                              {aggregation.subItem[
                                aggregationVal.main
                              ].options.map(fn.RenderSelectOptions)}
                            </Select>
                          ) : (
                            <Input
                              value={aggregationVal.sub}
                              style={{
                                fontSize: '12px',
                                marginLeft: '0.5rem',
                              }}
                              onChange={(e) =>
                                changeAggregation('sub', e.target.value)
                              }
                            />
                          )
                        ) : (
                          ''
                        )}
                      </div>
                    </div>
                  ) : (
                    ''
                  )}
                </div>
                <div>
                  <Button type="primary" onClick={applyFilter}>
                    {type === 'analysis' || useUpdate ? 'Save' : 'Apply'}
                  </Button>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
      <div>
        {type === 'analysis' || useUpdate ? (
          <Btn
            theme="white"
            style={{ fontWeight: 'normal' }}
            onClick={applyFilter}
          >
            <SyncOutlined /> Update
          </Btn>
        ) : (
          ''
        )}
      </div>
    </div>
  );
};

HeaderSetting.displayName = 'HeaderSetting';
HeaderSetting.propTypes = {
  period: PropTypes.object.isRequired,
  filter: PropTypes.array.isRequired,
  aggregation: PropTypes.object,
  type: PropTypes.string.isRequired,
  loadingSet: PropTypes.func,
  useUpdate: PropTypes.bool.isRequired,
};

export default HeaderSetting;
