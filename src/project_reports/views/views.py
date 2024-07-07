from collections import defaultdict

import pandas as pd
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.cache import cache_control
from rh.models import (
    ActivityDetail,
    ActivityDomain,
    ActivityPlan,
    ActivityType,
    Disaggregation,
    FacilitySiteType,
    Indicator,
    Location,
    LocationType,
    Project,
    TargetLocation,
)

from ..forms import (
    MonthlyReportFileUpload,
)
from ..models import (
    ActivityPlanReport,
    DisaggregationLocationReport,
    ProjectMonthlyReport,
    TargetLocationReport,
)

RECORDS_PER_PAGE = 10


def get_project_and_report_details(project_id, report_id=None):
    project = get_object_or_404(Project, pk=project_id)
    project_state = project.state
    activity_plans = project.activityplan_set.select_related(
        "activity_domain",
        "activity_type",
        "activity_detail",
    )
    target_locations = project.targetlocation_set.select_related("province", "district", "zone").all()
    monthly_report_instance = None

    if report_id is not None:
        monthly_report_instance = get_object_or_404(ProjectMonthlyReport, pk=report_id)

    return (
        project,
        project_state,
        activity_plans,
        target_locations,
        monthly_report_instance,
    )


def get_target_locations_domain(target_locations):
    # TODO: use cache
    # Create Q objects for each location type
    province_q = Q(id__in=[location.province.id for location in target_locations if location.province])
    district_q = Q(id__in=[location.district.id for location in target_locations if location.district])
    zone_q = Q(id__in=[location.zone.id for location in target_locations if location.zone])

    # Collect provinces, districts, and zones using a single query for each
    target_location_provinces = Location.objects.filter(province_q)
    target_location_districts = Location.objects.filter(district_q)
    target_location_zones = Location.objects.filter(zone_q)

    return (target_location_provinces, target_location_districts, target_location_zones)


# @login_required
# def get_location_report_empty_form(request):
#     """Get an empty location Report form for a project"""
#     # Get the project object based on the provided project ID
#     project = get_object_or_404(Project, pk=request.POST.get("project"))
#
#     # Get all existing target locaitions for the project
#     target_locations = project.targetlocation_set.select_related("province", "district", "zone").all()
#
#     (
#         target_location_provinces,
#         target_location_districts,
#         target_location_zones,
#     ) = get_target_locations_domain(target_locations)
#
#     ActivityReportFormset = inlineformset_factory(
#         ProjectMonthlyReport,
#         ActivityPlanReport,
#         form=ActivityPlanReportForm,
#         can_delete=True,
#     )
#
#     # Create an instance of ActivityPlanFormSet using the project instance and form_kwargs
#     activity_report_formset = ActivityReportFormset()
#
#     # Get the prefix index from the request
#     prefix_index = request.POST.get("prefix_index")
#
#     activity_domain_id = request.POST.get("activity_domain", None)
#     activity_domain = None
#     if activity_domain_id:
#         activity_domain = get_object_or_404(ActivityDomain, pk=activity_domain_id)
#
#     # Create an instance of TargetLocationFormSet with a prefixed name
#     location_report_formset = TargetLocationReportFormSet(
#         prefix=f"locations_report_{activity_report_formset.prefix}-{prefix_index}"
#     )
#
#     # for target_location_form in target_location_formset.forms:
#     # Create a disaggregation formset for each target location form
#     location_report_form = location_report_formset.empty_form
#
#     # Set the Target locations domain based on the activity plan
#     activity_plan = request.POST.get("activity_plan", None)
#     if activity_plan:
#         location_report_form.fields["target_location"].queryset = TargetLocation.objects.filter(
#             activity_plan=activity_plan
#         )
#
#     # Check if the activity plan is selected
#     if activity_domain:
#         # Get clusters associated with the activity plan's domain
#         clusters = activity_domain.clusters.all()
#
#         # Get only the relevant facility types - related to cluster
#         location_report_form.fields["facility_site_type"].queryset = FacilitySiteType.objects.filter(
#             cluster__in=clusters
#         )
#
#         cluster_has_nhs_code = any(cluster.has_nhs_code for cluster in clusters)
#         # If at least one cluster has NHS code, add the NHS code field to the form
#         if cluster_has_nhs_code:
#             location_report_form.fields["nhs_code"] = forms.CharField(max_length=200, required=True)
#         else:
#             location_report_form.fields.pop("nhs_code", None)
#     else:
#         location_report_form.fields["facility_site_type"].queryset = FacilitySiteType.objects.all()
#
#     location_report_form.fields["province"].queryset = Location.objects.filter(id__in=target_location_provinces)
#     location_report_form.fields["district"].queryset = Location.objects.filter(id__in=target_location_districts)
#     location_report_form.fields["zone"].queryset = Location.objects.filter(id__in=target_location_zones)
#
#     disaggregation_report_formset = DisaggregationReportFormSet(
#         request.POST or None,
#         instance=location_report_form.instance,
#         prefix=f"disaggregation_report_{location_report_form.prefix}",
#     )
#     location_report_form.disaggregation_report_formset = disaggregation_report_formset
#
#     # Prepare context for rendering the target location form template
#     context = {
#         "location_report_form": location_report_form,
#     }
#
#     # Render the target location form template and generate HTML
#     html = render_to_string("project_reports/forms/location_report_empty_form.html", context)
#
#     # Return JSON response containing the generated HTML
#     return JsonResponse({"html": html})


