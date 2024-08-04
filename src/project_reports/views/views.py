import pandas as pd
import logging
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from rh.models import (
    Project,
    ActivityDetail,
    ActivityDomain,
    ActivityPlan,
    ActivityType,
    Disaggregation,
    FacilitySiteType,
    TargetLocation,
    Organization,
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

logger = logging.getLogger(__name__)

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


def import_data_with_project_plan(request):
    if request.method == 'POST':
        form = MonthlyReportFileUpload(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return redirect('success_url')
    else:
        form = MonthlyReportFileUpload()
    return render(request, 'project_reports/monthly_reports/forms/file_upload_form.html', {'form': form})


def handle_uploaded_file(file):
    try:
        df = pd.read_csv(file)
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return

    required_fields = ['organization', 'activity_description_name', 'report_month', 'report_year',
                       'admin1pcode', 'admin1name', 'admin2pcode', 'admin2name', 'indicator_name']

    missing_fields = [field for field in required_fields if field not in df.columns]
    if missing_fields:
        logger.error(f"Missing required fields in CSV: {', '.join(missing_fields)}")
        return

    for _, row in df.iterrows():
        try:
            # Validate required fields
            for field in required_fields:
                if pd.isna(row[field]):
                    logger.error(f"Missing required field: {field} in row: {row}")
                    continue

            organization, created = Organization.objects.get_or_create(name=row['organization'])
            if created:
                logger.info(f"Created new organization: {row['organization']}")

            project, created = Project.objects.get_or_create(
                organization=organization,
                title=row['activity_description_name'],
                defaults={
                    'state': 'draft',
                    'is_hrp_project': True,
                    'start_date': '2024-01-01',  # Example start date
                    'end_date': '2024-12-31',  # Example end date
                }
            )
            if created:
                logger.info(f"Created new project: {row['activity_description_name']}")

            activity_domain, created = ActivityDomain.objects.get_or_create(name=row['activity_description_name'])
            if created:
                logger.info(f"Created new activity domain: {row['activity_description_name']}")

            activity_plan, created = ActivityPlan.objects.get_or_create(
                project=project,
                activity_domain=activity_domain,
                defaults={
                    'state': 'draft',
                    'total_target': int(row['total']),
                    'total_set_target': int(row['total']),
                    'description': row['activity_description_name'],
                }
            )
            if created:
                logger.info(f"Created new activity plan for project: {project.title}")

            province, created = Location.objects.get_or_create(pcode=row['admin1pcode'], name=row['admin1name'],
                                                               level=1)
            if created:
                logger.info(f"Created new province: {row['admin1name']}")

            district, created = Location.objects.get_or_create(pcode=row['admin2pcode'], name=row['admin2name'],
                                                               level=2)
            if created:
                logger.info(f"Created new district: {row['admin2name']}")

            target_location, created = TargetLocation.objects.get_or_create(
                project=project,
                activity_plan=activity_plan,
                province=province,
                district=district,
                defaults={
                    'facility_name': row.get('facility_name'),
                    'facility_id': row.get('facility_id'),
                    'facility_lat': float(row['facility_lat']) if pd.notna(row.get('facility_lat')) else None,
                    'facility_long': float(row['facility_long']) if pd.notna(row.get('facility_long')) else None,
                }
            )
            if created:
                logger.info(f"Created new target location for activity plan: {activity_plan.id}")

            monthly_report, created = ProjectMonthlyReport.objects.get_or_create(
                project=project,
                report_period=f"{row['report_year']}-{row['report_month']}-01",
                defaults={'state': 'todo'}
            )
            if created:
                logger.info(f"Created new monthly report for project: {project.title}")

            indicator, created = Indicator.objects.get_or_create(name=row['indicator_name'])
            if created:
                logger.info(f"Created new indicator: {row['indicator_name']}")

            activity_plan_report, created = ActivityPlanReport.objects.get_or_create(
                monthly_report=monthly_report,
                activity_plan=activity_plan,
                indicator=indicator,
                defaults={'target_achieved': int(row['total'])}
            )
            if created:
                logger.info(f"Created new activity plan report for monthly report: {monthly_report.id}")

            target_location_report, created = TargetLocationReport.objects.get_or_create(
                activity_plan_report=activity_plan_report,
                target_location=target_location,
                defaults={
                    'facility_name': row.get('facility_name'),
                    'facility_id': row.get('facility_id'),
                    'facility_lat': float(row['facility_lat']) if pd.notna(row.get('facility_lat')) else None,
                    'facility_long': float(row['facility_long']) if pd.notna(row.get('facility_long')) else None,
                }
            )
            if created:
                logger.info(f"Created new target location report for activity plan report: {activity_plan_report.id}")

            # Handle DisaggregationLocationReport if needed
            # For each disaggregation location report, you will need to fetch or create the disaggregation,
            # then create the corresponding DisaggregationLocationReport entry.
            # Example logic (assuming disaggregation fields are included in the CSV):
            # disaggregation, created = Disaggregation.objects.get_or_create(name=row['disaggregation_name'])
            # DisaggregationLocationReport.objects.get_or_create(
            #     target_location_report=target_location_report,
            #     disaggregation=disaggregation,
            #     defaults={'target_required': int(row['target_required']), 'target': int(row['target'])}
            # )

        except Exception as e:
            logger.error(f"Error processing row: {row}. Error: {e}")