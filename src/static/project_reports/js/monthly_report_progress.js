var DETAILS_TOGGLE_DURATION = 500
/**
* Handle Add Dynamic Target Location Report Form
**/
function addTargetLocationReportForm(prefix, project, nextFormIndex) {
	const activityReportFormPrefix = prefix
	const projectID = project

	// Use JavaScript Cookie library
	const csrftoken = Cookies.get('csrftoken');

	$.ajax({
		url: '/ajax/get_location_report_empty_form/',
		data: {'prefix_index': nextFormIndex, 'project': projectID},
		type: 'POST',
		dataType: 'json',
		beforeSend: function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken);
		},
		success: function (data) {
			if (data.html) {

				const emptylocationReportTemplate = data.html
				
				// Get the formset prefix
				const formPrefix = activityReportFormPrefix; 
				
				// Get the formset container
				const formsetContainer = $(`#${formPrefix}`);

				// Get the number of existing forms
				const formIdx = formsetContainer.children().length; // Get the number of existing forms
				
				// Replace the form prefix placeholder with the actual form index in the template HTML
				const newFormHtml = emptylocationReportTemplate.replace(/__prefix__/g, formIdx);
				
				// Create a new form element and append it to the formset container
				const newForm = $(document.createElement('div')).html(newFormHtml);
				const addedForm = newForm.children().first()
				formsetContainer.append(addedForm);

				// Update the management form values
				const managementForm = $(`input[name="locations_report_${formPrefix}-TOTAL_FORMS"]`);
				const totalForms = parseInt(managementForm.val()) + 1;
				managementForm.val(totalForms.toString());
				
				// Open/Activate the accordion
				const parentDiv = formsetContainer.closest('.target-location-accordion-slide')
				const innerHolder = parentDiv.closest('.inner-holder')

				// Unbind any existing click events
				innerHolder.find('.target-location-accordion-opener').off('click');
				innerHolder.find('.target-location-accordion-opener').on('click', function(event) {
					event.preventDefault(); // Prevent the default behavior (form submission)
					event.stopPropagation(); // Prevent the default behavior (propagation)
					innerHolder.toggleClass('target-location-accordion-active')
					parentDiv.toggleClass('js-acc-hidden')
					// $(this).next('.target-location-accordion-slide').slideToggle(DETAILS_TOGGLE_DURATION);
				});

				if (addedForm){
					const locationReportPrefix = addedForm[0].dataset.locationPrefix
					// 	// Load Locations (districts and zones)
					getLocations(locationReportPrefix, 'district', 'province');
					getLocations(locationReportPrefix, 'zone', 'district');
						
					// Add Load Locations (districts and zones) event for new form
					$(`#id_${locationReportPrefix}-province`).on('change', function() {
						getLocations(locationReportPrefix, 'district', 'province', clearZone=true);
					});
					$(`#id_${locationReportPrefix}-district`).on('change', function() {
						getLocations(locationReportPrefix, 'zone', 'district');
					});
					
					// 	// Update disaggregations based on indicators for the new added form 
					const activityReportFormIndex = formPrefix.match(/activityplanreport_set-(\d+)/)[1] 
					var $indicator = $(`#id_activityplanreport_set-${activityReportFormIndex}-indicator`);
					if ($indicator){
						let selectedID = $indicator[0].value;
						handleDisaggregationReportForms($indicator[0], selectedID, [locationReportPrefix])
					}

					// Call Facility Monitoring function when page loads.
					handleFacilityMonitoring(locationReportPrefix, addedForm);
					let $facilityMonitoring = $(addedForm).find(
						`#id_${locationReportPrefix}-facility_monitoring`
					);
					$facilityMonitoring.change(function () {
						handleFacilityMonitoring(locationReportPrefix, addedForm);
					});
				}
			}
		},
		error: function (error) {
			console.log('Error fetching empty form:', error);
		}
	});
}


