import useRuleSettingInfo from '../../../hooks/useRuleSettingInfo';
import React, { useEffect, useState } from 'react';
import { Collapse, Button } from 'antd';
import { SettingFilled } from '@ant-design/icons';
import { MSG_PREVIOUS_TABLE } from '../../../lib/api/Define/Message';
import PropTypes from 'prop-types';
import { css } from '@emotion/react';
import { E_SINGLE_TYPE, E_STEP_ANALYSIS } from '../../../lib/api/Define/etc';
import GraphManagement from '../../UI/organisms/GraphManagement/GraphManagement';
import Step5_Setting from './Step5_Setting';
import Step3_Multi_Setting from './MultiAnalysis/Step3_Setting';
import Step2_Multi_Setting from './MultiAnalysis/Step2_Setting';

const { Panel } = Collapse;

const tableWrapper = css`
  margin: 10px;
  display: flex;
  justify-content: center;
  & table {
    font-size: 14px;
  }
`;

const VisualSetting = ({ data, type }) => {
  const { ruleStepConfig, funcStepInfo } = useRuleSettingInfo();
  const [isOpen, setIsOpen] = useState(false);
  const [config, setConfig] = useState(null);

  useEffect(() => {
    console.log('[STEP6]data: ', data);
    const configData =
      ruleStepConfig.find((item) => item.step === E_STEP_ANALYSIS)?.data ?? {};

    setConfig({
      row: configData?.row ?? {},
    });
  }, []);

  if (config === null) return <></>;
  return (
    <>
      <div css={{ width: '100%', minWidth: '75%', paddingBottom: '0.9rem' }}>
        <Collapse defaultActiveKey={[1]}>
          <Panel header={MSG_PREVIOUS_TABLE} key="1">
            <div css={tableWrapper}>
              {type === E_SINGLE_TYPE ? (
                <Step5_Setting.view_preview data={data} />
              ) : funcStepInfo.use_org_analysis === false ? (
                <Step3_Multi_Setting.view_preview data={data} />
              ) : (
                <Step2_Multi_Setting.view_preview data={data} type={type} />
              )}
            </div>
          </Panel>
        </Collapse>
      </div>
      <div css={{ width: '100%' }}>
        <Button
          icon={<SettingFilled />}
          shape="round"
          type="primary"
          onClick={() => setIsOpen(true)}
        >
          User Graph Management
        </Button>
      </div>
      <GraphManagement closer={() => setIsOpen(false)} isOpen={isOpen} />
    </>
  );
};

VisualSetting.propTypes = {
  data: PropTypes.object,
  type: PropTypes.string,
};
export default VisualSetting;
