import React, { useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';
import { Modal } from '../atoms/Modal';
import Button from '../atoms/Button';
import { css } from '@emotion/react';
import { Spin, Progress, List, Avatar } from 'antd';
import {
  ClockCircleOutlined,
  LoadingOutlined,
  PaperClipOutlined,
} from '@ant-design/icons';
import { E_MULTI_TYPE } from '../../../lib/api/Define/etc';
import StatusTag from '../atoms/StatusTag/StatusTag';

const contentStyle = css`
  display: block;
`;

const gridContentWrapper = css`
  display: grid;
  grid-template-columns: 1fr 1fr;
  justify-items: center;
  & > div > div:last-of-type > p {
    margin-bottom: 0;
  }
  margin: 1rem 0;
`;

const ProcessIconStyle = css`
  display: flex;
  align-items: center;
  justify-contents: center;
`;

const footerStyle = css`
  display: flex;
  justify-content: flex-end;
  align-items: center;
`;
const useInterval = (callback, delay) => {
  const savedCallback = useRef();

  // Remember the latest callback.
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  // Set up the interval.
  useEffect(() => {
    if (delay !== null) {
      let id = setInterval(() => {
        savedCallback.current();
      }, delay);
      return () => clearInterval(id);
    }
  }, [delay]);
};
/*****************************************************************************
 *              Main Modal
 *****************************************************************************/

const ProgressModal = ({ isOpen, closeFunc, statusFunc, info }) => {
  const [status, setStatus] = useState('idle');
  const [percent, setPercent] = useState(0);
  const [contents, setContents] = useState(null);
  const [current, setCurrent] = useState(undefined);
  const total =
    info?.source_type === E_MULTI_TYPE
      ? info?.list.length
      : contents?.total_files ?? 0;
  const completed = contents?.error_files ?? 0 + contents?.success_files ?? 0;
  const status_msg =
    status === 'error' ||
    (info?.source_type !== E_MULTI_TYPE &&
      total > 0 &&
      completed === total &&
      contents?.converted === 0)
      ? 'ERROR'
      : status === 'success'
      ? 'COMPLETE'
      : 'PROCESS';

  useInterval(
    () => {
      // Your custom logic here
      info?.source_type === E_MULTI_TYPE
        ? statusFunc(setStatus, setCurrent, current)
        : statusFunc(setStatus, setPercent, setContents);
    },
    isOpen && status_msg === 'PROCESS' ? 1000 : null,
  );

  const closeModal = () => {
    closeFunc(status_msg, -1);
  };
  useEffect(() => {
    console.log('=======useEffect========');
    if (status === 'success') {
      closeFunc(status_msg, contents.converted);
    }
  }, [status, contents?.converted ?? undefined]);
  useEffect(() => {
    if (isOpen === false) {
      setContents(null);
      setPercent(0);
      setStatus('idle');
    }
  }, [isOpen]);
  if (isOpen === false) return <></>;

  return (
    <>
      <Modal
        isOpen={isOpen}
        header={<div>{status_msg}</div>}
        content={
          info?.source_type === E_MULTI_TYPE ? (
            <MultiJobContents list={info?.list ?? []} currentJob={current} />
          ) : (
            <Contents type={status_msg} percent={percent} contents={contents} />
          )
        }
        footer={
          <ModalFooter
            closeFunc={closeModal}
            btnText={
              status === 'success' || completed === total ? 'Close' : 'Cancel'
            }
          />
        }
        closeIcon={false}
      />
    </>
  );
};

ProgressModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  closeFunc: PropTypes.func.isRequired,
  statusFunc: PropTypes.func.isRequired,
  info: PropTypes.object,
};

/*****************************************************************************
 *              Modal Contents
 *****************************************************************************/
const ErrorContents = css`
  flex: none;
  order: 0;
  flex-grow: 1;
  margin: 0px 10px;
`;

const ItemDiv = css`
  color: rgba(0, 0, 0, 0.65);
  font-size: 14px;
  & > p {
    margin-right: 0.5rem;
  }
`;

const ItemLabel = css`
  display: inline-block;
  color: rgba(0, 0, 0, 0.85);
  margin-left: 1rem;
`;

const Contents = ({ type, percent, contents }) => {
  if (!!contents === false) {
    const antIcon = <LoadingOutlined style={{ fontSize: 24 }} spin />;
    return (
      <div css={contentStyle}>
        <div css={ErrorContents}>
          <div css={ItemDiv}>
            <Spin indicator={antIcon} />
            <div css={ItemLabel}>File uploading</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div css={gridContentWrapper}>
      <div>
        <div css={ItemDiv}>
          <p css={ItemLabel}>Error Files:</p>
          {contents.error_files}
        </div>
        <div css={ItemDiv}>
          <p css={ItemLabel}>Success Files:</p>
          {contents.success_files}
        </div>
        <div css={ItemDiv}>
          <p css={ItemLabel}>Total Files:</p>
          {contents.total_files}
        </div>
        <div css={ItemDiv}>
          <p css={ItemLabel}>Converted rows:</p>
          {contents.converted}
        </div>
      </div>
      {type === 'COMPLETE' ? (
        <Progress type="circle" percent={100} css={ProcessIconStyle} />
      ) : type === 'PROCESS' ? (
        <Progress type="circle" percent={percent} css={ProcessIconStyle} />
      ) : (
        <Progress
          type="circle"
          percent={percent}
          status="exception"
          css={ProcessIconStyle}
        />
      )}
    </div>
  );
};
Contents.propTypes = {
  type: PropTypes.string,
  percent: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  contents: PropTypes.object,
};

const MultiJobContents = ({ list, currentJob }) => {
  console.log('list', list);
  console.log('currentJob', currentJob);
  return (
    <div style={{ minWidth: '550px' }}>
      <List
        itemLayout="horizontal"
        dataSource={list ?? []}
        css={{ maxHeight: '300px' }}
        renderItem={(item) => (
          <List.Item>
            <List.Item.Meta
              avatar={<Avatar icon={<PaperClipOutlined />} />}
              title={`${item?.source}`}
              description={
                <div>
                  <span css={{ padding: '0px 4px' }}>
                    {item?.source_type ?? ''
                      ? `Source: ${item.source_type}`
                      : ''}
                  </span>
                </div>
              }
            />
            <div style={{ width: '80px' }}>
              {item?.rid ?? false ? (
                <StatusTag status={'success'} />
              ) : item.source === currentJob ? (
                <StatusTag status={'processing'} />
              ) : (
                <StatusTag
                  status={'waiting'}
                  color={'warning'}
                  icon={<ClockCircleOutlined />}
                />
              )}
            </div>
          </List.Item>
        )}
      />
    </div>
  );
};
MultiJobContents.propTypes = {
  list: PropTypes.array,
  currentJob: PropTypes.string,
};

/*****************************************************************************
 *              Modal Footer
 *****************************************************************************/

const ModalFooter = ({ btnText, closeFunc }) => {
  return (
    <div css={footerStyle}>
      <Button
        theme={'blue'}
        onClick={closeFunc}
        style={{ marginLeft: '8px', fontWeight: 400 }}
      >
        {btnText ? btnText : 'Close'}
      </Button>
    </div>
  );
};

ModalFooter.propTypes = {
  btnText: PropTypes.string,
  closeFunc: PropTypes.func.isRequired,
};

export default ProgressModal;
