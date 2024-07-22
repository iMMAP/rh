((window, document) => {
  function vw() {
    const vw = document.documentElement.clientWidth;
    document.documentElement.style.setProperty('--vw', `${vw}px`);
  }

  vw();
  window.addEventListener('resize', vw);
})(window, document);