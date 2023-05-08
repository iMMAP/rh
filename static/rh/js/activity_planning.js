// Constant for the duration of the slideToggle animations
const TOGGLE_DURATION = 500;

$(document).ready(function () {
	/**
	 * Initializes facility monitoring form functionality for multiple forms.
	 * @param {number} currentFormCount - The number of facility monitoring forms currently displayed on the page.
	 * @returns {void}
	 */

	async function get_facility_sites(formIndex) {
		const facilitySiteUrl = $(`#id_form-${formIndex}-facility_type`).attr(
			"facility-sites-queries-url"
		);

		const facilityIds = $(`select#id_form-${formIndex}-facility_type option`)
			.map(function () {
				return $(this).val();
			})
			.get();
		const clusterIds = $("#clusters").data("clusters");
		const selected_facilities = $(
			`select#id_form-${formIndex}-facility_type`
		).val();
		try {
			const response = await $.ajax({
				type: "GET",
				url: facilitySiteUrl,
				data: {
					clusters: clusterIds,
					listed_facilities: facilityIds,
				},
			});

			$(`#id_form-${formIndex}-facility_type`).html(response);
			$(`select#id_form-${formIndex}-facility_type`).val(selected_facilities);
		} catch (error) {
			console.error(`Error fetching Facilities: ${error}`);
		}
	}

	$.fn.reverse = [].reverse;
	let $activityBlockHolder = $(".activity-block-holder");
	$activityBlockHolder.reverse().each(function (formIndex, formElement) {
		// Call updateTitle for activity_domain manually as on page load as it is not triggered for
		// activity_domain
		updateTitle(`form-${formIndex}`, `id_form-${formIndex}-activity_domain`);

		// Call Facility Monitoring function when page loads.
		handleFacilityMonitoring(formElement, formIndex);

		// Call
		handleAgeDesegregation(formElement, formIndex);

		// Call get_facility_sites and fetch the facility sites types.
		get_facility_sites(formIndex);
	});

	$activityBlockHolder.on("change", function (event) {
		event.preventDefault();

		const $formElement = $(this);
		const formIndex = $(this).attr("data-form-id").split("form-")[1];

		// Handle Facility Monitoring Checkbox
		if (event.target.name.indexOf("facility_monitoring") >= 0) {
			let $facilityMonitoring = $formElement.find(
				`#id_form-${formIndex}-facility_monitoring`
			);
			let $facilityName = $formElement.find(
				`#id_form-${formIndex}-facility_name`
			);
			let $facilityId = $formElement.find(`#id_form-${formIndex}-facility_id`);
			let $facilityDetails1 = $formElement.find(
				`#form-${formIndex}_facility_details_1`
			);
			let $facilityDetails2 = $formElement.find(
				`#form-${formIndex}_facility_details_2`
			);

			if (!$facilityMonitoring.is(":checked")) {
				$facilityDetails1.hide(TOGGLE_DURATION);
				$facilityDetails2.hide(TOGGLE_DURATION);
				$facilityName.prop("required", false).removeClass("is-required");
				$facilityId.prop("required", false).removeClass("is-required");
			} else {
				$facilityDetails1.show(TOGGLE_DURATION);
				$facilityDetails2.show(TOGGLE_DURATION);
				$facilityName.prop("required", true).addClass("is-required");
				$facilityId.prop("required", true).addClass("is-required");
			}
		}

		// Handle Age Desegregation Checkbox
		if (event.target.name.indexOf("age_desegregation") >= 0) {
			let $ageDesegregation = $formElement.find(
				`#id_form-${formIndex}-age_desegregation`
			);
			let $statisticTable = $formElement.find(
				`#form-${formIndex}-statistic-holder`
			);
			if (!$ageDesegregation.is(":checked")) {
				$statisticTable.hide(TOGGLE_DURATION);
			} else {
				$statisticTable.show(TOGGLE_DURATION);
			}
		}
	});

	/*
	 * Desegregation Table calculations
	 */

	// Attach a handler to the 'input' event for all number input fields
	$('input[type="number"]').on("input", function () {
		const tableId = $(this).closest("table").attr("id");

		// Calculate the row total for the current row
		var rowTotal = 0;
		$(this)
			.closest("tr")
			.find('input[type="number"]')
			.each(function () {
				if ($(this).val()) {
					rowTotal += parseInt($(this).val());
				}
			});

		// Set the row total value for the current row and update the displayed value
		$(this)
			.closest("tr")
			.find(".total-row")
			.attr("data-row-total-value", rowTotal)
			.val(rowTotal | 0);

		var allRowsTotal = 0;
		$(`#${tableId} tbody tr`).each(function () {
			var rowTotal = parseInt($(this).find(".total-row").val());
			if (!isNaN(rowTotal)) {
				allRowsTotal += rowTotal;
			}
		});

		// Set the all rows total value for the all the rows and update the displayed value
		$(`#${tableId} tbody tr`)
			.find(".all-rows-total")
			.attr("data-row-total-value", allRowsTotal)
			.val(allRowsTotal | 0);

		const activityForm = tableId.split("-table")[0];
		const people = $(`#${activityForm}-people-count`);
		people.text(allRowsTotal);

		// Calculate the column total for all number input fields that have a value, reverse the each loop
		// as we are rendering the forms in reversed order
		// $.fn.reverse = [].reverse;
		/* TODO: Handle the total column wise */
		$(`#${tableId} input[type="number"][step="1"][placeholder="-"][value!=""]`)
			.reverse()
			.each(function (index) {
				// $('input[type="number"][step="1"][placeholder="-"][value!=""]').reverse().each(function(index) {
				var colTotal = 0;
				$(`#${tableId} tbody tr`).each(function () {
					var val = $(this).find('input[type="number"]').eq(index).val();
					if (val) {
						colTotal += parseInt(val);
					}
				});
				// var tableId = $(this).closest('table').attr('id');
				// Set the column total value for all total cells and update the displayed value
				// $(`.${tableId.replace("-table", "")}-total-col`).eq(index).attr('data-col-total-value', colTotal).val(colTotal);
			});
	});
});