/**
* Handle Add Dynamic Disaggregation Form
**/
function handleDisaggregationReportForms(indicatorsSelect, selectedID, locationsReportPrefixes=[]) {
    // Extract activity index from indicatorsSelect name attribute
	const activityReportIndex = (indicatorsSelect.name).match(/activityplanreport_set-(\d+)/)[1];
    // Get all target location forms
    var locationReportForms = $(`#report_locations-activityplanreport_set-${activityReportIndex} .target_location_form`);
	
    // Extract locations prefixes from target location forms
	if (locationsReportPrefixes.length === 0){
		locationReportForms.each(function(index, element) {
			var locationReportPrefix = $(element).data("location-prefix");
			locationsReportPrefixes.push(locationReportPrefix);
		});
	}
	
	// Use JavaScript Cookie library
	const csrftoken = Cookies.get('csrftoken');
	
    // Make AJAX request to fetch disaggregation forms
    $.ajax({
        url: '/ajax/get_disaggregations_report_forms/',
        data: {'indicator': selectedID, 'locations_prefixes': locationsReportPrefixes},
        type: 'POST',
        dataType: 'json',
		beforeSend: function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken);
		},
        success: function (data) {
            if (data) {
				$.each(locationsReportPrefixes, function(locationIndex) {
					const locationReportPrefix = locationsReportPrefixes[locationIndex];
                    const disaggregationFormsArray = data[locationReportPrefix];
					
                    // Remove existing forms
                    $('#' + locationReportPrefix).find('.location-inner-holder').remove();
					
                    if (disaggregationFormsArray) {
						// Append new disaggregation forms
                        $('#' + locationReportPrefix).find('.disaggregation-accordion-slide').append(disaggregationFormsArray.join(" "));
                    }
					
                    // Update the management form values
                    if (disaggregationFormsArray) {
                        const managementForm = $(`input[name="disaggregation_report_${locationReportPrefix}-TOTAL_FORMS"]`);
                        const totalForms = parseInt(disaggregationFormsArray.length);
                        managementForm.val(totalForms.toString());
                    }
					// Open/Activate the accordion
					const parentDiv = $('#' + locationReportPrefix).find('.disaggregation-accordion-slide')
					const innerHolder = parentDiv.closest('.inner-holder')

					// Unbind any existing click events
					innerHolder.find('.disaggregation-accordion-opener').off('click');
					innerHolder.find('.disaggregation-accordion-opener').on('click', function(event) {
						event.preventDefault(); // Prevent the default behavior
						event.stopPropagation(); // Prevent the default behavior (propagation)
						innerHolder.toggleClass('disaggregation-accordion-active')
						parentDiv.toggleClass('js-acc-hidden')
						// parentDiv.slideToggle(DETAILS_TOGGLE_DURATION);
					});
                });
            }
        },
        error: function (error) {
            console.log('Error fetching empty form:', error);
        }
    });
}


/**
* Get Districts and Zpnes for Target Location Form
**/
function getLocations(locationPrefix, locationType, parentType, clearZone = null) {
    // Get the URL for fetching locations
    const locationUrl = $(`#id_${locationPrefix}-${locationType}`).attr(`target-locations-queries-url`);
    
    // Get an array of location IDs
    const locationIds = $(`select#id_${locationPrefix}-${locationType} option`)
        .map((_, option) => option.value)
        .get();

    // Get the parent IDs
    const parentIds = [$(`#id_${locationPrefix}-${parentType}`).val()];

    // Get the selected locations
    const selectedLocations = $(`select#id_${locationPrefix}-${locationType}`).val();

    
	try {
		if (locationUrl) {
			// Use JavaScript Cookie library
			const csrftoken = Cookies.get('csrftoken');

			// Make an AJAX request to fetch locations data
			$.ajax({
				type: "POST",
				url: locationUrl,
				data: {
					parents: parentIds,
					listed_locations: locationIds,
				},
				beforeSend: function (xhr, settings) {
					xhr.setRequestHeader("X-CSRFToken", csrftoken);
				},
				success: function (data) {

					// Clear zone if needed
					if (parentType === 'province' && clearZone === true) {
						$(`#id_${locationPrefix}-zone`).html('').val('');
					}
					if (data){
						// Update the location select element
						$(`#id_${locationPrefix}-${locationType}`).html(data);
						$(`select#id_${locationPrefix}-${locationType}`).val(selectedLocations);
					}

				},
				error: function (error) {
					console.log('Error fetching empty form:', error);
				}
			});
		}
	} catch (error) {
		console.error(`Error fetching ${locationType}: ${error}`);
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
	let $facilityId = $formElement.find(`#id_${locationPrefix}-facility_id`);
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
	
	// Button to handle addition of new target location form.
	$(document).on('click', '.add-target-location-form-button', function(event) {
		event.preventDefault(); // Prevent the default behavior (form submission)
		event.stopPropagation(); // Prevent the default behavior (propagation)
		const activityReportFormPrefix = event.currentTarget.dataset.formPrefix
		const activityProject = event.currentTarget.dataset.project
		const activityReportFormIndex = activityReportFormPrefix.match(/\d+/)[0]
		addTargetLocationReportForm(activityReportFormPrefix, activityProject, activityReportFormIndex); // Call the function to add a new activity form
	});

	const $locationBlock = $(".location_report_form");
	$locationBlock.each(function (formIndex, formElement) {

		const locationReportPrefix = formElement.dataset.locationPrefix

		// Update the Target Locations Titles
		// updateLocationBlockTitles(locationReportPrefix);

		// Initial load for districts and zones
		getLocations(locationReportPrefix, 'district', 'province');
		getLocations(locationReportPrefix, 'zone', 'district');

		$(`#id_${locationReportPrefix}-province`).on('change', function() {
			getLocations(locationReportPrefix, 'district', 'province', clearZone=true);
		});
		$(`#id_${locationReportPrefix}-district`).on('change', function() {
			getLocations(locationReportPrefix, 'zone', 'district');
		});

		// Call Facility Monitoring function when page loads.
		handleFacilityMonitoring(locationReportPrefix, formElement);
		
		let $facilityMonitoring = $(formElement).find(
			`#id_${locationReportPrefix}-facility_monitoring`
		);
		$facilityMonitoring.change(function () {
			handleFacilityMonitoring(locationReportPrefix, formElement);
		});
	});

});
