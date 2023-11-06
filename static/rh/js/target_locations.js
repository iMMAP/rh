// Constant for the duration of the slideToggle animations
const TOGGLE_DURATION = 500;

$(function () {
	async function getLocations(formIndex, locationType, parentType, clearZone=null) {
		const locationUrl = $(`#id_form-${formIndex}-${locationType}`).attr(`locations-queries-url`);
		const locationIds = $(`select#id_form-${formIndex}-${locationType} option`)
		  .map((_, option) => option.value)
		  .get();
		const parentIds = [$(`#id_form-${formIndex}-${parentType}`).val()];
	  
		const selectedLocations = $(`select#id_form-${formIndex}-${locationType}`).val();
	  
		try {
		  const response = await $.ajax({
			type: "GET",
			url: locationUrl,
			data: {
			  parents: parentIds,
			  listed_locations: locationIds,
			},
		  });
	  
		  if (parentType === 'province' && clearZone === true) {
			$(`#id_form-${formIndex}-zone`).html('').val('');
		  }
		  $(`#id_form-${formIndex}-${locationType}`).html(response);
		  $(`select#id_form-${formIndex}-${locationType}`).val(selectedLocations);
		} catch (error) {
		  console.error(`Error fetching ${locationType}: ${error}`);
		}
	}
	  
	function updateLocationBlockTitles(formIndex) {
		updateTitle(`form-${formIndex}`, `id_form-${formIndex}-province`);
		updateTitle(`form-${formIndex}`, `id_form-${formIndex}-district`);
		updateTitle(`form-${formIndex}`, `id_form-${formIndex}-site_name`);
	}

	const $locationBlockHolder = $(".location-block-holder");
	$locationBlockHolder.on("change", function (event) {
		event.preventDefault();

		const $formElement = $(this);
		const formIndex = $(this).attr("data-form-id").split("form-")[1];

		// Handle Site Monitoring Checkbox
		if (event.target.name.indexOf("site_monitoring") >= 0) {
			handleSiteMonitoring($formElement, formIndex)
		}
	});
	$.fn.reverse = [].reverse;
	$locationBlockHolder.reverse().each(function (formIndex, formElement) {
		// Call updateTitle for activity_domain manually as on page load as it is not triggered for
		// activity_domain
		updateLocationBlockTitles(formIndex);

		// Initial load for districts and zones
		getLocations(formIndex, 'district', 'province');
		getLocations(formIndex, 'zone', 'district');

		$(`#id_form-${formIndex}-province`).change(function () {
			getLocations(formIndex, 'district', 'province', clearZone=true);
		});
		$(`#id_form-${formIndex}-district`).change(function () {
			getLocations(formIndex, 'zone', 'district');
		});
		
		handleSiteMonitoring($(formElement), formIndex)
	});
});

/**
Updates the titles of the activity form sections based on the selected values of the input element.
@param {string} formPrefix - The prefix of the activity form sections.
@param {string} inputElementId - The ID of the input element that triggered the update.
**/
function updateTitle(formPrefix, inputElementId) {
	const selectedValue = $("#" + inputElementId).val();
	const selectedText = $("#" + inputElementId + " option:selected").text();

	const titleElements = {
		province: $("#title-province-" + formPrefix),
		district: $("#title-district-" + formPrefix),
		site_name: $("#title-site_name-" + formPrefix),
	};

	for (const [key, value] of Object.entries(titleElements)) {
		if (inputElementId.includes(key)) {
			var matches = selectedValue.match(/\d+/g);
			if (matches != null) {
				value.text(selectedValue ? selectedText + ", " : "");
			} else {
				value.text(selectedValue ? selectedValue : "");
			}
		}
	}
}


/**
* Handle Facility Monitoring field
@param {string} formElement - Form Element.
@param {string} formIndex - Form Index.
**/
function handleSiteMonitoring($formElement, formIndex) {
	let $siteMonitoring = $formElement.find(
		`#id_form-${formIndex}-site_monitoring`
	);
	let $siteName = $formElement.find(
		`#id_form-${formIndex}-site_name`
	);
	let $siteLat = $formElement.find(`#id_form-${formIndex}-site_lat`);
	let $siteLong = $formElement.find(`#id_form-${formIndex}-site_long`);
	let $siteDetails = $formElement.find(
		`#form-${formIndex}_site_details`
	);
	if (!$siteMonitoring.is(":checked")) {
		$siteDetails.hide(TOGGLE_DURATION);
		$siteName.prop("required", false).removeClass("is-required");
		$siteLat.prop("required", false).removeClass("is-required");
		$siteLong.prop("required", false).removeClass("is-required");
	} else {
		$siteDetails.show(TOGGLE_DURATION);
		$siteName.prop("required", true).addClass("is-required");
		$siteLat.prop("required", true).addClass("is-required");
		$siteLong.prop("required", true).addClass("is-required");
	}
}