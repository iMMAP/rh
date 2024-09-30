// popups init
export default function initPopups() {
  const contentPopup = (holderSelector, options) => {
    const holder = document.querySelector(holderSelector);

    if(!holder){
      return;
    }

    const popup = holder.querySelector(options.popup);
    const btnOpen = holder.querySelector(options.btnOpen);
    const btnClose = holder.querySelector(options.btnClose);

    const showPopup = () => {
      holder.classList.add(options.openClass);
      popup.style.display = 'block';
      document.addEventListener('click', outsideClickHandler);
    };

    const hidePopup = () => {
      holder.classList.remove(options.openClass);
      popup.style.display = 'none';
      document.removeEventListener('click', outsideClickHandler);
    };

    const outsideClickHandler = (e) => {
      if (!holder.contains(e.target) && e.target !== btnOpen) {
        hidePopup();
      }
    };

    btnOpen?.addEventListener('click', (e) => {
      e.preventDefault();
      holder.classList.contains(options.openClass) ? hidePopup() : showPopup();
    });

    if(btnClose){
    btnClose?.addEventListener('click', (e) => {
      e.preventDefault();
      hidePopup();
    });
    }
  };

  contentPopup('.export-formats-holder', {
    mode: 'click',
    popup: '.export-formats',
    btnOpen: '.export-open',
    btnClose: '.export-close',
    openClass: 'export-formats-active',
  });

  contentPopup('.filter-holder', {
    mode: 'click',
    popup: '.filter-options',
    btnOpen: '.filter-open',
    btnClose: '.filter-close',
    openClass: 'filter-active',
  });

  // contentPopup('.confirmation-modal', {
  //   mode: 'click',
  //   popup: '.confirmation-options',
  //   btnOpen: '.confirmation-open',
  //   btnClose: '.confirmation-close',
  //   openClass: 'confirmation-active',
  // });
}