/**
* Handle Facility Monitoring field
@param {string} formElement - Form Element.
@param {string} formIndex - Form Index.
**/
function handleFacilityMonitoring(formElement, formIndex) {
	let $facilityMonitoring = $(formElement).find(
		`#id_form-${formIndex}-facility_monitoring`
	);
	let $facilityName = $(formElement).find(
		`#id_form-${formIndex}-facility_name`
	);
	let $facilityId = $(formElement).find(`#id_form-${formIndex}-facility_id`);
	let $facilityDetails1 = $(formElement).find(
		`#form-${formIndex}_facility_details_1`
	);
	let $facilityDetails2 = $(formElement).find(
		`#form-${formIndex}_facility_details_2`
	);

	if (!$facilityMonitoring.is(":checked")) {
		$facilityDetails1.hide();
		$facilityDetails2.hide();
		$facilityName.prop("required", false).removeClass("is-required");
		$facilityId.prop("required", false).removeClass("is-required");
	} else {
		$facilityName.prop("required", true).addClass("is-required");
		$facilityId.prop("required", true).addClass("is-required");
	}
}

/**
* Handle Age Desegregation
@param {string} formElement - Form Element.
@param {string} formIndex - Form Index.
**/
function handleAgeDesegregation(formElement, formIndex) {
	let $ageDesegregation = $(formElement).find(
		`#id_form-${formIndex}-age_desegregation`
	);
	let $statisticTable = $(formElement).find(
		`#form-${formIndex}-statistic-holder`
	);
	if (!$ageDesegregation.is(":checked")) {
		$statisticTable.hide();
	}
}

/**
Updates the titles of the activity form sections based on the selected values of the input element.
@param {string} formPrefix - The prefix of the activity form sections.
@param {string} inputElementId - The ID of the input element that triggered the update.
**/
function updateTitle(formPrefix, inputElementId) {
	const selectedValue = $("#" + inputElementId).val();
	const selectedText = $("#" + inputElementId + " option:selected").text();

	const titleElements = {
		activity_domain: $("#title-domain-" + formPrefix),
		activity_type: $("#title-type-" + formPrefix),
		activity_detail: $("#title-detail-" + formPrefix),
	};

	for (const [key, value] of Object.entries(titleElements)) {
		if (inputElementId.includes(key)) {
			if (key === "activity_detail") {
				value.text(selectedValue ? selectedText : "");
			} else {
				value.text(selectedValue ? selectedText + ", " : "");
			}
		}
	}
}
