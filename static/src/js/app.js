import 'simplebar';
import ResizeObserver from 'resize-observer-polyfill';
import ready, { HTML } from './utils';
import './utils/responsiveHelper';
import initVhHeight from './utils/vh';
import initDropDownClasses from './utils/hasDropClasses';
import initMobileNav from './components/initMobileNav.js';
import initOpenClose from './components/initOpenClose.js';
import initFixedHeader from './components/initFixedHeader';
import initPopups from './components/initPopups';
import initCustomSelect from './components/initCustomSelect';
import initTabs from './components/initTabs';
import initCollapsibleTable from './components/initCollapsibleTable';
import initCheckAllCheckboxes from './components/initCheckAllCheckboxes';
import initShowHideInputValue from './components/initShowHideInputValue';
import initCopyInputValue from './components/initCopyInputValue';
import initAccordion from './components/initAccordion';
import initTooltip from './components/initTooltip';
import initExportAndSW from './utils/exportSW';


ready(() => {
  window.ResizeObserver = ResizeObserver;
  HTML.classList.add('is-loaded');
  initVhHeight();
  initDropDownClasses();
  initMobileNav();
  initOpenClose();
  initFixedHeader();
  initPopups();
  initCustomSelect();
  initTabs();
  initCollapsibleTable();
  initCheckAllCheckboxes();
  initShowHideInputValue();
  initCopyInputValue();
  initAccordion();
  initTooltip();

  initExportAndSW();
});
