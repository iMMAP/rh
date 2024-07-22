// biome-ignore lint/complexity/noForEach: <explanation>
document.querySelectorAll("[data-check-pattern]").forEach((el) => {
	const mainCheckbox = el;
	const selector = mainCheckbox.getAttribute("data-check-pattern");

	const onChangeHandler = (e) => {
		const currentCheckbox = e.target;
		let subCheckboxes;

		if (currentCheckbox === mainCheckbox) {
			subCheckboxes = document.querySelectorAll(selector);
			// biome-ignore lint/complexity/noForEach: <explanation>
			subCheckboxes.forEach((checkbox) => {
				checkbox.checked = mainCheckbox.checked;
			});
		} else if (currentCheckbox.matches(selector)) {
			subCheckboxes = document.querySelectorAll(selector);
			mainCheckbox.checked = Array.from(subCheckboxes).every(
				(checkbox) => checkbox.checked,
			);
		}
	};

	// biome-ignore lint/complexity/noForEach: <explanation>
	document
		.querySelectorAll('input[type="checkbox"]')
		.forEach((checkbox) => {
			checkbox.addEventListener("change", onChangeHandler);
		});
});
