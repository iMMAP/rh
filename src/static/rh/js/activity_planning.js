var DETAILS_TOGGLE_DURATION = 500;
/**
 * Handle Add Dynamic Activity Form
 **/
function addActivityForm(prefix, project, nextFormIndex) {
	// Get the empty form template
	const activityFormPrefix = `${prefix}-${nextFormIndex}`;
	const activityFormIndex = nextFormIndex;
	const projectID = project;

	$.ajax({
		url: "/ajax/get_activity_empty_form/",
		data: { project: projectID, prefix_index: nextFormIndex },
		type: "POST",
		dataType: "json",
		beforeSend: function (xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken);
		},
		success: function (data) {
			if (data.html) {
				const emptyFormTemplate = data.html;

				// Get the formset container
				const formsetContainer = $("#activity-formset");

				// Get the number of existing forms
				const formIdx = formsetContainer.children().length;
				// Replace the form prefix placeholder with the actual form index in the template HTML
				const newFormHtml = emptyFormTemplate.replace(/__prefix__/g, formIdx);

				// Create a new form element and append it to the formset container
				const newForm = $(document.createElement("div")).html(newFormHtml);
				const addForm = newForm.children().first();
				formsetContainer.append(addForm);

				// Open/Activate the accordion
				const parentDiv = addForm.find(".project-activity-accordion-slide");
				const innerHolder = parentDiv.closest(".inner-holder");

				// Unbind any existing click events
				innerHolder.find(".project-activity-accordion-opener").off("click");
				innerHolder
					.find(".project-activity-accordion-opener")
					.on("click", function (event) {
						event.preventDefault(); // Prevent the default behavior (form submission)
						event.stopPropagation(); // Prevent the default behavior (propagation)
						innerHolder.toggleClass("project-activity-accordion-active");
						$(this)
							.next(".project-activity-accordion-slide")
							.toggleClass("js-acc-hidden");
						// $(this).next('.target-location-accordion-slide').slideToggle(DETAILS_TOGGLE_DURATION);
					});

				setTimeout(function () {
					// Initialize chained and chainedm2m fields for the newly added form
					const activityTypeSelect = $(
						`select[id^='id_activityplan_set-${formIdx}-activity_type']`,
					);
					const activityDomainSelectID =
						"#id_" + activityTypeSelect.data("chainfield");
					const activityTypeUrl = activityTypeSelect.data("url");
					const activityTypeID = "#" + activityTypeSelect.attr("id");
					chainedfk.init(
						activityDomainSelectID,
						activityTypeUrl,
						activityTypeID,
						"",
						"--------",
						true,
					);

					const activityDetailSelect = $(
						`select[id^='id_activityplan_set-${formIdx}-activity_detail']`,
					);
					const activityTypeSelectID =
						"#id_" + activityDetailSelect.data("chainfield");
					const activityDetailUrl = activityDetailSelect.data("url");
					const activityDetailID = "#" + activityDetailSelect.attr("id");
					chainedfk.init(
						activityTypeSelectID,
						activityDetailUrl,
						activityDetailID,
						"",
						"--------",
						true,
					);

					const indicatorsSelect = $(
						`select[id^='id_activityplan_set-${formIdx}-indicator']`,
					);
					const IndicatorsUrl = indicatorsSelect.data("url");
					const IndicatorsID = "#" + indicatorsSelect.attr("id");
					// chainedm2m.init(activityTypeSelectID, IndicatorsUrl, IndicatorsID, '', '--------', true);
					chainedfk.init(
						activityTypeSelectID,
						IndicatorsUrl,
						IndicatorsID,
						"",
						"--------",
						true,
					);
					$(IndicatorsID).select2();
				}, 100);
			}
		},
		error: function (error) {
			console.log("Error fetching empty form:", error);
		},
	});

	// Update the management form values
	const managementForm = $(`input[name="${prefix}-TOTAL_FORMS"]`);
	const totalForms = parseInt(managementForm.val()) + 1;
	managementForm.val(totalForms.toString());
}

/**
 * Handle Add Dynamic Activity Form
 **/
