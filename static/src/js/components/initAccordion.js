import '../plugins/accordionPlugin';

// accordion menu init
export default function initAccordion() {
  jQuery('.monthly-accordion').slideAccordion({
    opener: '.monthly-accordion-opener',
    slider: '.monthly-accordion-slide',
    animSpeed: 300,
    activeClass: 'monthly-accordion-active',
    scrollToActiveItem: {
      enable: true,
      extraOffset: 0,
    },
  });
  jQuery('.stock-accordion').slideAccordion({
    opener: '.stock-accordion-opener',
    slider: '.stock-accordion-slide',
    animSpeed: 300,
    activeClass: 'stock-accordion-active',
    scrollToActiveItem: {
      enable: true,
      extraOffset: 0,
    },
  });
}
