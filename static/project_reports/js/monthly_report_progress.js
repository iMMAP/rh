debugger
/**
* Handle Add Dynamic Target Location Report Form
**/
function addTargetLocationReportForm(prefix, project, nextFormIndex) {
	const activityFormPrefix = prefix
	const projectID = project

	// Use JavaScript Cookie library
	const csrftoken = Cookies.get('csrftoken');

	$.ajax({
		url: '/ajax/get_target_location_empty_form/',
		data: {'project': projectID, 'prefix_index': nextFormIndex},
		type: 'POST',
		dataType: 'json',
		beforeSend: function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken);
		},
		success: function (data) {
			if (data.html) {

				const emptyFormTemplate = data.html
				
				// Get the formset prefix
				const formPrefix = activityFormPrefix; 
				
				// Get the formset container
				const formsetContainer = $(`#${formPrefix}`);

				// Get the number of existing forms
				const formIdx = formsetContainer.children().length; // Get the number of existing forms
				
				// Replace the form prefix placeholder with the actual form index in the template HTML
				const newFormHtml = emptyFormTemplate.replace(/__prefix__/g, formIdx);
				
				// Create a new form element and append it to the formset container
				const newForm = $(document.createElement('div')).html(newFormHtml);
				const addedForm = newForm.children().first()
				formsetContainer.append(addedForm);

				// Update the management form values
				const managementForm = $(`input[name="target_locations_${formPrefix}-TOTAL_FORMS"]`);
				const totalForms = parseInt(managementForm.val()) + 1;
				managementForm.val(totalForms.toString());
				
				// Open/Activate the accordion
				const parentDiv = formsetContainer.closest('.location_accordion_slide')
				const innerHolder = parentDiv.closest('.inner-holder')

				// Unbind any existing click events
				innerHolder.find('.location_accordion_opener').off('click');
				innerHolder.find('.location_accordion_opener').click(function(event) {
					event.preventDefault(); // Prevent the default behavior (form submission)
					event.stopPropagation(); // Prevent the default behavior (propagation)
					$(this).next('.location_accordion_slide').slideToggle(DETAILS_TOGGLE_DURATION);
				});

				if (addedForm){
					const locationPrefix = addedForm[0].dataset.locationPrefix
					// Load Locations (districts and zones)
					getLocations(locationPrefix, 'district', 'province');
					getLocations(locationPrefix, 'zone', 'district');
					
					// Add Load Locations (districts and zones) event for new form
					$(`#id_${locationPrefix}-province`).change(function () {
						getLocations(locationPrefix, 'district', 'province', clearZone=true);
					});
					$(`#id_${locationPrefix}-district`).change(function () {
						getLocations(locationPrefix, 'zone', 'district');
					});
					
					// Update disaggregations based on indicators for the new added form 
					const activityFormIndex = formPrefix.match(/activityplan_set-(\d+)/)[1] 
					var $select2Event = $(`#id_activityplan_set-${activityFormIndex}-indicators`);
					if ($select2Event){
						let selectedIDs = $select2Event.select2('data').map(item => item.id);
						handleDisaggregationReportForms($select2Event[0], selectedIDs, [locationPrefix])
					}

					// Update change event on indicators for the new added form 
					$select2Event.on("change.select2", function (event) { 
						let indicatorsSelect = event.currentTarget
						let selectedIDs = $(indicatorsSelect).select2('data').map(item => item.id);
						handleDisaggregationReportForms(indicatorsSelect, selectedIDs, [locationPrefix])
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
function handleDisaggregationReportForms(indicatorsSelect, selectedIDs, locationsPrefixes=[]) {
    // Extract activity index from indicatorsSelect name attribute
    const activityIndex = (indicatorsSelect.name).match(/activityplan_set-(\d+)/)[1];
    // Get all target location forms
    var targetLocationForms = $(`#Locations-activityplan_set-${activityIndex} .target_location_form`);
	
    // Extract locations prefixes from target location forms
	if (locationsPrefixes.length === 0){
		targetLocationForms.each(function(index, element) {
			var locationPrefix = $(element).data("location-prefix");
			locationsPrefixes.push(locationPrefix);
		});
	}

	// Use JavaScript Cookie library
	const csrftoken = Cookies.get('csrftoken');

    // Make AJAX request to fetch disaggregation forms
    $.ajax({
        url: '/ajax/get_disaggregations_forms/',
        data: {'indicators': selectedIDs, 'locations_prefixes': locationsPrefixes},
        type: 'POST',
        dataType: 'json',
		beforeSend: function(xhr, settings) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken);
		},
        success: function (data) {
            if (data) {
                $.each(locationsPrefixes, function(locationIndex) {
                    const locationPrefix = locationsPrefixes[locationIndex];
                    const disaggregationFormsArray = data[locationPrefix];

                    // Remove existing forms
                    $('#' + locationPrefix).find('.location-inner-holder').remove();

                    if (disaggregationFormsArray) {
                        // Append new disaggregation forms
                        $('#' + locationPrefix).find('.disaggregation_accordion_slide').append(disaggregationFormsArray.join(" "));
                    }

                    // Update the management form values
                    if (disaggregationFormsArray) {
                        const managementForm = $(`input[name="disaggregation_${locationPrefix}-TOTAL_FORMS"]`);
                        const totalForms = parseInt(disaggregationFormsArray.length);
                        managementForm.val(totalForms.toString());
                    }
					// Open/Activate the accordion
					const parentDiv = $('#' + locationPrefix).find('.disaggregation_accordion_slide')
					const innerHolder = parentDiv.closest('.inner-holder')

					// Unbind any existing click events
					innerHolder.find('.disaggregation_accordion_opener').off('click');
					innerHolder.find('.disaggregation_accordion_opener').click(function(event) {
						event.preventDefault(); // Prevent the default behavior
						event.stopPropagation(); // Prevent the default behavior (propagation)
						parentDiv.slideToggle(DETAILS_TOGGLE_DURATION);
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
async function getLocations(locationPrefix, locationType, parentType, clearZone = null) {
    // Get the URL for fetching locations
    const locationUrl = $(`#id_${locationPrefix}-${locationType}`).attr(`locations-queries-url`);
    
    // Get an array of location IDs
    const locationIds = $(`select#id_${locationPrefix}-${locationType} option`)
        .map((_, option) => option.value)
        .get();

    // Get the parent IDs
    const parentIds = [$(`#id_${locationPrefix}-${parentType}`).val()];

    // Get the selected locations
    const selectedLocations = $(`select#id_${locationPrefix}-${locationType}`).val();

    try {

		// Use JavaScript Cookie library
		const csrftoken = Cookies.get('csrftoken');

        // Make an AJAX request to fetch locations data
        const response = await $.ajax({
            type: "POST",
            url: locationUrl,
            data: {
                parents: parentIds,
                listed_locations: locationIds,
            },
			beforeSend: function(xhr, settings) {
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			},
        });

        // Clear zone if needed
        if (parentType === 'province' && clearZone === true) {
            $(`#id_${locationPrefix}-zone`).html('').val('');
        }

        // Update the location select element
        $(`#id_${locationPrefix}-${locationType}`).html(response);
        $(`select#id_${locationPrefix}-${locationType}`).val(selectedLocations);
    } catch (error) {
        console.error(`Error fetching ${locationType}: ${error}`);
    }
}


/**
* Ready Function
**/
$(document).ready(function () {
	
	// Button to handle addition of new target location form.
	$(document).on('click', '.add-target-location-form-button', function(event) {
		event.preventDefault(); // Prevent the default behavior (form submission)
		event.stopPropagation(); // Prevent the default behavior (propagation)
		const activityFormPrefix = event.currentTarget.dataset.formPrefix
		const activityProject = event.currentTarget.dataset.project
		const activityFormIndex = activityFormPrefix.match(/\d+/)[0]
		addTargetLocationReportForm(activityFormPrefix, activityProject, activityFormIndex); // Call the function to add a new activity form
	});

	let $activityBlockHolder = $(".activity_form");
	$activityBlockHolder.each(function (formIndex, formElement) {
		
		// Update disaggregations based on indicators
		var $select2Event = $(`#id_activityplan_set-${formIndex}-indicators`);
		$select2Event.on("change.select2", function (event) { 
			let indicatorsSelect = event.currentTarget
			let selectedIDs = $(indicatorsSelect).select2('data').map(item => item.id);
			handleDisaggregationReportForms(indicatorsSelect, selectedIDs)
		});
	});

	const $locationBlock = $(".target_location_form");
	$locationBlock.each(function (formIndex, formElement) {

		const locationPrefix = formElement.dataset.locationPrefix

		// Update the Target Locations Titles
		updateLocationBlockTitles(locationPrefix);

		// Initial load for districts and zones
		getLocations(locationPrefix, 'district', 'province');
		getLocations(locationPrefix, 'zone', 'district');

		$(`#id_${locationPrefix}-province`).change(function () {
			getLocations(locationPrefix, 'district', 'province', clearZone=true);
		});
		$(`#id_${locationPrefix}-district`).change(function () {
			getLocations(locationPrefix, 'zone', 'district');
		});
		
	});

});
