import '../plugins/mobileNavPlugin';

// mobile menu init
export default function initMobileNav() {
  window.ResponsiveHelper.addRange({
    '..1023': {
      on: () => {
        jQuery('body').mobileNav({
          menuActiveClass: 'nav-active',
          menuOpener: '.mobile-menu-opener',
          hideOnClickOutside: true,
          menuDrop: '.mobile-menu-holder',
        });
      },
      off: () => {
        jQuery('body').mobileNav('destroy');
      },
    },
  });
}
