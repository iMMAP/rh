export default function initFixedHeader() {
    const headerHeight = document.querySelector('#header').offsetHeight;
    const wrapper = document.querySelector('.wrapper-inner');
    const init = () => {
      if (window.scrollY >= 0.1) {
        document.body.classList.add('fixed-header');
        wrapper.style.paddingTop = `${headerHeight}px`;
      } else {
        document.body.classList.remove('fixed-header');
        wrapper.style.paddingTop = '';
      }
    };

  window.addEventListener('scroll', () => {
    init();
  });

  init();
}
