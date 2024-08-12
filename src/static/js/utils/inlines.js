const formset = (elements, opts) => {
	const defaults = {
		prefix: "form",
		addText: "add another",
		deleteText: "remove",
		addCssClass: "add-row",
		deleteCssClass: "delete-row",
		emptyCssClass: "empty-row",
		formCssClass: "dynamic-form",
		added: null,
		removed: null,
		addButton: null,
	};

	const options = { ...defaults, ...opts };
	const elementsArray = Array.from(elements);
	const parent = elementsArray[0].parentElement;
	const totalForms = document.getElementById(
		`id_${options.prefix}-TOTAL_FORMS`,
	);
	const maxForms = document.getElementById(
		`id_${options.prefix}-MAX_NUM_FORMS`,
	);
	const minForms = document.getElementById(
		`id_${options.prefix}-MIN_NUM_FORMS`,
	);
	let nextIndex = Number.parseInt(totalForms.value, 10);
	let addButton = options.addButton;

	const updateElementIndex = (el, prefix, ndx) => {
		const idRegex = new RegExp(`(${prefix}-(\\d+|__prefix__))`);
		const replacement = `${prefix}-${ndx}`;

		if (el.hasAttribute("for")) {
			el.setAttribute(
				"for",
				el.getAttribute("for").replace(idRegex, replacement),
			);
		}
		if (el.id) {
			el.id = el.id.replace(idRegex, replacement);
		}
		if (el.name) {
			el.name = el.name.replace(idRegex, replacement);
		}
	};

	const toggleDeleteButtonVisibility = (inlineGroup) => {
		if (minForms.value !== "" && minForms.value - totalForms.value >= 0) {
			for (const button of inlineGroup.querySelectorAll(".inline-deletelink")) {
				button.style.display = "none";
			}
		} else {
			for (const button of inlineGroup.querySelectorAll(".inline-deletelink")) {
				button.style.display = "";
			}
		}
	}

	const addInlineAddButton = () => {
		if (!addButton) {
			if (elementsArray[0].tagName === "TR") {
				const numCols = elementsArray[elementsArray.length - 1].children.length;
				const newRow = document.createElement("tr");
				newRow.className = options.addCssClass;
				newRow.innerHTML = `<td colspan="${numCols}"><a href="#">${options.addText}</a></td>`;
				parent.appendChild(newRow);
				addButton = newRow.querySelector("a");
			} else {
				const newDiv = document.createElement("div");
				newDiv.className = options.addCssClass;
				newDiv.innerHTML = `<a href="#">${options.addText}</a>`;
				elementsArray[elementsArray.length - 1].after(newDiv);
				addButton = newDiv.querySelector("a");
			}
		}
		addButton.addEventListener("click", addInlineClickHandler);
	};

	const addInlineClickHandler = (e) => {
		e.preventDefault();
		const template = document.getElementById(`${options.prefix}-empty`);
		const row = template.cloneNode(true);
		const newRowSelect = row.querySelector('select');

		// delete the prev selected options
		const selects = document.querySelectorAll('table tbody tr.form-row select');
		for (const select of selects) {
			const selectedOptions = Array.from(select.options).filter(option => option.selected);
			for(const opt of selectedOptions){
				if (newRowSelect) {
					const optionToRemove = Array.from(newRowSelect.options).find(option => option.value === opt.value);
					if (optionToRemove) {
						optionToRemove.remove();
					}
				}
			}
		}
		
		row.classList.remove(options.emptyCssClass);
		row.classList.add(options.formCssClass);
		row.id = `${options.prefix}-${nextIndex}`;
		addInlineDeleteButton(row);

		for (const el of row.querySelectorAll("*")) {
			updateElementIndex(el, options.prefix, totalForms.value);
		}

		template.before(row);
		totalForms.value = Number.parseInt(totalForms.value, 10) + 1;
		nextIndex += 1;

		if (maxForms.value !== "" && maxForms.value - totalForms.value <= 0) {
			addButton.parentElement.style.display = "none";
		}
		toggleDeleteButtonVisibility(row.closest(".inline-group"));

		if (options.added) {
			options.added(row);
		}
		row.dispatchEvent(
			new CustomEvent("formset:added", {
				bubbles: true,
				detail: { formsetName: options.prefix },
			}),
		);
	};

	const addInlineDeleteButton = (row) => {
		let deleteButton;
		if (row.tagName === "TR") {
			const lastCell = row.children[row.children.length - 1];
			deleteButton = document.createElement("div");
			deleteButton.innerHTML = `<a class="${options.deleteCssClass}" href="#">${options.deleteText}</a>`;
			lastCell.appendChild(deleteButton);
		} else if (row.tagName === "UL" || row.tagName === "OL") {
			deleteButton = document.createElement("li");
			deleteButton.innerHTML = `<a class="${options.deleteCssClass}" href="#">${options.deleteText}</a>`;
			row.appendChild(deleteButton);
		} else {
			deleteButton = document.createElement("span");
			deleteButton.innerHTML = `<a class="${options.deleteCssClass}" href="#">${options.deleteText}</a>`;
			row.children[0].appendChild(deleteButton);
		}
		deleteButton
			.querySelector("a")
			.addEventListener("click", inlineDeleteHandler);
	};

	const inlineDeleteHandler = (e) => {
		e.preventDefault();
		const deleteButton = e.target;
		const row = deleteButton.closest(`.${options.formCssClass}`);
		const inlineGroup = row.closest(".inline-group");
		const prevRow = row.previousElementSibling;
		if (prevRow?.classList.contains("row-form-errors")) {
			prevRow.remove();
		}
		row.remove();
		nextIndex -= 1;

		if (options.removed) {
			options.removed(row);
		}
		document.dispatchEvent(
			new CustomEvent("formset:removed", {
				detail: { formsetName: options.prefix },
			}),
		);
		const forms = document.querySelectorAll(`.${options.formCssClass}`);
		totalForms.value = forms.length;
		if (maxForms.value === "" || maxForms.value - forms.length > 0) {
			addButton.parentElement.style.display = "";
		}
		toggleDeleteButtonVisibility(inlineGroup);

		for (const [i, form] of forms.entries()) {
			updateElementIndex(form, options.prefix, i);
			for (const el of form.querySelectorAll("*")) {
				updateElementIndex(el, options.prefix, i);
			}
		}
	};

	for (const element of elementsArray) {
		if (!element.classList.contains(options.emptyCssClass)) {
			element.classList.add(options.formCssClass);
		}
	}

	for (const element of elementsArray) {
		if (
			element.classList.contains(options.formCssClass) &&
			!element.classList.contains("has_original") &&
			!element.classList.contains(options.emptyCssClass)
		) {
			addInlineDeleteButton(element);
		}
	}

	toggleDeleteButtonVisibility(elementsArray[0]);

	addInlineAddButton();

	const showAddButton =
		maxForms.value === "" || maxForms.value - totalForms.value > 0;
	if (elementsArray.length && showAddButton) {
		addButton.parentElement.style.display = "";
	} else {
		addButton.parentElement.style.display = "none";
	}
};

