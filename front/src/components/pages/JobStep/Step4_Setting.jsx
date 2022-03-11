import React from 'react';
import PropTypes from 'prop-types';
import { css } from '@emotion/react';
import { Table } from 'antd';
import { AnyRegex, CommonRegex } from '../../../lib/util/RegExp';
import { getArray, getTableForm } from '../../../lib/util/Util';
import { postRequestJsonData } from '../../../lib/api/axios/requests';
import { SingleJobStepConf as steps } from '../../../hooks/useJobStepInfo';
import { E_STEP_4, E_STEP_5, R_OK } from '../../../lib/api/Define/etc';
import { NotificationBox } from '../../UI/molecules/NotificationBox';
import FilterSetting from './FilterSetting';
const tableWrapper = css`
  display: contents;
`;

const PreviewRequest = async ({ filterStepInfo, originLog, setData }) => {
  const filterTmp = [...filterStepInfo];

  const filterArr = getArray(filterTmp ?? [], false, false);

  if (originLog === undefined || originLog === null) {
    console.log('data is empty');
  } else {
    const obj = Object.assign(
      {},
      {
        data: {
          row: originLog.row,
          disp_order: originLog.disp_order,
        },
        filter: { items: filterArr },
      },
    );

    try {
      const { info, status } = await postRequestJsonData(
        steps[E_STEP_4].preview,
        undefined,
        obj,
      );
      console.log('info', info);
      console.log('status', status);
      if (status === R_OK) {
        if (info.result === true) {
          const tableData = getTableForm({ info: info.data, max_row: 5 });
          setData((prevState) => ({
            ...prevState,
            ['filter_header']: tableData.columns,
            ['filter_data']: tableData.dataSource,
            ['filter_error']: undefined,
          }));
          return { data: info.data, step: E_STEP_4 };
        } else {
          console.log('info.result === false');
          NotificationBox('error', info.err);
          return { data: undefined, step: undefined };
        }
      }
    } catch (e) {
      if (e.response) {
        const {
          data: { msg },
        } = e.response;
        console.log(e.response);
        NotificationBox('error', msg);
      }
    }
  }
};
const PreviewButtonEvent = ({ filterStepInfo, originLog, setData }) => {
  return PreviewRequest({
    filterStepInfo,
    originLog,
    setData,
  }).then((_) => _);
};

const PreviousButtonEvent = () => {};

const NextButtonEvent = async ({
  setLoading,
  filterStepInfo,
  data,
  originLog,
}) => {
  setLoading(true);
  if (EnableCheck(filterStepInfo) ?? false) {
    const result = await PreviewRequest({
      filterStepInfo,
      setData: data.func,
      originLog,
    }).then((_) => _);
    console.log('PreviewResult', result);
    if (result === undefined) {
      setLoading(false);
    }
    return {
      info: undefined,
      next: E_STEP_5,
      preview: { current: result.step, info: result.data },
    };
  } else {
    return {
      info: undefined,
      next: E_STEP_5,
      preview: undefined,
    };
  }
};
const EnableCheck = (filterStepInfo) => {
  const idVaildFilterName = Boolean(
    !filterStepInfo.filter((o) => CommonRegex.test(o.name) === false).length,
  );
  const idVaildFilterType = Boolean(
    !filterStepInfo.filter((o) => AnyRegex.test(o.type) === false).length,
  );
  const idVaildFilterCondition = Boolean(
    !filterStepInfo.filter((o) => AnyRegex.test(o.condition) === false).length,
  );

  return (
    (filterStepInfo?.length === 0 ?? true) ||
    (idVaildFilterName && idVaildFilterType && idVaildFilterCondition)
  );
};

const ContentsForm = ({ data }) => {
  return <FilterSetting data={data} />;
};
ContentsForm.propTypes = {
  data: PropTypes.object,
};
const PreviewForm = ({ data }) => {
  if (data == null) return <></>;

  const { filter_header, filter_data, filter_error } = data;

  if (
    filter_header === undefined &&
    filter_data === undefined &&
    filter_error === undefined
  )
    return <></>;

  return (
    <div css={tableWrapper}>
      {filter_error !== undefined ? (
        <>{filter_error}</>
      ) : (
        <Table
          bordered
          pagination={false}
          columns={filter_header}
          dataSource={filter_data}
          size="middle"
          rowKey="key"
          scroll={{ x: 'max-content' }}
        />
      )}
    </div>
  );
};
PreviewForm.propTypes = {
  data: PropTypes.object,
};
const Step4_Setting = ({ children }) => {
  return <div>{children}</div>;
};

Step4_Setting.propTypes = {
  children: PropTypes.node,
};
Step4_Setting.btn_next = NextButtonEvent;
Step4_Setting.btn_previous = PreviousButtonEvent;
Step4_Setting.btn_preview = PreviewButtonEvent;
Step4_Setting.check_next = EnableCheck;
Step4_Setting.check_preview = EnableCheck;

Step4_Setting.view_contents = ContentsForm;
Step4_Setting.view_preview = PreviewForm;

export default Step4_Setting;
