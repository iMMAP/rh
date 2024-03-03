import ResizeObserver from "resize-observer-polyfill";
import ready, { HTML } from "./utils";
import "./utils/responsiveHelper";
import initVhHeight from "./utils/vh";
import initDropDownClasses from "./utils/hasDropClasses";
import initMobileNav from "./components/initMobileNav.js";
import initOpenClose from "./components/initOpenClose.js";
import initFixedHeader from "./components/initFixedHeader";
import initPopups from "./components/initPopups";
import initTabs from "./components/initTabs";
import initCollapsibleTable from "./components/initCollapsibleTable";
import initCheckAllCheckboxes from "./components/initCheckAllCheckboxes";
import initShowHideInputValue from "./components/initShowHideInputValue";
import initCopyInputValue from "./components/initCopyInputValue";
import initAccordion from "./components/initAccordion";
import initTooltip from "./components/initTooltip";
// import initExport from './utils/export';
import initSWPopup from './utils/sweatalertPopups';
// import initExportSW from './utils/exportSW';

import * as Sentry from "@sentry/browser";



ready(() => {
  window.ResizeObserver = ResizeObserver;
  HTML.classList.add("is-loaded");
  initVhHeight();
  initDropDownClasses();
  initMobileNav();
  initOpenClose();
  initFixedHeader();
  initPopups();
  initTabs();
  initCollapsibleTable();
  initCheckAllCheckboxes();
  initShowHideInputValue();
  initCopyInputValue();
  initAccordion();
  initTooltip();
  // initExportSW();
  // initExport();
  initSWPopup();


  // Sentry feedback form
  Sentry.init({
    dsn: "https://c2be26cb81341d42992ae0ad9b338f9b@o4506381004701696.ingest.sentry.io/4506381006667776",
  
    integrations: [
      new Sentry.Feedback({
        // Additional SDK configuration goes in here, for example:
        colorScheme: "light",
      }),
    ],
  });


  const msgAlert = document.querySelector('.close-alert-message')
  if(msgAlert){
      msgAlert.addEventListener('click', function() {
          const msgContainer = document.querySelector('.message-container')
          if(msgContainer){
              msgContainer.style.display = 'none';
          }
      });
  }
});
