import '../plugins/popupPlugin';

// popups init
export default function initPopups() {
  jQuery('.export-formats-holder').contentPopup({
    mode: 'click',
    popup: '.export-formats',
    btnOpen: '.export-open',
    btnClose: '.export-close',
    openClass: 'export-formats-active',
  });

  jQuery('.filter-holder, body').contentPopup({
    mode: 'click',
    popup: '.filter-options',
    btnOpen: '.filter-open',
    btnClose: '.filter-close',
    openClass: 'filter-active',
  });
}
