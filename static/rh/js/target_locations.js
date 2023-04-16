
$(document).ready(function() {

    let $locationBlockHolder = $('.location-block-holder');
    $locationBlockHolder.each(function (formIndex, formElement) {

        // Call updateTitle for activity_domain manually as on page load as it is not triggered for
        // activity_domain
        updateTitle(`form-${formIndex}`, `id_form-${formIndex}-province`);
        updateTitle(`form-${formIndex}`, `id_form-${formIndex}-district`);
        updateTitle(`form-${formIndex}`, `id_form-${formIndex}-site_name`);

    });

})



/**
Updates the titles of the activity form sections based on the selected values of the input element.
@param {string} formPrefix - The prefix of the activity form sections.
@param {string} inputElementId - The ID of the input element that triggered the update.
**/
function updateTitle(formPrefix, inputElementId) {
    const selectedValue = $('#' + inputElementId).val();
    const selectedText = $('#' + inputElementId + ' option:selected').text();

    const titleElements = {
        'province': $('#title-province-' + formPrefix),
        'district': $('#title-district-' + formPrefix),
        'site_name': $('#title-site_name-' + formPrefix)
    };

    for (const [key, value] of Object.entries(titleElements)) {
        if (inputElementId.includes(key)) {
            var matches = selectedValue.match(/\d+/g);
            if (matches != null) {
                value.text(selectedValue ? selectedText + ', ' : '');
            }else{
                value.text(selectedValue ? selectedValue : '');
            }
        }
    }
}