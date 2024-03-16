import ResizeObserver from "resize-observer-polyfill";
import ready, { HTML } from "./utils";
import "./utils/responsiveHelper";
import initVhHeight from "./utils/vh";
import initMobileNav from "./components/initMobileNav.js";
import initOpenClose from "./components/initOpenClose.js";
import initFixedHeader from "./components/initFixedHeader";
import initPopups from "./components/initPopups";
import initTooltip from "./components/initTooltip";
import initSWPopup from './utils/sweatalertPopups';
import initExportSW from './utils/exportSW.js';


ready(() => {
  window.ResizeObserver = ResizeObserver;
  HTML.classList.add("is-loaded");
  initVhHeight();
  initMobileNav();
  initOpenClose();
  initFixedHeader();
  initPopups();
  initTooltip();
  initSWPopup();
  initExportSW();

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
