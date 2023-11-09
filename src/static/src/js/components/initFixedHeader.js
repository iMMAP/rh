// initialize fixed blocks on scroll
export default function initFixedHeader() {
  const headerHeight = $('#header').outerHeight();
  const wrapper = $('.wrapper-inner');
  const init = () => {
    if ($(window).scrollTop() >= 0.1) {
      $('body').addClass('fixed-header');
      jQuery(wrapper).css('padding-top', `${headerHeight}px`);
    } else {
      $('body').removeClass('fixed-header');
      jQuery(wrapper).css('padding-top', '');
    }
  };
  $(window).scroll(() => {
    init();
  });
  init();
}
