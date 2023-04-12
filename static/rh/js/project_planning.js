$(document).ready(function() {

    const isHrpProject = $("#id_is_hrp_project");
    const hasHrpCode = $("#id_has_hrp_code");
    const prHasHRPCodeEl = $("#prHasHRPCodeEl");
    const prHrpCode = $("#prHrpCode");
    const idHrpCode = $("#id_hrp_code");

    /**
    * Initiate the Select2 widget
    */
    $('.js_multiselect').select2();

    /**
    * Toggles the display of the HRP code form field based on whether the 'isHrpProject'
    * checkbox is checked or not. If checked, the HRP code form field and corresponding
    * label are displayed. Otherwise, the HRP code field is hidden, its value is reset,
    * and the 'hasHrpCode' checkbox is unchecked.
    */
    function toggleHrpCode() {
        if (isHrpProject.is(":checked")) {
            prHasHRPCodeEl.show(300);
        } else {
            prHrpCode.hide(200);
            idHrpCode.val('');
            prHasHRPCodeEl.hide(200);
            hasHrpCode.prop('checked', false);
        }
    }

    /**
    * Toggles the "required" attribute and "is-required" class of the project HRP code field
      based on whether the "has HRP code" checkbox is checked or not.
    * If the checkbox is checked, the HRP code field is shown,
      made required and the "is-required" class is added.
    * If the checkbox is unchecked, the HRP code field is hidden,
      its value is cleared, the "required" attribute is removed, and the "is-required" class is removed.
    */
    function toggleRequired() {
        if (hasHrpCode.is(":checked")) {
            prHrpCode.show(300);
            prHrpCode.prop('required', true);
            prHrpCode.addClass("is-required");
        } else {
            prHrpCode.hide(200);
            idHrpCode.val('');
            prHrpCode.prop('required', false);
            prHrpCode.removeClass("is-required");
        }
    }

    toggleHrpCode();
    toggleRequired();
    isHrpProject.change(toggleHrpCode);
    hasHrpCode.change(toggleRequired);


    /**
    * Retrieves activities based on selected clusters and listed activities
    */
    function getActivities() {
        // Retrieve the URL for the AJAX request
        const activitiesUrl = $("#id_activities").attr("activities-queries-url");

        // Retrieve the IDs of all listed activities
        const activityIds = $("select#id_activities option").map(function() {
            return $(this).val();
        }).get();

        // Retrieve the IDs of all selected clusters
        const clusterIds = $("#id_clusters").val();

        // Retrieve the currently selected activities
        const selectedActivities = $("select#id_activities").val();

        // Send an AJAX request to the server to retrieve the activities
        $.ajax({
            type: 'GET',
            url: activitiesUrl,
            data: {
              clusters: clusterIds,
              listed_activities: activityIds,
            },
            success: function (data) {
                // Replace the contents of the activities select box with the retrieved data
                $("#id_activities").html(data);

                // Set the selected activities back to their original values
                $("select#id_activities").val(selectedActivities);
            }
        });
    };


    /**
    * Retrieves districts based on selected and listed provinces
    */
    function get_districts() {
        const districtsUrl = $("#id_districts").attr("districts-queries-url");
        const districtIds = $("#id_districts option").map(function() {
            return $(this).val();
        }).get();

        const provinceIds = $("#id_provinces").val();
        const selectedDistricts = $("#id_districts").val();

        $.ajax({
            type: 'GET',
            url: districtsUrl,
            data: {
              provinces: provinceIds,
              listed_districts: districtIds,
            },
            success: function(data) {
              const $districts = $("#id_districts");
              $districts.html(data);
              $districts.val(selectedDistricts);
            }
        });
    }

    $(document).ready(function() {
      get_districts();
    });

    $("#id_provinces").change(function() {
      get_districts();
    });

});