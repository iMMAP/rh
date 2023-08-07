// Constant for the duration of the slideToggle animations
const TOGGLE_DURATION = 500;

/**
* Handle Add Dynamic Activity Form
**/
function addActivityForm(prefix, project, nextFormIndex) {
	// Get the empty form template
	const activityFormPrefix = prefix
	const projectID = project

	$.ajax({
		url: '/ajax/get_activity_empty_form/',
		data: {'project': projectID, 'prefix_index': nextFormIndex},
		type: 'GET',
		dataType: 'json',
		success: function (data) {
			if (data.html) {

				const emptyFormTemplate = data.html

				// Get the formset container
				const formsetContainer = $("#activity-formset");
				
				// Get the number of existing forms
				const formIdx = formsetContainer.children().length; 
			
				// Replace the form prefix placeholder with the actual form index in the template HTML
				const newFormHtml = emptyFormTemplate.replace(/__prefix__/g, formIdx);
			
				// Create a new form element and append it to the formset container
				const newForm = $(document.createElement('div')).html(newFormHtml);
				formsetContainer.append(newForm.children().first());

				setTimeout(function () {
					// Initialize chained and chainedm2m fields for the newly added form
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
			
					const indicatorsSelect = $(`select[id^='id_activityplan_set-${formIdx}-indicators']`);
					const IndicatorsUrl = indicatorsSelect.data('url');
					const IndicatorsID = "#" + indicatorsSelect.attr('id');
					chainedm2m.init(activityTypeSelectID, IndicatorsUrl, IndicatorsID, '', '--------', true);
					$(IndicatorsID).select2();

					// TODO: Handle the Locations dropdown for the new form as well.
			
				}, 100);
				
			}
		},
		error: function (error) {
			console.log('Error fetching empty form:', error);
		}
	});

	// Update the management form values
	const managementForm = $(`input[name="${activityFormPrefix}-TOTAL_FORMS"]`);
	const totalForms = parseInt(managementForm.val()) + 1;
	managementForm.val(totalForms.toString());	
}


