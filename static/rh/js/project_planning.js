$(document).ready(function() {

    /**/
    $('.js_multiselect').select2();

    if (!$("#id_is_hrp_project").is(":checked")){
        $("#prHasHRPCodeEl").hide();
    }

    $("#id_is_hrp_project").change(function(){
        if($(this).is(":checked")) {
            $("#prHasHRPCodeEl").show(300);
        } else {

            $("#prHrpCode").hide(200);
            $("#id_hrp_code").val('');

            $("#prHasHRPCodeEl").hide(200);
            $("#id_has_hrp_code").prop('checked', false);
        }
    });

    if (!$("#id_has_hrp_code").is(":checked")){
        $("#prHrpCode").hide();

    }else {
        $("#id_hrp_code").prop('required', true)
        $("#prHrpCode").addClass("is-required");
    }
    $("#id_has_hrp_code").change(function(){
        if($(this).is(":checked")) {
            $("#prHrpCode").show(300);
            $("#prHrpCode").prop('required',true)
            $("#prHrpCode").addClass("is-required");
        } else {
            $("#prHrpCode").hide(200);
            $("#id_hrp_code").val('');
        }
    });

    if (!$("#id_facility_monitoring").is(":checked")){
        $("#facility_details_1").hide();
        $("#facility_details_2").hide();


        $("#id_facility_name").prop('required', true)
        $("#id_facility_id").prop('required', true)
        $("#facility_name").removeClass("is-required");
        $("#facility_id").removeClass("is-required");
    }else {
        $("#id_facility_name").prop('required', false)
        $("#id_facility_id").prop('required', false)
        $("#facility_name").addClass("is-required");
        $("#facility_id").addClass("is-required");
    }

    $("#id_facility_monitoring").change(function(){
        if($(this).is(":checked")) {
            $("#facility_details_1").show(300);
            $("#facility_details_2").show(300);

            $("#id_facility_name").prop('required', true)
            $("#id_facility_id").prop('required', true)
            $("#facility_name").addClass("is-required");
            $("#facility_id").addClass("is-required");
        } else {
            $("#facility_details_1").hide(200);
            $("#facility_details_2").hide(200);
            $("#id_facility_name").val('');
            $("#id_facility_id").val('');
            $("#id_facility_lat").val('');
            $("#id_facility_long").val('');

            $("#id_facility_name").prop('required', false)
            $("#id_facility_id").prop('required', false)
            $("#facility_name").removeClass("is-required");
            $("#facility_id").removeClass("is-required");
        }
    });

    /*$("#prDistricts").hide();
    $("#pr_has_districts").change(function(){
        if($(this).is(":checked")) {
            $("#prDistricts").show(300);
        } else {
            $("#prDistricts").hide(200);
            $("#id_districts").val('');
        }
    });*/

    function get_activities(){
        const activities_url = $("#id_activities").attr("activities-queries-url");
        const activityIds = $("select#id_activities option").map(function() {return $(this).val();}).get();
        const clusterIds = $("#id_clusters").val();
        const selected_activities = $("select#id_activities").val()
        $.ajax({
            type: 'GET',
            url: activities_url,
            data: {
                clusters: clusterIds,
                listed_activities: activityIds,
            },
            success: function (data) {
                $("#id_activities").html(data);
                $("select#id_activities").val(selected_activities);
            }
        });
    }

    function get_districts(){
        const districts_url = $("#id_districts").attr("districts-queries-url");
        const districtIds = $("select#id_districts option").map(function() {return $(this).val();}).get();
        const provinceIds = $("#id_provinces").val();
        const selected_districts = $("select#id_districts").val()
        $.ajax({
            type: 'GET',
            url: districts_url,
            data: {
                provinces: provinceIds,
                listed_districts: districtIds,
            },
            success: function (data) {
                $("#id_districts").html(data);
                $("select#id_districts").val(selected_districts);
            }
        });
    };

    $('#id_districts').ready(function () {
        get_districts()
    });

    $("#id_provinces").change(function () {
        get_districts()
    });

    $('#id_activities').ready(function () {
        get_activities()
    });

    $("#id_clusters").change(function () {
        get_activities()
    });
});