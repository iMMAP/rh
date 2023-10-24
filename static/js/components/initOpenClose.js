import '../plugins/openClosePlugin';

// accordion menu init
export default function initOpenClose() {
  jQuery('.js-main-nav-openclose').openClose({
    activeClass: 'active',
    opener: '.openclose-opener',
    slider: '.inner-drop',
    animSpeed: 400,
    hideOnClickOutside: true,
    effect: 'slide',
  });
}