const tabularFormset = (elements, options) => {
	const rows = elements;


	const reinitDateTimeShortCuts = () => {
		if (typeof DateTimeShortcuts !== "undefined") {

			for (const el of document.querySelectorAll(".datetimeshortcuts")) {
				el.remove();
			}

			DateTimeShortcuts.init();
		}
	};

	const updateSelectFilter = () => {
		if (typeof SelectFilter !== "undefined") {
			for (const el of document.querySelectorAll(".selectfilter")) {
				SelectFilter.init(el.id, el.dataset.fieldName, false);
			}
			for (const el of document.querySelectorAll(".selectfilterstacked")) {
				SelectFilter.init(el.id, el.dataset.fieldName, true);
			}
		}
	};

	const initPrepopulatedFields = (row) => {
		// biome-ignore lint/complexity/noForEach: <explanation>
		row.querySelectorAll(".prepopulated_field").forEach((field) => {
			const input = field.querySelector("input, select, textarea");
			const dependencyList = input.dataset.dependency_list || [];
			const dependencies = dependencyList.map(
				(fieldName) =>
					`#${row.querySelector(`.field-${fieldName} input, select, textarea`).id}`,
			);
			if (dependencies.length) {
				input.prepopulate(dependencies, input.getAttribute("maxlength"));
			}
		});
	};

	formset(rows, {
		prefix: options.prefix,
		addText: options.addText,
		formCssClass: `dynamic-${options.prefix}`,
		deleteCssClass: "inline-deletelink",
		deleteText: options.deleteText,
		emptyCssClass: "empty-form",
		added: (row) => {
			initPrepopulatedFields(row);
			reinitDateTimeShortCuts();
			updateSelectFilter();
		},
		addButton: options.addButton,
	});

	return rows;
};

