import initMobileNav from "./components/initMobileNav.js";
import initOpenClose from "./components/initOpenClose.js";
import initFixedHeader from "./components/initFixedHeader";
import initPopups from "./components/initPopups";
import initTooltip from "./components/initTooltip";

document.addEventListener('DOMContentLoaded', () => {
  document.documentElement.classList.add("is-loaded");
  initMobileNav();
  initOpenClose();
  initFixedHeader();
  initPopups();
  initTooltip();
});
