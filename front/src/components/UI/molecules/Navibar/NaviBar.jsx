import React, { useEffect, useState } from 'react';
import { Menu } from 'antd';
import { HomeOutlined } from '@ant-design/icons';
import SubMenu from 'antd/es/menu/SubMenu';
import { css } from '@emotion/react';
import { useHistory } from 'react-router';
import useCommonJob from '../../../../hooks/useBasicInfo';
import { arrayUnshift } from '../../../../lib/util/Util';
import { MAIN, OVERLAY } from '../../../../lib/api/Define/URL';
import { fixedTopMenu } from '../../../../lib/api/Define/FixedMenu';
import PropTypes from 'prop-types';

const MainBoxCss = css`
  background: #061178;
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
  border-radius: 26px 26px 10px 10px;
  display: flex;
  flex-wrap: no-wrap;
  justify-content: center;
  .ant-menu.ant-menu-dark .ant-menu-sub {
    background: #061178 !important;
  }
  & li {
    &:hover {
      background-color: rgba(24, 144, 255, 0.8);
    }
  }
  .ant-menu-dark.ant-menu-horizontal > .ant-menu-item:hover {
    background-color: rgba(24, 144, 255, 0.8);
  }
  .ant-menu-submenu-selected {
    background-color: #1890ff;
  }
`;

const MenuItemCss = css`
  padding: 0 4.5rem !important;
  &:hover {
    background-color: rgba(24, 144, 255, 0.8);
  }
`;

const Navibar_MenuItem = ({ title, keys, disable, icon }) => {
  console.log('Navibar_MenuItem', keys);
  console.log('Navibar_MenuItem', title);
  return (
    <Menu.Item
      key={keys ?? title}
      disabled={disable ?? false}
      css={MenuItemCss}
      icon={icon ?? undefined}
    >
      {title}
    </Menu.Item>
  );
};
Navibar_MenuItem.propTypes = {
  title: PropTypes.string,
  keys: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  disable: PropTypes.bool,
  icon: PropTypes.node,
};

const Navibar_SubMenuItem = ({ title, keys, sublist }) => {
  return (
    <SubMenu title={title} css={MenuItemCss}>
      {sublist.map((submenu) => {
        return (
          <Navibar_MenuItem
            keys={submenu.func_id}
            title={submenu.title}
            key={keys}
          />
        );
      })}
    </SubMenu>
  );
};
Navibar_SubMenuItem.propTypes = {
  title: PropTypes.string,
  keys: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  sublist: PropTypes.array,
};

const NaviBar = () => {
  const [current, setCurrent] = useState([MAIN]);
  const [naviBar, setNaviBar] = useState(undefined);
  const history = useHistory();
  const { currentPath, setCurrentPath, supportUrl, MenuInfo } = useCommonJob();
  useEffect(() => {
    if (supportUrl.length > 0) {
      const findObj = currentPath.find((obj) =>
        supportUrl.find((obj2) => obj2.func === obj),
      );
      if (findObj !== undefined) setCurrent(findObj);
      else setCurrent(currentPath[0]);
    }
    console.log('[useEffect]current', current);
    console.log('[useEffect]supportUrl', supportUrl);
  }, [currentPath, supportUrl]);

  useEffect(() => {
    console.log('naviBar update');
    setNaviBar(MenuInfo.navibar);
  }, [MenuInfo]);

  const handleClick = (e) => {
    console.log('handleClick', e);
    if (e) {
      if (e.key === MAIN) {
        if (currentPath[0] !== e.key || history.location !== MAIN) {
          history.location !== MAIN ? history.replace(MAIN) : '';
          currentPath[0] !== e.key ? setCurrentPath([MAIN]) : '';
        }
      } else {
        setCurrentPath(
          arrayUnshift(
            currentPath,
            parseInt(e.key).toString() !== 'NaN' ? parseInt(e.key) : e.key,
          ),
        );
        if (e.key.includes([OVERLAY])) {
          history.push({ pathname: e.key });
        }
      }
    }
  };
  if (naviBar === undefined) return <></>;
  return (
    <div css={MainBoxCss}>
      <Menu
        theme="dark"
        mode="horizontal"
        style={{ background: 'transparent' }}
        onClick={(e) => handleClick(e)}
        selectedKeys={current}
      >
        <Menu.Item key={MAIN} icon={<HomeOutlined />} css={MenuItemCss}>
          HOME
        </Menu.Item>
        {fixedTopMenu.map((fixed) => {
          return fixed.func.length > 0 ? (
            <SubMenu
              key={`fixed_${fixed?.title ?? 'menu'}`}
              css={MenuItemCss}
              title={fixed.title}
            >
              {fixed.func.map((submenu) => {
                return (
                  <Menu.Item
                    key={submenu.func_id}
                    css={MenuItemCss}
                    className="sub-menu-style"
                  >
                    {submenu.title}
                  </Menu.Item>
                );
              })}
            </SubMenu>
          ) : (
            <Navibar_MenuItem
              keys={`fixed_${fixed?.title ?? 'menu'}`}
              disable={true}
            />
          );
        })}
        {naviBar.map((menu) => {
          return menu.func && menu.func.length > 0 ? (
            <SubMenu
              key={`${menu.category_id}_${menu.title}`}
              title={menu.title}
              css={MenuItemCss}
            >
              {menu.func.map((submenu) => {
                return (
                  <Menu.Item
                    key={submenu.func_id}
                    css={MenuItemCss}
                    className="sub-menu-style"
                  >
                    {submenu.title}
                  </Menu.Item>
                );
              })}
            </SubMenu>
          ) : (
            <Menu.Item
              key={`${menu.category_id}_${menu.title}`}
              disabled
              css={MenuItemCss}
            >
              {menu.title}
            </Menu.Item>
          );
        })}
      </Menu>
    </div>
  );
};

export default NaviBar;
