import '../plugins/accordionPlugin.js';

// accordion menu init
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
jQuery('.activity-acc-accordion').slideAccordion({
  opener: '.activity-acc-accordion-opener',
  slider: '.activity-acc-accordion-slide',
  animSpeed: 300,
  activeClass: 'activity-acc-accordion-active',
  scrollToActiveItem: {
    enable: true,
    extraOffset: 0,
  },
});
jQuery('.target-location-accordion').slideAccordion({
  opener: '.target-location-accordion-opener',
  slider: '.target-location-accordion-slide',
  animSpeed: 300,
  activeClass: 'target-location-accordion-active',
  scrollToActiveItem: {
    enable: true,
    extraOffset: 0,
  },
});
jQuery('.disaggregation-accordion').slideAccordion({
  opener: '.disaggregation-accordion-opener',
  slider: '.disaggregation-accordion-slide',
  animSpeed: 300,
  activeClass: 'disaggregation-accordion-active',
  scrollToActiveItem: {
    enable: true,
    extraOffset: 0,
  },
});

jQuery('.project-activity-accordion').slideAccordion({
  opener: '.project-activity-accordion-opener',
  slider: '.project-activity-accordion-slide',
  animSpeed: 300,
  activeClass: 'project-activity-accordion-active',
  scrollToActiveItem: {
    enable: true,
    extraOffset: 0,
  },
});
