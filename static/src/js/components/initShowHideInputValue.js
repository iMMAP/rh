export default function initShowHideInputValue() {
  const BLOCK = Array.prototype.slice.call(document.querySelectorAll('.js-show-hide-field'));

  BLOCK.forEach((element) => {
    const BUTTON = element.querySelector('.show-hide-btn');
    const INPUT = element.querySelector('input');

    BUTTON.addEventListener('click', (event) => {
      event.preventDefault();

      if (INPUT.type === 'password') {
        BUTTON.innerHTML = '<span class="icon-eye-off"></span>';
        INPUT.type = 'text';
      } else {
        BUTTON.innerHTML = '<span class="icon-eye"></span>';
        INPUT.type = 'password';
      }
    });
  });
}
