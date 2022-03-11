import React, { useState } from 'react';
import { Button, Upload } from 'antd';
import * as SG from '../styleGroup';
import { UploadOutlined } from '@ant-design/icons';
import { MSG_JOB_FILE_UPLOAD } from '../../../../../lib/api/Define/Message';
import useOverlayResultInfo from '../../../../../hooks/useOverlayResultInfo';
import PropTypes from 'prop-types';
import { CPVS_MODE } from '../../../../../lib/api/Define/OverlayDefault';
import { NotificationBox } from '../../../../UI/molecules/NotificationBox';

const JobFileUpload = ({ mode, obj }) => {
  const [uploading, setUploading] = useState(false);
  const { jobFileUpload } = useOverlayResultInfo();

  const props = {
    multiple: false,
    maxCount: 1,
    action: '',
    customRequest: ({ file, onProgress, onError, onSuccess }) => {
      const formData = new FormData();
      formData.append('file', file);
      setUploading(true);
      const shot_list = Object.keys(obj.shots);
      onProgress({ percent: 50 }, file);
      jobFileUpload(shot_list, mode, formData)
        .then(() => onSuccess(file))
        .catch((e) => {
          console.log(e);
          NotificationBox('ERROR', e.message, 0);
          onError(file);
        })
        .finally(setUploading(false));
    },
    onChange: ({ file }) => {
      console.log(file);
    },
  };
  return (
    <div css={SG.contentItemStyle} className="column-3">
      <span className="label">{MSG_JOB_FILE_UPLOAD}</span>
      <Upload {...props}>
        <Button
          icon={<UploadOutlined />}
          loading={uploading}
          disabled={obj.mode === CPVS_MODE.FROM_LOG}
        >
          {uploading ? 'uploading' : 'Start Upload'}
        </Button>
      </Upload>
    </div>
  );
};
JobFileUpload.propTypes = {
  mode: PropTypes.string,
  obj: PropTypes.object,
};

export default JobFileUpload;
