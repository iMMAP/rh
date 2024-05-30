export default function initCopyInputValue() {
  const BLOCK = Array.prototype.slice.call(document.querySelectorAll('.js-copy-field'));

  // biome-ignore lint/complexity/noForEach: <explanation>
  BLOCK.forEach((element) => {
    const BUTTON = element.querySelector('.copy-btn');
    const INPUT = element.querySelector('input');
    const TOOLTIP = element.querySelector('.tooltiptext');

    BUTTON.addEventListener('click', (event) => {
      event.preventDefault();

      INPUT.select();
      INPUT.setSelectionRange(0, 99999);
      navigator.clipboard.writeText(INPUT.value);

      TOOLTIP.innerHTML = 'Copied!';
    });
  });
}
