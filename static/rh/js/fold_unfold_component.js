const DETAILS_TOGGLE_DURATION = 500;

// jQuery's shorthand document ready function
$(function() {
    // Loop through all elements with the class 'js-collapse-expand'
    // and initialize them as unfolded using the 'foldUnfoldDetails' function.
    $('.js-collapse-expand').each(function(formIndex, formElement) {
        foldUnfoldDetails(`form-${formIndex}`, false, );
    });

    // Attach click event handler to all elements with class 'collapse-details'
    $(document).on('click', '.collapse-details', function(e) {
        e.preventDefault();
        const parentElement = $(this).closest('.js-collapse-expand');  // find closest parent element
        const formIndex = parentElement.attr('data-form-id'); // get the value of 'data-form-id'
        foldUnfoldDetails(formIndex); // call the function to fold/unfold the details
    });

    // Attach click event handler to detail element with class 'fold-unfold-all-details'
    $(document).on('click', '.fold-unfold-all-details', function(e) {
        e.preventDefault();
        const allCollapsed = !$('#fold-icon-down').hasClass('hidden');
        $('.js-collapse-expand').each(function(formIndex, formElement) {
            foldUnfoldDetails(`form-${formIndex}`, allCollapsed);
        });
        $('#fold-icon-up, #fold-icon-down, #all-fold, #all-unfold').toggleClass('hidden');
    });
});

/**
 * Toggles the visibility of elements based on form index and collapse state.
 *
 * @param {number} formIndex - The index of the form to toggle.
 * @param {boolean} allCollapsed - The collapse state of the form.
 */
function foldUnfoldDetails(formIndex, allCollapsed) {

    // Get the IDs of the elements to be toggled
    const actionsId = `#${formIndex}-actions`;
    const detailsId = `#${formIndex}-details`;
    const upArrowId = `#${formIndex}-up`;
    const downArrowId = `#${formIndex}-down`;
    const foldId = `#${formIndex}-fold`;
    const unFoldId = `#${formIndex}-unfold`;

    /**
    * Toggles the visibility of the actions and details elements, and their icons.
    */
    const toggleElements = () => {
        $(actionsId).slideToggle(DETAILS_TOGGLE_DURATION);
        $(detailsId).slideToggle(DETAILS_TOGGLE_DURATION);
        $(upArrowId).toggleClass('hidden');
        $(downArrowId).toggleClass('hidden');
        $(foldId).toggleClass('hidden');
        $(unFoldId).toggleClass('hidden');
    }

    // If collapse state is not defined, toggle the elements
    if (allCollapsed === undefined) {
        toggleElements();
    }
    // If all forms should be collapsed, hide the details element and corresponding icons
    else if (allCollapsed) {
        if (!$(detailsId).is(':visible')) {
            toggleElements();
        }
    }
    // If all forms should be expanded, show the details element and corresponding icons
    else {
        if ($(detailsId).is(':visible')) {
            toggleElements();
        }
    }
}






