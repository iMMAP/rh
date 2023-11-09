export default function initCheckAllCheckboxes() {
  jQuery('[data-check-pattern]').checkAll();
}

/*
 * jQuery check all plugin
 */
/* eslint-disable */
;(function($) {
  'use strict';

  $.fn.checkAll = function(options) {
    return this.each(function() {
      var mainCheckbox = $(this);
      var selector = mainCheckbox.attr('data-check-pattern');
      var onChangeHandler = function(e) {
        var $currentCheckbox = $(e.currentTarget);
        var $subCheckboxes;

        if ($currentCheckbox.is(mainCheckbox)) {
          $subCheckboxes = $(selector);
          $subCheckboxes.prop('checked', mainCheckbox.prop('checked'));
        } else if ($currentCheckbox.is(selector)) {
          $subCheckboxes = $(selector);
          mainCheckbox.prop('checked', $subCheckboxes.filter(':checked').length === $subCheckboxes.length);
        }
      };

      $(document).on('change', 'input[type="checkbox"]', onChangeHandler);
    });
  };
}(jQuery));
/* eslint-enable */
