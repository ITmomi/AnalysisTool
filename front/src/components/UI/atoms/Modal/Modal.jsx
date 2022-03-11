import React from 'react';
import PropTypes from 'prop-types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTimes } from '@fortawesome/free-solid-svg-icons';
import { css } from '@emotion/react';
import { CSSTransition } from 'react-transition-group';

const Modal = ({
  isOpen,
  onClickBg,
  closeIcon,
  onClickIcon,
  width,
  header,
  content,
  footer,
  style,
}) => {
  return (
    <CSSTransition in={isOpen} timeout={100} classNames="modal" unmountOnExit>
      <>
        <div
          css={overlayStyle}
          onClick={onClickBg}
          onKeyDown={onClickBg}
          role="button"
          tabIndex={0}
        />
        <div css={[mainStyle, style]}>
          <div css={[headerStyle, { width }]}>
            <div>{header}</div>
            {closeIcon ? (
              <div
                css={iconStyle}
                onClick={onClickIcon}
                onKeyDown={onClickIcon}
                role="button"
                tabIndex={0}
              >
                <FontAwesomeIcon icon={faTimes} size="sm" />
              </div>
            ) : (
              ''
            )}
          </div>
          <div css={contentStyle}>{content}</div>
          <div css={footerStyle}>{footer}</div>
        </div>
      </>
    </CSSTransition>
  );
};

Modal.displayName = 'Modal';
Modal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClickBg: PropTypes.func,
  closeIcon: PropTypes.bool.isRequired,
  onClickIcon: PropTypes.func,
  width: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  header: PropTypes.node,
  content: PropTypes.node,
  footer: PropTypes.node,
  style: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
};
Modal.defaultProps = {
  header: 'header',
  content: 'content',
  footer: 'footer',
};

const overlayStyle = css`
  position: fixed;
  z-index: 1000;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.2);
  outline: none;
`;

const mainStyle = css`
  position: fixed;
  z-index: 1001;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  min-width: 400px;
  border-radius: 2px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.26);
`;

const headerStyle = css`
  font-size: 20px;
  font-weight: bold;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
`;

const contentStyle = css`
  padding: 1rem;
  & > div + div {
    margin-top: 1rem;
  }
`;

const footerStyle = css`
  padding: 1rem;
  border-top: 1px solid #f0f0f0;
`;

const iconStyle = css`
  outline: none;
  cursor: pointer;
  transition: color 0.2s;
  & {
    svg {
      color: #bfbfbf;
    }
    svg,
    path {
      cursor: pointer;
    }
  }
  &:hover {
    svg {
      color: #7b7b7b;
    }
  }
`;

export default Modal;
