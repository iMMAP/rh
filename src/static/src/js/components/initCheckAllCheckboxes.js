/*
 * jQuery check all plugin
 */
/* eslint-disable */
(($) => {

	$.fn.checkAll = function (options) {
		return this.each(function () {
			const mainCheckbox = $(this);
			const selector = mainCheckbox.attr("data-check-pattern");
			var onChangeHandler = (e) => {
				const $currentCheckbox = $(e.currentTarget);
				// biome-ignore lint/style/noVar: <explanation>
				var $subCheckboxes;

				if ($currentCheckbox.is(mainCheckbox)) {
					$subCheckboxes = $(selector);
					$subCheckboxes.prop("checked", mainCheckbox.prop("checked"));
				} else if ($currentCheckbox.is(selector)) {
					$subCheckboxes = $(selector);
					mainCheckbox.prop(
						"checked",
						$subCheckboxes.filter(":checked").length === $subCheckboxes.length,
					);
				}
			};

			$(document).on("change", 'input[type="checkbox"]', onChangeHandler);
		});
	};
})(jQuery);
/* eslint-enable */

jQuery("[data-check-pattern]").checkAll();