function addTargetLocationForm(prefix, project, nextFormIndex, activityDomain) {
	const activityFormPrefix = prefix;
	const projectID = project;

	$.ajax({
		url: "/ajax/get_target_location_empty_form/",
		data: { project: projectID, prefix_index: nextFormIndex, activity_domain: activityDomain },
		type: "POST",
		dataType: "json",
		beforeSend: function (xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken);
		},
		success: function (data) {
			if (data.html) {
				const emptyFormTemplate = data.html;

				// Get the formset prefix
				const formPrefix = activityFormPrefix;

				// Get the formset container
				const formsetContainer = $(`#${formPrefix}`);

				// Get the number of existing forms
				const formIdx = formsetContainer.children().length; // Get the number of existing forms

				// Replace the form prefix placeholder with the actual form index in the template HTML
				const newFormHtml = emptyFormTemplate.replace(/__prefix__/g, formIdx);

				// Create a new form element and append it to the formset container
				const newForm = $(document.createElement("div")).html(newFormHtml);
				const addedForm = newForm.children().first();
				formsetContainer.append(addedForm);

				// Update the management form values
				const managementForm = $(
					`input[name="target_locations_${formPrefix}-TOTAL_FORMS"]`,
				);
				const totalForms = parseInt(managementForm.val()) + 1;
				managementForm.val(totalForms.toString());

				// Open/Activate the accordion
				const parentDiv = formsetContainer.closest(
					".target-location-accordion-slide",
				);
				const innerHolder = parentDiv.closest(".inner-holder");

				// Unbind any existing click events
				innerHolder.find(".target-location-accordion-opener").off("click");
				innerHolder
					.find(".target-location-accordion-opener")
					.on("click", function (event) {
						event.preventDefault(); // Prevent the default behavior (form submission)
						event.stopPropagation(); // Prevent the default behavior (propagation)
						innerHolder.toggleClass("target-location-accordion-active");
						$(this)
							.next(".target-location-accordion-slide")
							.toggleClass("js-acc-hidden");
						// $(this).next('.target-location-accordion-slide').slideToggle(DETAILS_TOGGLE_DURATION);
					});

				if (addedForm) {
					const locationPrefix = addedForm[0].dataset.locationPrefix;
					// Load Locations (districts and zones)
					getLocations(locationPrefix, "district", "province");
					getLocations(locationPrefix, "zone", "district");

					// Add Load Locations (districts and zones) event for new form
					$(`#id_${locationPrefix}-province`).on("change", function () {
						getLocations(
							locationPrefix,
							"district",
							"province",
							(clearZone = true),
						);
					});
					$(`#id_${locationPrefix}-district`).on("change", function () {
						getLocations(locationPrefix, "zone", "district");
					});

					// Update disaggregations based on indicators for the new added form
					const activityFormIndex = formPrefix.match(
						/activityplan_set-(\d+)/,
					)[1];
					let $select2Event = $(
						`#id_activityplan_set-${activityFormIndex}-indicator`,
					);

					let selectedID = $select2Event[0].value
					handleDisaggregationForms($select2Event[0], selectedID, [
						locationPrefix,
					]);

					// Call Facility Monitoring function when page loads.
					handleFacilityMonitoring(locationPrefix, addedForm);
					let $facilityMonitoring = $(addedForm).find(
						`#id_${locationPrefix}-facility_monitoring`
					);
					$facilityMonitoring.change(function () {
						handleFacilityMonitoring(locationPrefix, addedForm);
					});

				}
			}
		},
		error: function (error) {
			console.log("Error fetching empty form:", error);
		},
	});
}

/**
 * Handle Add Dynamic Disaggregation Form
 **/
function handleDisaggregationForms(
	indicatorsSelect,
	selectedID,
	locationsPrefixes = [],
) {
	
	// Extract activity index from indicatorsSelect name attribute
	const activityIndex = indicatorsSelect.name.match(
		/activityplan_set-(\d+)/,
	)[1];
	// Get all target location forms
	var targetLocationForms = $(
		`#Locations-activityplan_set-${activityIndex} .target_location_form`,
	);

	


	// Extract locations prefixes from target location forms
	if (locationsPrefixes.length === 0) {
		targetLocationForms.each(function (index, element) {
			var locationPrefix = $(element).data("location-prefix");
			locationsPrefixes.push(locationPrefix);
		});
	}

	// Make AJAX request to fetch disaggregation forms
	$.ajax({
		url: "/ajax/get_disaggregations_forms/",
		data: { indicator: selectedID, locations_prefixes: locationsPrefixes },
		type: "POST",
		dataType: "json",
		beforeSend: function (xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken);
		},
		success: function (data) {
			if (data) {
				$.each(locationsPrefixes, function (locationIndex) {
					const locationPrefix = locationsPrefixes[locationIndex];
					const disaggregationFormsArray = data[locationPrefix];
					// Remove existing forms
					$("#" + locationPrefix)
						.find(".location-inner-holder")
						.remove();

					if (disaggregationFormsArray) {
						// Append new disaggregation forms
						$("#" + locationPrefix)
							.find(".disaggregation-accordion-slide")
							.append(disaggregationFormsArray.join(" "));
					}

					// Update the management form values
					if (disaggregationFormsArray) {
						const managementForm = $(
							`input[name="disaggregation_${locationPrefix}-TOTAL_FORMS"]`,
						);
						const totalForms = parseInt(disaggregationFormsArray.length);
						managementForm.val(totalForms.toString());
					}
					// Open/Activate the accordion
					const parentDiv = $("#" + locationPrefix).find(
						".disaggregation-accordion-slide",
					);
					const innerHolder = parentDiv.closest(".inner-holder");

					// Unbind any existing click events
					innerHolder.find(".disaggregation-accordion-opener").off("click");
					innerHolder
						.find(".disaggregation-accordion-opener")
						.on("click", function (event) {
							event.preventDefault(); // Prevent the default behavior
							event.stopPropagation(); // Prevent the default behavior (propagation)
							innerHolder.toggleClass("disaggregation-accordion-active");
							parentDiv.toggleClass("js-acc-hidden");
							// parentDiv.slideToggle(DETAILS_TOGGLE_DURATION);
						});
				});
			}
		},
		error: function (error) {
			console.log("Error fetching empty form:", error);
		},
	});
}

