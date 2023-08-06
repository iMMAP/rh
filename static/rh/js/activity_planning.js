// Constant for the duration of the slideToggle animations
const TOGGLE_DURATION = 500;

/**
* Handle Add Dynamic Activity Form
**/
function addActivityForm(prefix, project, nextFormIndex) {
	// Get the empty form template
	debugger
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
		const activityFormPrefix = event.currentTarget.dataset.formPrefix
		const activityProject = event.currentTarget.dataset.project
		const nextFormIndex = event.currentTarget.dataset.formsCount
		addActivityForm(activityFormPrefix, activityProject, nextFormIndex); // Call the function to add a new activity form
	});
	
	// Button to handle addition of new activity form.
	$(document).on('click', '.add-target-location-form-button', function(event) {
		event.preventDefault(); // Prevent the default behavior (form submission)
		event.stopPropagation(); // Prevent the default behavior (propagation)
		const activityFormPrefix = event.currentTarget.dataset.formPrefix
		const activityProject = event.currentTarget.dataset.project
		const activityFormIndex = activityFormPrefix.match(/\d+/)[0]
		addTargetLocationForm(activityFormPrefix, activityProject, activityFormIndex); // Call the function to add a new activity form
	});

	

	// $(document).on("click", ".select2-search__field", function(event) {
	// 	event.preventDefault();
	// 	event.stopPropagation()
	// 	debugger

	// });
	

	$.fn.reverse = [].reverse;
	let $activityBlockHolder = $(".activity-block-holder");
	$activityBlockHolder.reverse().each(function (formIndex, formElement) {
		// Call updateTitle for activity_domain manually as on page load as it is not triggered for
		// activity_domain
		updateTitle(`activityplan_set-${formIndex}`, `id_activityplan_set-${formIndex}-activity_domain`);

		var $select2Event = $(`#id_activityplan_set-${formIndex}-indicators`);
		$select2Event.on("select2:select", function (event) { 
			let indicatorsSelect = event.currentTarget
			let selectedIDs = $(indicatorsSelect).select2('data').map(item => item.id);
			$.ajax({
				url: '/ajax/get_disaggregations_forms/',
				data: {'indicators': selectedIDs},
				type: 'GET',
				dataType: 'json',
				success: function (data) {
					if (data.html) {
						debugger
		
						
					}
				},
				error: function (error) {
					console.log('Error fetching empty form:', error);
				}
			});


			console.log("select2:select", selectedIDs); 
		});
	
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
