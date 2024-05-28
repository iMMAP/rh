var DETAILS_TOGGLE_DURATION = 500
/**
* Handle Add Dynamic Target Location Report Form
**/
function addTargetLocationReportForm(prefix, project, nextFormIndex, activityDomain, activityPlan) {
	const activityReportFormPrefix = prefix
	const projectID = project

	// Use JavaScript Cookie library
	$.ajax({
		url: '/ajax/get_location_report_empty_form/',
		data: {'prefix_index': nextFormIndex, 'project': projectID, 'activity_domain': activityDomain, 'activity_plan': activityPlan},
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
				});

				if (addedForm){
					const locationReportPrefix = addedForm[0].dataset.locationPrefix
										
					// 	// Update disaggregations based on indicators for the new added form 
					const activityReportFormIndex = formPrefix.match(/activityplanreport_set-(\d+)/)[1] 
					var $indicator = $(`#id_activityplanreport_set-${activityReportFormIndex}-indicator`);
					if ($indicator){
						let selectedID = $indicator[0].value;
						handleDisaggregationReportForms($indicator[0], selectedID, [locationReportPrefix])
					}

					// Handle Target Location fields.
					let $targetLocation = $(addedForm).find(`#id_${locationReportPrefix}-target_location`);
					$targetLocation.change(function () {
						var targetLocationId = $(this).val();
						autoPopulateTargetLocationReport(targetLocationId, locationReportPrefix, addedForm);
					});
					
					// Hide Facility Details when new form is added
					let facilityDetails = addedForm.find(`#facility_details_${locationReportPrefix}`);
					facilityDetails.hide()
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
	
	// Use the global csrftoken variable
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
* Handle Auto-population of target location report fields.
@param {string} locationPrefix - Form Location Prefix.
@param {string} formElement - Form Element.
**/
function autoPopulateTargetLocationReport(targetLocationId, locationPrefix, formElement) {
	formElement = $(formElement)	
	locationPrefix = locationPrefix
	$.ajax({
		url: '/ajax/get_target_location_auto_fields/',
		data: {'target_location': targetLocationId},
		type: 'POST',
		dataType: 'json',
		beforeSend: function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken);
		},
		success: function (data) {
			let country = formElement.find(`#id_${locationPrefix}-country`);
			let province = formElement.find(`#id_${locationPrefix}-province`);
			let district = formElement.find(`#id_${locationPrefix}-district`);
			let zone = formElement.find(`#id_${locationPrefix}-zone`);
			let facility_site_type = formElement.find(`#id_${locationPrefix}-facility_site_type`);
			let facility_monitoring = formElement.find(`#id_${locationPrefix}-facility_monitoring`);
			let facility_name = formElement.find(`#id_${locationPrefix}-facility_name`);
			let facility_id = formElement.find(`#id_${locationPrefix}-facility_id`);
			let facility_lat = formElement.find(`#id_${locationPrefix}-facility_lat`);
			let facility_long = formElement.find(`#id_${locationPrefix}-facility_long`);
			let nhs_code = formElement.find(`#id_${locationPrefix}-nhs_code`);
			let facilityDetails = formElement.find(`#facility_details_${locationPrefix}`);

			country.val(data.country);
			province.val(data.province);
			district.val(data.district);
			zone.val(data.zone);
			facility_site_type.val(data.facility_site_type);
			facility_monitoring.prop('checked', data.facility_monitoring);
			nhs_code.val(data.nhs_code);
			
			
			if (data.facility_monitoring){
				facilityDetails.show();
				facility_name.val(data.facility_name);
				facility_id.val(data.facility_id);
				facility_lat.val(data.facility_lat);
				facility_long.val(data.facility_long);
			}else{
				facilityDetails.hide();
			}
		},
		error: function (error) {
			console.log('Error fetching empty form:', error);
		}
	});
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
		const activityDomain = event.currentTarget.dataset.activityDomain
		const activityPlan = event.currentTarget.dataset.activityPlan
		const activityReportFormIndex = activityReportFormPrefix.match(/\d+/)[0]
		addTargetLocationReportForm(activityReportFormPrefix, activityProject, activityReportFormIndex, activityDomain, activityPlan); // Call the function to add a new activity form
	});

	const $locationBlock = $(".location_report_form");
	$locationBlock.each(function (formIndex, formElement) {
		const locationReportPrefix = formElement.dataset.locationPrefix

		// autoPopulateTargetLocationReport(locationReportPrefix, formElement);
		let $targetLocation = $(formElement).find(
			`#id_${locationReportPrefix}-target_location`
		);
		$targetLocation.change(function () {
			var targetLocationId = $(this).val();
			autoPopulateTargetLocationReport(targetLocationId, locationReportPrefix, formElement);
		});
	});

});