/**
Updates the titles of the activity form sections based on the selected values of the input element.
**/
function updateActivityTitle(formPrefix, inputElementId) {
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

/**
Updates the titles of the activity form sections based on the selected values of the input element.
@param {string} activityFormPrefix - The prefix of the activity form sections.
@param {string} locationInputElementId - The ID of the input element that triggered the update.
**/
function updateLocationTitle(locationPrefix, locationInputElementId) {
	const selectedLocationValue = $("#" + locationInputElementId).val();
	const selectedLocationText = $(
		"#" + locationInputElementId + " option:selected",
	).text();

	const locationTitleElements = {
		province: $("#title-province-" + locationPrefix),
		district: $("#title-district-" + locationPrefix),
		// TODO: Update for site and zone
		// site_name: $("#title-site_name-" + locationPrefix),
	};

	for (const [key, value] of Object.entries(locationTitleElements)) {
		if (locationInputElementId.includes(key)) {
			if (key === "district") {
				value.text(selectedLocationValue ? selectedLocationText : "");
			} else {
				value.text(selectedLocationValue ? selectedLocationText + "," : "");
			}
		}
	}
}

/**
* Update the titles for locations in each activity
@param {string} locationPrefix - The prefix of the location form sections.
**/
function updateLocationBlockTitles(locationPrefix) {
	// id_target_locations_activityplan_set-0-0-province
	updateLocationTitle(locationPrefix, `id_${locationPrefix}-province`);
	updateLocationTitle(locationPrefix, `id_${locationPrefix}-district`);
}

/**
 * TODO: Make it generic
 * Get Districts and Zpnes for Target Location Form
 **/
function getLocations(
	locationPrefix,
	locationType,
	parentType,
	clearZone = null,
) {
	// Get the URL for fetching locations
	const locationUrl = $(`#id_${locationPrefix}-${locationType}`).attr(
		`locations-queries-url`,
	);

	// Get an array of location IDs
	const locationIds = $(`select#id_${locationPrefix}-${locationType} option`)
		.map((_, option) => option.value)
		.get();

	// Get the parent IDs
	const parentIds = [$(`#id_${locationPrefix}-${parentType}`).val()];

	// Get the selected locations
	const selectedLocations = $(
		`select#id_${locationPrefix}-${locationType}`,
	).val();
	if (locationUrl) {
		// Use JavaScript Cookie library
		$.ajax({
			url: locationUrl,
			data: {
				parents: parentIds,
				listed_locations: locationIds,
			},
			type: "POST",
			dataType: "json",
			beforeSend: function (xhr, settings) {
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			},
			success: function (data) {
				// Clear zone if needed
				if (parentType === "province" && clearZone === true) {
					$(`#id_${locationPrefix}-zone`).html("").val("");
				}
				if (data) {
					// Update the location select element
					$(`#id_${locationPrefix}-${locationType}`).html(data);
					$(`select#id_${locationPrefix}-${locationType}`).val(
						selectedLocations,
					);
				}

				// if(locationType == 'zone' && data === ''){
				// 	$(`#id_${locationPrefix}-${locationType}`).parent().hide();
				// }else{
				// 	$(`#id_${locationPrefix}-${locationType}`).parent().show();
				// }
			},
			error: function (error) {
				console.log("Error fetching empty form:", error);
			},
		});
	}
}


/**
* Handle Facility Monitoring field
@param {string} locationPrefix - Form Location Prefix.
@param {string} formElement - Form Element.
**/
function handleFacilityMonitoring(locationPrefix, formElement) {
	$formElement = $(formElement)
	let $facilityMonitoring = $(`#id_${locationPrefix}-facility_monitoring`);
	let $facilityName = $formElement.find(
		`#id_${locationPrefix}-facility_name`
	);
	let $facilityDetails = $formElement.find(
		`#facility_details_${locationPrefix}`
	);

	if (!$facilityMonitoring.is(":checked")) {
		$facilityDetails.hide();
		$facilityName.prop("required", false).removeClass("is-required");
	} else {
		$facilityDetails.show();
		$facilityName.prop("required", true).addClass("is-required");
	}
}

/**
 * Ready Function
 **/
$(function () {
	// Initialize indicators with django select except for the empty form
	$(
		"select:not(#id_activityplan_set-__prefix__-indicator)",
	).select2();


	// Button to handle addition of new activity form.
	$("#add-activity-form-button")
		.off("click")
		.on("click", function (event) {
			event.preventDefault(); // Prevent the default behavior (form submission)
			event.stopPropagation();
			const activityFormPrefix = event.currentTarget.dataset.formPrefix;
			const activityProject = event.currentTarget.dataset.project;
			const nextFormIndex = event.currentTarget.dataset.formsCount;
			addActivityForm(activityFormPrefix, activityProject, nextFormIndex); // Call the function to add a new activity form
		});

	// Button to handle addition of new target location form.
	$(document)
		.off("click")
		.on("click", ".add-target-location-form-button", function (event) {
			event.preventDefault(); // Prevent the default behavior (form submission)
			event.stopPropagation(); // Prevent the default behavior (propagation)
			
			const activityFormPrefix = event.currentTarget.dataset.formPrefix;
			const activityProject = event.currentTarget.dataset.project;
			const activityDomain = $(document).find(`#id_${activityFormPrefix}-activity_domain`)
			const activityFormIndex = activityFormPrefix.match(/\d+/)[0];
			addTargetLocationForm(
				activityFormPrefix,
				activityProject,
				activityFormIndex,
				activityDomain.val(),
			); // Call the function to add a new activity form
		});

	let $activityBlockHolder = $(".activity_form");
	$activityBlockHolder.each(function (formIndex, formElement) {
		// Call updateActivityTitle for activity_domain manually as on page load as it is not triggered for
		updateActivityTitle(
			`activityplan_set-${formIndex}`,
			`id_activityplan_set-${formIndex}-activity_domain`,
		);

		// Update disaggregations based on indicators
		var $select2Event = $(`#id_activityplan_set-${formIndex}-indicator`);
		$select2Event.on("select2:select", function (event) {
			let indicatorsSelect = event.currentTarget;
			let selectedID = $(indicatorsSelect)[0].value
			
			handleDisaggregationForms(indicatorsSelect, selectedID);
		});

		$select2Event.on("select2:unselect", function (event) {
			let indicatorsSelect = event.currentTarget;
			let selectedID = $(indicatorsSelect)[0].value
			handleDisaggregationForms(indicatorsSelect, selectedID);
		});

	});

	const $locationBlock = $(".target_location_form");
	$locationBlock.each(function (formIndex, formElement) {
		const locationPrefix = formElement.dataset.locationPrefix;

		// Update the Target Locations Titles
		updateLocationBlockTitles(locationPrefix);

		// TODO: Optimize by saving data locally
		// Initial load for districts and zones
		getLocations(locationPrefix, "district", "province");
		getLocations(locationPrefix, "zone", "district");

		$(`#id_${locationPrefix}-province`).on("change", function () {
			getLocations(locationPrefix, "district", "province", (clearZone = true));
		});
		$(`#id_${locationPrefix}-district`).on("change", function () {
			getLocations(locationPrefix, "zone", "district");
		});
		// Call Facility Monitoring function when page loads.
		handleFacilityMonitoring(locationPrefix, formElement);
		
		let $facilityMonitoring = $(formElement).find(
			`#id_${locationPrefix}-facility_monitoring`
		);
		$facilityMonitoring.change(function () {
			handleFacilityMonitoring(locationPrefix, formElement);
		});
	});
});
// update indicator types 
function updateIndicatorTypes(e){
	let id = e.target.value;
	console.log(id);
	let indicatorUrl = e.target.dataset.indicatorUrl;

	const formData = new FormData();
	formData.append('id',id);
	formData.append('csrfmiddlewaretoken', csrftoken);
	fetch(indicatorUrl,{
		method: 'POST',
		body: formData
	}).then(async response => {
		let data = await response.json()
		document.getElementById("indicator-types").innerHTML = data.html;
	}).catch(error => {
		console.log(error);
	});

}
