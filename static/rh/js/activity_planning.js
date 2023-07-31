// Constant for the duration of the slideToggle animations
const TOGGLE_DURATION = 500;

/**
* Handle Add Dynamic Activity Form
**/
function addActivityForm() {
	// Get the empty form template
	const emptyFormTemplate = $("#empty-activity-form-template");

	// Get the formset container and the form index
	const formsetContainer = $("#activity-formset");
	const formIdx = formsetContainer.children().length; // Get the number of existing forms
	const formPrefix = emptyFormTemplate[0].getAttribute('data-form-prefix'); // Get the formset prefix

	// Replace the form prefix placeholder with the actual form index in the template HTML
	const newFormHtml = emptyFormTemplate.html().replace(/__prefix__/g, formIdx);

	// Create a new form element and prepend it to the formset container
	const newForm = $(document.createElement('div')).html(newFormHtml);
	formsetContainer.prepend(newForm.children().first());

	setTimeout(function () {
		// Initialize chained fields for the newly added form
		const activityTypeSelect = $(`select[id^='id_activityplan_set-${formIdx}-activity_type']`);
		const activityDomainSelectID = "#id_" + activityTypeSelect.data('chainfield');
		const activityTypeUrl = activityTypeSelect.data('url');
		const activityTypeID = "#" + activityTypeSelect.attr('id');
		chainedfk.init(activityDomainSelectID, activityTypeUrl, activityTypeID, '', '--------', true);

		const activityDetailSelect = $(`select[id^='id_activityplan_set-${formIdx}-activity_detail']`);
		const activityTypeSelectID = "#id_" + activityDetailSelect.data('chainfield');
		const activityDetailUrl = activityDetailSelect.data('url');
		const activityDetailID = "#" + activityDetailSelect.attr('id');
		chainedfk.init(activityTypeSelectID, activityDetailUrl, activityDetailID, '', '--------', true);

		const IndicatorsSelect = $(`select[id^='id_activityplan_set-${formIdx}-indicators']`);
		const IndicatorsUrl = IndicatorsSelect.data('url');
		const IndicatorsID = "#" + IndicatorsSelect.attr('id');
		chainedm2m.init(activityTypeSelectID, IndicatorsUrl, IndicatorsID, '', '--------', true);
		$(IndicatorsID).select2();

	}, 100);

	// Update the management form values
	const managementForm = $(`input[name="${formPrefix}-TOTAL_FORMS"]`);
	const totalForms = parseInt(managementForm.val()) + 1;
	managementForm.val(totalForms.toString());
}


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


$(document).ready(function () {

	// Initialize indicators with django select except the empty form
	$("select[multiple]:not(#id_activityplan_set-__prefix__-indicators)").select2();

	// Button to handle addition of new activity form.
	$('#add-activity-form-button').on('click', function(event) {
		event.preventDefault(); // Prevent the default behavior (form submission)
		addActivityForm(); // Call the function to add a new activity form
	});

	/**
	 * Initializes facility monitoring form functionality for multiple forms.
	 * @param {number} currentFormCount - The number of facility monitoring forms currently displayed on the page.
	 * @returns {void}
	 */
	/*async function get_facility_sites(formIndex) {
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

		requestData = {
			clusters: clusterIds,
			listed_facilities: facilityIds,
		}

		try {
			const response = await $.ajax({
				type: "GET",
				url: facilitySiteUrl,
				data: requestData,
			});

			$(`#id_form-${formIndex}-facility_type`).html(response);
			$(`select#id_form-${formIndex}-facility_type`).val(selected_facilities);
		} catch (error) {
			console.error(`Error fetching Facilities: ${error}`);
		}
	}*/

	$.fn.reverse = [].reverse;
	let $activityBlockHolder = $(".activity-block-holder");
	$activityBlockHolder.reverse().each(function (formIndex, formElement) {
		// Call updateTitle for activity_domain manually as on page load as it is not triggered for
		// activity_domain
		updateTitle(`activityplan_set-${formIndex}`, `id_activityplan_set-${formIndex}-activity_domain`);

		// Call Facility Monitoring function when page loads.
		// handleFacilityMonitoring(formElement, formIndex);

		// Call get_facility_sites and fetch the facility sites types.
		// get_facility_sites(formIndex);

	
	});

	$activityBlockHolder.on("change", function (event) {
		event.preventDefault();

		const $formElement = $(this);
		const formIndex = $(this).attr("data-form-id").split("form-")[1];

		// Handle Facility Monitoring Checkbox
		// FIXME: Fix repeated code.
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
	});

});
