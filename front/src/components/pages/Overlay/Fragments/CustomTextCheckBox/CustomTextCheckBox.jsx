import React from 'react';
import PropTypes from 'prop-types';
import { getParseData } from '../../../../../lib/util/Util';

const CustomTextCheckBox = ({
  value,
  isChecked,
  disabled,
  id,
  useText,
  label,
  onText,
  offText,
  changeFunc,
}) => {
  const ValueChangeFunc = (e) => {
    const data = getParseData(e);
    if (data.id === 'value') {
      changeFunc(e);
    } else {
      if (data.id === 'mode') {
        changeFunc({ mode: data.value ? onText : offText });
      } else {
        changeFunc(e);
      }
    }
  };
  return !useText ? (
    <label htmlFor={id} className="only-checkbox">
      <input
        type="checkbox"
        id={id}
        checked={isChecked}
        onChange={() => ValueChangeFunc({ mode: !isChecked })}
      />
      <div>{label}</div>
      <div className="mode-slider-wrapper">
        <div className="slider">
          <span>{offText}</span>
          <span>{onText}</span>
        </div>
      </div>
    </label>
  ) : (
    <div className="text-checkbox">
      <input
        type="text"
        value={value}
        onChange={(e) => ValueChangeFunc({ value: e.target.value })}
        readOnly={!isChecked || disabled}
      />
      <label htmlFor={id}>
        <input
          type="checkbox"
          id={id}
          checked={isChecked}
          onChange={() => ValueChangeFunc({ checked: !isChecked })}
        />
        <div className="svg-wrapper">
          <svg viewBox="0 1 21 21">
            <polyline points="5 10.75 8.5 14.25 14 7.8" />
          </svg>
        </div>
      </label>
    </div>
  );
};
CustomTextCheckBox.propTypes = {
  value: PropTypes.string,
  isChecked: PropTypes.bool,
  disabled: PropTypes.bool,
  id: PropTypes.string.isRequired,
  useText: PropTypes.bool,
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onText: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  offText: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  changeFunc: PropTypes.func,
};
CustomTextCheckBox.defaultProps = {
  value: '',
  isChecked: false,
  disabled: false,
  useText: false,
  onText: 'on',
  offText: 'off',
};

export default CustomTextCheckBox;
