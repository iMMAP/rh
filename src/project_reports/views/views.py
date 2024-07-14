import pandas as pd
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
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