@cache_control(no_store=True)
@login_required
def load_target_locations_details(request):
    parent_ids = [int(i) for i in request.POST.getlist("parents[]") if i]
    parents = Location.objects.filter(pk__in=parent_ids).select_related("parent")

    response = ""

    # Use defaultdict to keep track of seen district primary keys for each parent
    seen_district_pks = defaultdict(set)

    # Retrieve target locations for the current parent
    for parent in parents:
        target_locations = TargetLocation.objects.filter(province=parent)

        # Check if any target_location exists for the current parent
        if target_locations.exists():
            response += f'<optgroup label="{parent.name}">'

            # Iterate over target_location objects for the current parent and retrieve the district primary keys
            for target_location in target_locations:
                district_pk = target_location.district.pk
                if district_pk not in seen_district_pks[parent.pk]:
                    seen_district_pks[parent.pk].add(district_pk)

                    # Update the set of seen district primary keys for the current parent
                    response += (
                        f'<option value="{target_location.district.pk}">{target_location.district.name}</option>'
                    )

            response += "</optgroup>"

    return JsonResponse(response, safe=False)


# @login_required
# def get_disaggregations_report_empty_forms(request):
#     """Get target location empty form"""
#
#     # Create a dictionary to hold disaggregation forms per location prefix
#     location_disaggregation_report_dict = {}
#     if request.POST.get("indicator"):
#         indicator = get_object_or_404(Indicator, pk=int(request.POST.get("indicator")))
#
#         # Get selected locations prefixes
#         locations_report_prefix = request.POST.getlist("locations_prefixes[]")
#
#         # Loop through each Indicator and retrieve its related Disaggregations
#         related_disaggregations = indicator.disaggregation_set.all()
#
#         initial_data = []
#
#         # Populate initial data with related disaggregations
#         if related_disaggregations:
#             for disaggregation in related_disaggregations:
#                 initial_data.append({"disaggregation": disaggregation})
#
#             # Create DisaggregationFormSet for each location prefix
#             for location_report_prefix in locations_report_prefix:
#                 DisaggregationReportFormSet.extra = len(related_disaggregations)
#                 disaggregation_report_formset = DisaggregationReportFormSet(
#                     prefix=f"disaggregation_report_{location_report_prefix}",
#                     initial=initial_data,
#                 )
#
#                 # Generate HTML for each disaggregation form and store in dictionary
#                 for disaggregation_report_form in disaggregation_report_formset.forms:
#                     context = {
#                         "disaggregation_report_form": disaggregation_report_form,
#                     }
#                     html = render_to_string(
#                         "project_reports/forms/disaggregation_report_empty_form.html",
#                         context,
#                     )
#
#                     if location_report_prefix in location_disaggregation_report_dict:
#                         location_disaggregation_report_dict[location_report_prefix].append(html)
#                     else:
#                         location_disaggregation_report_dict.update({location_report_prefix: [html]})
#
#         # Set back extra to 0 to avoid empty forms if refreshed.
#         DisaggregationReportFormSet.extra = 0
#
#     # Return JSON response containing generated HTML forms
#     return JsonResponse(location_disaggregation_report_dict)


