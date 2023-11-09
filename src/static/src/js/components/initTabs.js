import '../plugins/tabsPlugin';

export default function initTabs() {
  jQuery('.js-tabs-nav').tabset({
    tabLinks: 'a',
    defaultTab: true,
    addToParent: true,
  });
}
