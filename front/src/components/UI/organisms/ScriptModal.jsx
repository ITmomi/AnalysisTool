import React, { useCallback, useEffect, useState } from 'react';
import { Modal } from 'antd';
import styled from '@emotion/styled';
import PropTypes from 'prop-types';
import AceEditor from 'react-ace';
import 'ace-builds/src-min-noconflict/ext-language_tools';
import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/snippets/python';
import 'ace-builds/src-noconflict/theme-tomorrow';
import pythonLogo from '../../../static/python_icon.svg';

const StyledEditor = styled.div`
  margin-top: 10px;
  * {
    font-family: consolas;
    line-height: 1;
  }
`;

export const ScriptEdit = ({
  title,
  target,
  visible,
  setVisible,
  script,
  onChangeScript,
}) => {
  const [code, setCode] = useState('');
  const onChange = (value) => {
    setCode(value);
  };
  const onClose = useCallback(() => {
    setVisible(false);
  }, [setVisible]);
  const onOk = useCallback(() => {
    onChangeScript({ [target]: code || null });
    setVisible(false);
  }, [onChangeScript, setVisible, code]);
  useEffect(() => {
    setCode(script ?? '');
  }, [script]);
  useEffect(() => {
    visible === true ? setCode(script) : setCode('');
  }, [visible]);
  return (
    <Modal
      title={
        <div style={{ fontWeight: 700 }}>
          <img src={pythonLogo} alt={'Python Code'} /> {title}
        </div>
      }
      visible={visible}
      onOk={onOk}
      onCancel={onClose}
      width={600}
      destroyOnClose
    >
      <StyledEditor>
        <AceEditor
          placeholder="Input Python Code Here!"
          mode="python"
          theme="tomorrow"
          width={'552px'}
          onChange={onChange}
          fontSize={14}
          showPrintMargin={true}
          showGutter={true}
          highlightActiveLine={true}
          value={code ?? undefined}
          setOptions={{
            enableLiveAutocompletion: true,
            enableSnippets: false,
            showLineNumbers: true,
            tabSize: 4,
          }}
          enableSnippets={true}
        />
      </StyledEditor>
    </Modal>
  );
};

ScriptEdit.propTypes = {
  title: PropTypes.string,
  target: PropTypes.string,
  visible: PropTypes.bool,
  setVisible: PropTypes.func,
  script: PropTypes.string,
  onChangeScript: PropTypes.func,
};
