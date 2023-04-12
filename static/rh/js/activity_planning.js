/**
* Initializes facility monitoring form functionality for multiple forms.
* @param {number} currentFormCount - The number of facility monitoring forms currently displayed on the page.
* @returns {void}
*/
$(document).ready(function() {
    $.fn.reverse = [].reverse;
    let $activityBlockHolder = $('.activity-block-holder');
    $activityBlockHolder.reverse().each(function (formIndex, formElement) {

        let $facilityMonitoring = $(formElement).find(`#id_form-${formIndex}-facility_monitoring`);
        let $facilityName = $(formElement).find(`#id_form-${formIndex}-facility_name`);
        let $facilityId = $(formElement).find(`#id_form-${formIndex}-facility_id`);
        let $facilityDetails1 = $(formElement).find(`#form-${formIndex}_facility_details_1`);
        let $facilityDetails2 = $(formElement).find(`#form-${formIndex}_facility_details_2`);

        if (!$facilityMonitoring.is(":checked")) {
            $facilityDetails1.hide();
            $facilityDetails2.hide();
            $facilityName.prop('required', false).removeClass("is-required");
            $facilityId.prop('required', false).removeClass("is-required");
        } else {
            $facilityName.prop('required', true).addClass("is-required");
            $facilityId.prop('required', true).addClass("is-required");
        }
    });

    $activityBlockHolder.on("change", function (event) {
        var $formElement = $(this);
        const formIndex = $(this).attr("data-form-id").split("form-")[1];
        let $facilityMonitoring = $formElement.find(`#id_form-${formIndex}-facility_monitoring`);
        let $facilityName = $formElement.find(`#id_form-${formIndex}-facility_name`);
        let $facilityId = $formElement.find(`#id_form-${formIndex}-facility_id`);
        let $facilityDetails1 = $formElement.find(`#form-${formIndex}_facility_details_1`);
        let $facilityDetails2 = $formElement.find(`#form-${formIndex}_facility_details_2`);

        if (!$facilityMonitoring.is(":checked")) {
            $facilityDetails1.hide();
            $facilityDetails2.hide();
            $facilityName.prop('required', false).removeClass("is-required");
            $facilityId.prop('required', false).removeClass("is-required");
        } else {
            $facilityDetails1.show(300);
            $facilityDetails2.show(300);
            $facilityName.prop('required', true).addClass("is-required");
            $facilityId.prop('required', true).addClass("is-required");
        }

    });

    // Attach a handler to the 'input' event for all number input fields
    $('input[type="number"]').on('input', function() {
        var tableId = $(this).closest('table').attr('id');
//        const tableIndex = tableId.split("form-")[1];
        // Calculate the row total for the current row
        var rowTotal = 0;
        $(this).closest('tr').find('input[type="number"]').each(function() {
            if ($(this).val()) {
                rowTotal += parseInt($(this).val());
            }
        });

        // Set the row total value for the current row and update the displayed value
        $(this).closest('tr').find('.total-row').attr('data-row-total-value', rowTotal).val(rowTotal | 0);


        // Calculate the column total for all number input fields that have a value, reverse the each loop
        // as we are rendering the forms in reversed order
//        $.fn.reverse = [].reverse;
        /*TODO: Handle the total column wise*/
        $(`#${tableId} input[type="number"][step="1"][placeholder="-"][value!=""]`).reverse().each(function(index) {
//        $('input[type="number"][step="1"][placeholder="-"][value!=""]').reverse().each(function(index) {
            var colTotal = 0;
            $(`#${tableId} tbody tr`).each(function() {
                var val = $(this).find('input[type="number"]').eq(index).val();
                if (val) {
                    colTotal += parseInt(val);
                }
            });
//            var tableId = $(this).closest('table').attr('id');
            // Set the column total value for all total cells and update the displayed value

//            $(`.${tableId.replace("-table", "")}-total-col`).eq(index).attr('data-col-total-value', colTotal).val(colTotal);

        });
    });
})


/**
Updates the titles of the activity form sections based on the selected values of the input element.
@param {string} formPrefix - The prefix of the activity form sections.
@param {string} inputElementId - The ID of the input element that triggered the update.
*/
function updateTitle(formPrefix, inputElementId) {
  const selectedValue = $('#' + inputElementId).val();
  const selectedText = $('#' + inputElementId + ' option:selected').text();

  const titleElements = {
    'activity_domain': $('#title-domain-' + formPrefix),
    'activity_type': $('#title-type-' + formPrefix),
    'activity_detail': $('#title-detail-' + formPrefix)
  };

  for (const [key, value] of Object.entries(titleElements)) {
    if (inputElementId.includes(key)) {
      value.text(selectedValue ? selectedText + ', ' : '');
    }
  }
}



