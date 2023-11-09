import Choices from 'choices.js';

const initCustomSelects = () => {
  const selects = [...document.querySelectorAll('.custom-select')];

  if (!selects.length) return;

  selects.forEach((select) => {
    const choice = new Choices(select, {
      searchEnabled: false,
      itemSelectText: '',
      classNames: {
        listDropdown: 'choices__list--dropdown',
      },
      shouldSort: false,
    });

    choice.init();
  });
};

export default initCustomSelects;