/**
* Handle Add Dynamic Activity Form
**/
function addTargetLocationForm(prefix, project, nextFormIndex) {
	// Get the empty form template
	// const emptyFormTemplate = $(`#empty-target-location-form-template-${activityFormPrefix}`);
	const activityFormPrefix = prefix
	const projectID = project
	$.ajax({
		url: '/ajax/get_target_location_empty_form/',
		data: {'project': projectID, 'prefix_index': nextFormIndex},
		type: 'GET',
		dataType: 'json',
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
				
				// Create a new form element and prepend it to the formset container
				const newForm = $(document.createElement('div')).html(newFormHtml);
				formsetContainer.append(newForm.children().first());

				// Update the management form values
				const managementForm = $(`input[name="target_locations_${formPrefix}-TOTAL_FORMS"]`);
				const totalForms = parseInt(managementForm.val()) + 1;
				managementForm.val(totalForms.toString());
				
				// Open/Activate the accordion
				const parentDiv = formsetContainer.closest('.target_location-accordion-slide')
				parentDiv.removeClass('js-acc-hidden')
				parentDiv.closest('.inner-holder').addClass('target_location-accordion-active')
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
function handleDisaggregationForms(indicatorsSelect, selectedIDs) {
    // Extract activity index from indicatorsSelect name attribute
    const activityIndex = (indicatorsSelect.name).match(/activityplan_set-(\d+)/)[1];

    // Get all target location forms
    var targetLocationForms = $(`#Locations-activityplan_set-${activityIndex} .target_location_form`);

    // Extract locations prefixes from target location forms
    var locationsPrefixes = [];
    targetLocationForms.each(function(index, element) {
        var locationPrefix = $(element).data("location-prefix");
        locationsPrefixes.push(locationPrefix);
    });

    // Make AJAX request to fetch disaggregation forms
    $.ajax({
        url: '/ajax/get_disaggregations_forms/',
        data: {'indicators': selectedIDs, 'locations_prefixes': locationsPrefixes},
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            if (data) {
                $.each(locationsPrefixes, function(locationIndex) {
                    const locationPrefix = locationsPrefixes[locationIndex];
                    const disaggregationFormsArray = data[locationPrefix];

                    // Remove existing forms
                    $('#' + locationPrefix).find('.location-inner-holder').remove();

                    if (disaggregationFormsArray) {
                        // Append new disaggregation forms
                        $('#' + locationPrefix).find('.disaggregation-accordion-slide').append(disaggregationFormsArray.join(" "));
                    }

                    // Update the management form values
                    if (disaggregationFormsArray) {
                        const managementForm = $(`input[name="disaggregation_${locationPrefix}-TOTAL_FORMS"]`);
                        const totalForms = parseInt(disaggregationFormsArray.length);
                        managementForm.val(totalForms.toString());
                    }
                });
            }
        },
        error: function (error) {
            console.log('Error fetching empty form:', error);
        }
    });
}


/**
Updates the titles of the activity form sections based on the selected values of the input element.
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
        // Make an AJAX request to fetch locations data
        const response = await $.ajax({
            type: "GET",
            url: locationUrl,
            data: {
                parents: parentIds,
                listed_locations: locationIds,
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



$(document).ready(function () {

	// Initialize indicators with django select except the empty form
	$("select[multiple]:not(#id_activityplan_set-__prefix__-indicators)").select2();

	// Button to handle addition of new activity form.
	$('#add-activity-form-button').on('click', function(event) {
		event.preventDefault(); // Prevent the default behavior (form submission)
		const activityFormPrefix = event.currentTarget.dataset.formPrefix
		const activityProject = event.currentTarget.dataset.project
		const nextFormIndex = event.currentTarget.dataset.formsCount
		addActivityForm(activityFormPrefix, activityProject, nextFormIndex); // Call the function to add a new activity form
	});
	
	// Button to handle addition of new target location form.
	$(document).on('click', '.add-target-location-form-button', function(event) {
		event.preventDefault(); // Prevent the default behavior (form submission)
		event.stopPropagation(); // Prevent the default behavior (propagation)
		const activityFormPrefix = event.currentTarget.dataset.formPrefix
		const activityProject = event.currentTarget.dataset.project
		const activityFormIndex = activityFormPrefix.match(/\d+/)[0]
		addTargetLocationForm(activityFormPrefix, activityProject, activityFormIndex); // Call the function to add a new activity form
	});

	let $activityBlockHolder = $(".activity_form");
	$activityBlockHolder.each(function (formIndex, formElement) {
		
		// Call updateTitle for activity_domain manually as on page load as it is not triggered for
		updateTitle(`activityplan_set-${formIndex}`, `id_activityplan_set-${formIndex}-activity_domain`);

		// Update disaggregations based on indicators
		/*$('.select2-selection--multiple').ready(function(){
			debugger
			let selectedIDs = $select2Event[0].dataset.value
			handleDisaggregationForms($select2Event[0], JSON.parse(selectedIDs))
		});*/
		
		// Update disaggregations based on indicators
		var $select2Event = $(`#id_activityplan_set-${formIndex}-indicators`);
		$select2Event.on("change.select2", function (event) { 
			let indicatorsSelect = event.currentTarget
			let selectedIDs = $(indicatorsSelect).select2('data').map(item => item.id);
			handleDisaggregationForms(indicatorsSelect, selectedIDs)
		});
	});

	const $locationBlock = $(".target_location_form");
	$locationBlock.each(function (formIndex, formElement) {
		// Call updateTitle for activity_domain manually as on page load as it is not triggered for
		// activity_domain
		// updateLocationBlockTitles(formIndex);
		
		const locationPrefix = formElement.dataset.locationPrefix


		// Initial load for districts and zones
		getLocations(locationPrefix, 'district', 'province');
		getLocations(locationPrefix, 'zone', 'district');
		

		$(`#id_${locationPrefix}-province`).change(function () {
			getLocations(locationPrefix, 'district', 'province', clearZone=true);
		});
		$(`#id_${locationPrefix}-district`).change(function () {
			getLocations(locationPrefix, 'zone', 'district');
		});
		
		// handleSiteMonitoring($(formElement), formIndex)
	});

});
