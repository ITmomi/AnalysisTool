import React from 'react';
import { Tabs } from 'antd';
import PropTypes from 'prop-types';

const { TabPane } = Tabs;

const SelectTab = ({ list, selected, changeEvent }) => {
  return (
    <div>
      <Tabs onChange={changeEvent} type="card" activeKey={selected}>
        {list.map((tab) => (
          <TabPane tab={`Axis : ${tab}`} key={tab} />
        ))}
      </Tabs>
    </div>
  );
};
SelectTab.propTypes = {
  list: PropTypes.array,
  selected: PropTypes.string,
  changeEvent: PropTypes.func,
};
export default SelectTab;