const stackedFormset = (elements, options) => {
	const rows = elements;

	const updateInlineLabel = (row) => {
		document.querySelectorAll(".inline_label").forEach((label, i) => {
			const count = i + 1;
			label.innerHTML = label.innerHTML.replace(/(#\d+)/g, `#${count}`);
		});
	};

	const reinitDateTimeShortCuts = () => {
		if (typeof DateTimeShortcuts !== "undefined") {

			for (const el of document.querySelectorAll(".datetimeshortcuts")) {
				el.remove();
			}

			DateTimeShortcuts.init();
		}
	};

	const updateSelectFilter = () => {
		if (typeof SelectFilter !== "undefined") {

			for (const el of document.querySelectorAll(".selectfilter")) {
				SelectFilter.init(el.id, el.dataset.fieldName, false);
			}

			for (const el of document.querySelectorAll(".selectfilterstacked")) {
				SelectFilter.init(el.id, el.dataset.fieldName, true);
			}

		}
	};

	const initPrepopulatedFields = (row) => {
		// biome-ignore lint/complexity/noForEach: <explanation>
		row.querySelectorAll(".prepopulated_field").forEach((field) => {
			const input = field.querySelector("input, select, textarea");
			const dependencyList = input.dataset.dependency_list || [];

			const dependencies = dependencyList.map((fieldName) => {
				let fieldElement = row.querySelector(`.form-row .field-${fieldName}`);
				if (!fieldElement) {
					fieldElement = row.querySelector(`.form-row.field-${fieldName}`);
				}
				return `#${fieldElement.querySelector("input, select, textarea").id}`;
			});

			if (dependencies.length) {
				input.prepopulate(dependencies, input.getAttribute("maxlength"));
			}
		});
	};

	formset(rows, {
		prefix: options.prefix,
		addText: options.addText,
		formCssClass: `dynamic-${options.prefix}`,
		deleteCssClass: "inline-deletelink",
		deleteText: options.deleteText,
		emptyCssClass: "empty-form",
		removed: updateInlineLabel,
		added: (row) => {
			initPrepopulatedFields(row);
			reinitDateTimeShortCuts();
			updateSelectFilter();
			updateInlineLabel(row);
		},
		addButton: options.addButton,
	});

	return rows;
};

// biome-ignore lint/complexity/noForEach: <explanation>
document.querySelectorAll(".js-inline-admin-formset").forEach((element) => {
	const data = element.dataset;
	const inlineOptions = JSON.parse(data.inlineFormset);
	let selector;
	switch (data.inlineType) {
		case "stacked":
			selector = `${inlineOptions.name}-group .inline-related`;
			stackedFormset(
				document.querySelectorAll(selector),
				inlineOptions.options,
			);
			break;
		case "tabular":
			selector = `${inlineOptions.name}-group .tabular.inline-related tbody > tr.form-row`;
			tabularFormset(
				document.querySelectorAll(selector),
				inlineOptions.options,
			);
			break;
	}
});