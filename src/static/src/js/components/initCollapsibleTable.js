document.querySelectorAll('.js-collapsible-table').forEach(element => {
  element.querySelectorAll('tbody tr').forEach((element) => {
    const opener = element.querySelector('.table-slide-opener');

    opener.addEventListener('click', (event) => {
      event.preventDefault();

      const target = opener.getAttribute('href');
      const targetEl = document.getElementById(target);

      if (targetEl.style.maxHeight) {
        targetEl.style.maxHeight = null;
        element.classList.remove('active-row');
      } else {
        /* eslint-disable */
        targetEl.style.maxHeight = targetEl.scrollHeight + 'px';
        /* eslint-enable */
        element.classList.add('active-row');
      }
    });
  });

})