def recompute_target_achieved(plan_report):
    """Recompute the target achieved for each activity plan report"""
    location_reports = plan_report.targetlocationreport_set.all()

    activity_report_target = 0
    for location_report in location_reports:
        disaggregation_location_reports = location_report.disaggregationlocationreport_set.all()

        for disaggregation_location_report in disaggregation_location_reports:
            activity_report_target += disaggregation_location_report.target
    plan_report.target_achieved = activity_report_target
    plan_report.save()


@login_required
def delete_location_report_view(request, location_report):
    """Delete the target location report"""
    location_report = get_object_or_404(TargetLocationReport, pk=location_report)
    plan_report = location_report.activity_plan_report
    monthly_report = location_report.activity_plan_report.monthly_report
    if location_report:
        location_report.delete()

        # Recompute the achieved target for the location_report activity.
        recompute_target_achieved(plan_report)

    # Generate the URL using reverse
    url = reverse(
        "view_monthly_report",
        kwargs={
            "project": monthly_report.project.pk,
            "report": monthly_report.pk,
        },
    )

    # Return the URL in a JSON response
    response_data = {"redirect_url": url}
    return JsonResponse(response_data)


def import_monthly_reports(request, report):
    """Import monthly report activities via excel."""
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    if request.method == "POST":
        form = MonthlyReportFileUpload(request.POST, request.FILES)
        if form.is_valid():
            report_file = form.cleaned_data["file"]
            df = pd.read_excel(report_file)
            if df.empty:
                success = False
                message = "No Data in the file!"
            else:
                success = True
                message = ""

                with transaction.atomic():
                    for index, row in df.iterrows():
                        message = ""

                        # TODO: Handle same file upload multiple times,
                        # check all of the file first and then run import

                        # Get or create Indicator
                        indicator_name = row.get("indicator")
                        activity_domain_name = row.get("activity_domain")
                        activity_type_name = row.get("activity_type")
                        activity_detail_name = row.get("activity_detail")
                        country_name = row.get("admin0pcode")
                        province_name = row.get("admin1pcode")
                        district_name = row.get("admin2pcode")
                        zone_name = row.get("zone")
                        location_type_name = row.get("location_type")
                        facility_site_type_name = row.get("facility_site_type")

                        # Validate required columns
                        columns_to_check = [
                            "indicator",
                            "activity_domain",
                            "activity_type",
                            "admin0pcode",
                            "admin1pcode",
                            "admin2pcode",
                        ]
                        required_column_missing = False
                        for column in columns_to_check:
                            if pd.isnull(row[column]):
                                required_column_missing = True
                                message += f"<span>Row [{index + 2}]: {column.capitalize()} is missing. </span><br/>"

                        if required_column_missing:
                            success = False
                            continue  # Skip the rest of the loop for this row

                        try:
                            indicator = get_object_or_404(Indicator, name=indicator_name)
                            activity_domain = get_object_or_404(ActivityDomain, code=activity_domain_name)
                            activity_type = get_object_or_404(ActivityType, code=activity_type_name)
                        except Exception as e:
                            success = False
                            message += f"<span>Row [{index + 2}]: {e} </span><br/>"
                            continue  # Skip the rest of the loop for this row

                        activity_plan_params = {
                            "project": monthly_report.project,
                            "activity_domain": activity_domain,
                            "activity_type": activity_type,
                        }
                        if not pd.isna(activity_detail_name):
                            try:
                                activity_detail = ActivityDetail.objects.get(code=activity_detail_name)
                            except ActivityDetail.DoesNotExist:
                                continue

                            if activity_detail:
                                activity_plan_params.update({"activity_detail": activity_detail})
                        try:
                            activity_plan = get_object_or_404(ActivityPlan, **activity_plan_params)
                        except Exception as e:
                            success = False
                            message += f"<span>Row [{index + 2}]: {e} </span><br/>"
                            break

                        # Create ActivityPlanReport
                        activity_plan_report_params = {
                            "monthly_report": monthly_report,
                            "activity_plan": activity_plan,
                            "indicator": indicator,
                        }
                        activity_plan_report = ActivityPlanReport.objects.filter(
                            monthly_report=monthly_report,
                            activity_plan=activity_plan,
                            indicator=indicator,
                        )
                        if not activity_plan_report:
                            activity_plan_report = ActivityPlanReport.objects.create(**activity_plan_report_params)
                        else:
                            activity_plan_report = activity_plan_report[0]

                        # Handle Location details
                        try:
                            country = get_object_or_404(Location, code=country_name)
                            province = get_object_or_404(Location, code=province_name)
                            district = get_object_or_404(Location, code=district_name)
                        except Exception as e:
                            success = False
                            message += f"<span>Row [{index + 2}]: {e} </span><br/>"
                            break

                        target_location_report_params = {
                            "activity_plan_report": activity_plan_report,
                            "country": country,
                            "province": province,
                            "district": district,
                        }

                        if not pd.isna(zone_name):
                            try:
                                zone = Location.objects.get_object_or_404(Location, name=zone_name)
                            except Location.DoesNotExist:
                                continue

                            if zone:
                                target_location_report_params.update({"zone": zone})

                        # Create TargetLocationReport
                        if not pd.isna(location_type_name):
                            try:
                                location_type = get_object_or_404(LocationType, name=location_type_name)
                            except LocationType.DoesNotExist:
                                continue

                            if location_type:
                                target_location_report_params.update({"location_type": location_type})

                        # Create TargetLocationReport
                        if not pd.isna(facility_site_type_name):
                            try:
                                facility_site_type = get_object_or_404(FacilitySiteType, name=facility_site_type_name)
                            except FacilitySiteType.DoesNotExist:
                                continue

                            if facility_site_type:
                                target_location_report_params.update({"facility_site_type": facility_site_type})

                        if target_location_report_params:
                            target_location_report = TargetLocationReport.objects.create(
                                **target_location_report_params
                            )

                        if not target_location_report:
                            success = False
                            message += f"<span>Row [{index + 2}]: Failed to create Target Location Report. </span><br/>"
                            continue  # Skip the rest of the loop for this row

                        activity_report_target = 0
                        activity_plans = monthly_report.project.activityplan_set.all()
                        disaggregations = []
                        disaggregation_list = []
                        for plan in activity_plans:
                            target_locations = plan.targetlocation_set.all()
                            for location in target_locations:
                                disaggregation_locations = location.disaggregationlocation_set.all()
                                for dl in disaggregation_locations:
                                    if dl.disaggregation.name not in disaggregation_list:
                                        disaggregation_list.append(dl.disaggregation.name)
                                        disaggregations.append(dl.disaggregation.name)
                                    else:
                                        continue

                        for disaggregation in disaggregations:
                            disaggregation_name = disaggregation
                            disaggregation_target = row.get(disaggregation, 0)
                            if not pd.isna(disaggregation_target):
                                activity_report_target += row.get(disaggregation, 0)
                            if not pd.isna(disaggregation_target) and not pd.isna(disaggregation_name):
                                disaggregation = Disaggregation.objects.get(name=disaggregation_name)
                            else:
                                continue

                            disaggregation_location_report_params = {
                                "target_location_report": target_location_report,
                                "disaggregation": disaggregation,
                                "target": int(disaggregation_target),
                            }
                            DisaggregationLocationReport.objects.create(**disaggregation_location_report_params)

                        activity_plan_report.target_achieved += activity_report_target
                        activity_plan_report.save()

                        success = True

            url = reverse(
                "view_monthly_report",
                kwargs={
                    "project": monthly_report.project.pk,
                    "report": monthly_report.pk,
                },
            )

            # Return the URL in a JSON response
            response_data = {"success": success, "redirect_url": url, "message": message}
            return JsonResponse(response_data)
