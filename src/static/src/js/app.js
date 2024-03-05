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

import * as Sentry from "@sentry/browser";



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
