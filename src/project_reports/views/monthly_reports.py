import calendar
from datetime import datetime, timedelta

import pandas as pd
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q

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
)

from ..forms import (
    MonthlyReportFileUpload,
    ProjectMonthlyReportForm,
)
from ..models import (
    ActivityPlanReport,
    DisaggregationLocationReport,
    ProjectMonthlyReport,
    TargetLocationReport,
)

from ..filters import MonthlyReportsFilter

RECORDS_PER_PAGE = 10


class HTTPResponseHXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["HX-Redirect"] = self["Location"]

    status_code = 200


@login_required
def index_project_report_view(request, project):
    """Project Monthly Report View"""

    project = get_object_or_404(Project.objects.filter(pk=project).order_by("-id"), pk=project)

    # Setup Filter
    reports_filter = MonthlyReportsFilter(
        request.GET,
        request=request,
        queryset=ProjectMonthlyReport.objects.filter(project=project)
        .order_by("-id")
        .prefetch_related(
            Prefetch(
                "activityplanreport_set",
                ActivityPlanReport.objects.select_related("activity_plan").prefetch_related(
                    Prefetch(
                        "targetlocationreport_set", TargetLocationReport.objects.select_related("province", "district")
                    ),
                ),
            ),
        ),
    )

    # Setup Pagination
    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    p = Paginator(reports_filter.qs, per_page=per_page)
    page = request.GET.get("page", 1)
    p_reports = p.get_page(page)
    p_reports.adjusted_elided_pages = p.get_elided_page_range(page)

    reports = ProjectMonthlyReport.objects.filter(project=project).aggregate(
        project_reports_todo_count=Count("id", filter=Q(state__in=ProjectMonthlyReport.REPORT_STATES)),
        project_report_complete_count=Count("id", filter=Q(state="complete"), is_active=True),
        project_report_archive_count=Count("id", filter=Q(state="archive", is_active=False)),
        project_reports_count=Count("id", filter=Q(is_active=True)),
    )

    context = {
        "project": project,
        "project_reports": p_reports,
        "project_reports_todo": reports["project_reports_todo_count"],
        "project_report_complete": reports["project_report_complete_count"],
        "project_report_archive": reports["project_report_archive_count"],
        "project_report_count": reports["project_reports_count"],
        "reports_filter": reports_filter,
        "project_view": False,
        "financial_view": False,
        "reports_view": True,
    }

    return render(request, "project_reports/monthly_reports/views/monthly_reports_view_base.html", context)


@login_required
def create_project_monthly_report_view(request, project):
    """View for creating a project."""
    project = get_object_or_404(Project, pk=project)

    if project.state == "in-progress":
        # Get the current date
        current_date = datetime.now()

        # Calculate the last day of the current month
        last_day = calendar.monthrange(current_date.year, current_date.month)[1]

        # Create a new date representing the end of the current month
        end_of_month = datetime(current_date.year, current_date.month, last_day)

        form = ProjectMonthlyReportForm(
            request.POST or None,
            initial={"report_due_date": end_of_month, "project": project},
        )

        if request.method == "POST":
            if form.is_valid():
                report = form.save(commit=False)
                report.project = project
                report.is_active = True
                report.state = "pending"
                report.save()

                return redirect("create_report_activity_plan", report=report.pk, project=project.pk)

                # return render(request, "project_reports/report_activity_plans/activity_plan_form.html", context=context)
                # return redirect(
                #     "view_monthly_report",
                #     project=project.pk,
                #     report=report.pk,
                # )

        context = {
            "project": project,
            "report_form": form,
            "report_view": True,
            "report_activities": False,
            "report_locations": False,
        }
        return render(request, "project_reports/monthly_reports/forms/monthly_report_form.html", context)

    messages.error(request, "Your project is not ready for reporting! Please submit your project first.")

    return redirect(
        "project_reports_home",
        project=project.pk,
    )


@login_required
def update_project_monthly_report_view(request, project, report):
    """View for updating a project."""

    report = get_object_or_404(ProjectMonthlyReport, pk=report)

    if request.method == "POST":
        form = ProjectMonthlyReportForm(request.POST, instance=report)
        if form.is_valid():
            report = form.save()
            report.project_id = project
            report.save()
            return redirect(
                "list_report_activity_plans",
                project=project,
                report=report.pk,
            )
    else:
        form = ProjectMonthlyReportForm(instance=report)

    context = {
        "form": form,
        "monthly_report": report,
        "project": report.project,
        "report_form": form,
        "report_view": True,
        "report_activities": False,
        "report_locations": False,
    }
    return render(request, "project_reports/monthly_reports/forms/monthly_report_form.html", context)


@login_required
def details_monthly_progress_view(request, project, report):
    """Project Monthly Report Read View"""
    project = get_object_or_404(Project, pk=project)

    monthly_report = get_object_or_404(
        ProjectMonthlyReport.objects.prefetch_related(
            Prefetch(
                "activityplanreport_set",
                ActivityPlanReport.objects.select_related(
                    "activity_plan__activity_domain", "activity_plan__activity_type", "indicator"
                ),
            ),
        ),
        pk=report,
    )

    # activity_reports = monthly_report.activityplanreport_set
    #
    # activity_plans = project.activityplan_set.select_related(
    #     "activity_domain",
    #     "activity_type",
    # )
    #
    # activity_plans = [plan for plan in activity_plans]
    #
    # report_plans = ActivityPlanReport.objects.filter(monthly_report=monthly_report.pk).annotate(
    #     report_target_location_count=Count("targetlocationreport")
    # )
    #
    # if not report_plans:
    #     for plan in activity_plans:
    #         if plan.state == "in-progress":
    #             ActivityPlanReport.objects.create(
    #                 monthly_report_id=monthly_report.pk,
    #                 activity_plan_id=plan.pk,
    #                 indicator_id=plan.indicator.pk,
    #             )

    activity_reports = monthly_report.activityplanreport_set.all()

    context = {
        "project": project,
        "monthly_report": monthly_report,
        "activity_reports": activity_reports,
        "report_view": True,
        "report_activities": False,
        "report_locations": False,
    }

    return render(request, "project_reports/monthly_reports/views/monthly_report_view.html", context)


@login_required
def copy_project_monthly_report_view(request, report):
    """Copy report view"""
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)

    # Calculate the first day of the current month
    today = datetime.now()
    first_day_of_current_month = today.replace(day=1)

    # Calculate the first day of the last month
    first_day_of_last_month = (first_day_of_current_month - timedelta(days=1)).replace(day=1)

    last_month_report = None

    # Filter the reports for the last month and find the latest submitted report
    last_month_reports = ProjectMonthlyReport.objects.filter(
        project=monthly_report.project.pk,
        report_date__gte=first_day_of_last_month,
        report_date__lt=first_day_of_current_month,
        state="complete",  # Filter by the "Submitted" state
        approved_on__isnull=False,  # Ensure the report has a submission date
    )
    if last_month_reports:
        last_month_report = last_month_reports.latest("approved_on")

    # Check if the new monthly report was successfully created.
    if monthly_report and last_month_report:
        # Get all activity plans reports associated with the current monthly report.
        activity_plan_reports = last_month_report.activityplanreport_set.all()

        # delete existing records
        monthly_report.activityplanreport_set.all().delete()

        # Iterate through each activity plan  report and copy it to the new monthly report.
        for plan_report in activity_plan_reports:
            new_plan_report = copy_monthly_report_activity_plan(monthly_report, plan_report)
            location_reports = plan_report.targetlocationreport_set.all()

            # Iterate through target locations reports and copy them to the new plan report.
            for location_report in location_reports:
                new_location_report = copy_target_location_report(new_plan_report, location_report)
                disaggregation_location_reports = location_report.disaggregationlocationreport_set.all()

                # Iterate through disaggregation locations reports and copy them to the new location report.
                for disaggregation_location_report in disaggregation_location_reports:
                    copy_disaggregation_location_reports(new_location_report, disaggregation_location_report)
        messages.success(request, "Report activities copied successfully.")
        url = reverse_lazy(
            "list_report_activity_plans", kwargs={"project": monthly_report.project.pk, "report": monthly_report.pk}
        )

    else:
        messages.error(request, "At least one last month approved report is required.")
        url = reverse_lazy(
            "view_monthly_report", kwargs={"project": monthly_report.project.pk, "report": monthly_report.pk}
        )

    # Save the changes made to the new monthly report.
    monthly_report.state = "todo"
    monthly_report.save()

    return HTTPResponseHXRedirect(redirect_to=url)


def copy_monthly_report_activity_plan(monthly_report, plan_report):
    """Copy activity plan reports"""
    try:
        # Duplicate the original activity plan report by retrieving it with the provided primary key.
        new_plan_report = get_object_or_404(ActivityPlanReport, pk=plan_report.pk)
        new_plan_report.pk = None  # Generate a new primary key for the duplicated plan report.
        new_plan_report.save()  # Save the duplicated plan report to the database.

        # Associate the duplicated plan report with the new monthly report.
        new_plan_report.monthly_report = monthly_report

        # Set the plan report as active
        new_plan_report.is_active = True

        # Copy indicator from the current plan report to the duplicated plan report.
        new_plan_report.indicator = plan_report.indicator

        # Save the changes made to the duplicated plan report.
        new_plan_report.save()

        # Return the duplicated plan report.
        return new_plan_report
    except Exception as _:
        # If an exception occurs, return False to indicate the copy operation was not successful.
        return False


def copy_target_location_report(plan_report, location_report):
    """Copy Target Locations"""
    try:
        # Duplicate the original target location report report report
        # by retrieving it with the provided primary key.
        new_location_report = get_object_or_404(TargetLocationReport, pk=location_report.pk)
        new_location_report.pk = None  # Generate a new primary key for the duplicated location.
        new_location_report.save()  # Save the duplicated location to the database.

        # Associate the duplicated location with the new activity plan report.
        new_location_report.activity_plan_report = plan_report

        new_location_report.save()

        # Return the duplicated location.
        return new_location_report
    except Exception as _:
        # If an exception occurs, return False to indicate the copy operation was not successful.
        return False


def copy_disaggregation_location_reports(location_report, disaggregation_location_report):
    """Copy Disaggregation Locations"""
    try:
        # Duplicate the original disaggregation location by retrieving it with the provided
        # primary key.
        new_disaggregation_location_report = get_object_or_404(
            DisaggregationLocationReport, pk=disaggregation_location_report.pk
        )
        new_disaggregation_location_report.pk = None  # Generate a new primary key for the duplicated location report.
        new_disaggregation_location_report.save()  # Save the duplicated location report to the database.

        # Associate the duplicated disaggregation location report with the new target location report.
        new_disaggregation_location_report.target_location_report = location_report

        # Save the changes made to the duplicated disaggregation location report.
        new_disaggregation_location_report.save()

        # Return True to indicate that the copy operation was successful.
        return True
    except Exception as _:
        # If an exception occurs, return False to indicate the copy operation was not successful.
        return False


@login_required
def delete_project_monthly_report_view(request, report):
    """Delete View for Project Reports"""
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    # TODO: Check access rights before deleting
    if monthly_report:
        monthly_report.delete()
    url = reverse_lazy("project_reports_home", kwargs={"project": monthly_report.project.pk})
    url_with_params = f"{url}?state=todo&state=pending&state=submit&state=reject"

    return HTTPResponseHXRedirect(redirect_to=url_with_params)


@login_required
def archive_project_monthly_report_view(request, report):
    """Archive View for Project Reports"""
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    if monthly_report:
        monthly_report.state = "archive"
        monthly_report.is_active = False
        monthly_report.save()
    url = reverse_lazy("project_reports_home", kwargs={"project": monthly_report.project.pk})
    url_with_params = f"{url}?state=todo&state=pending&state=submit&state=reject"

    return HTTPResponseHXRedirect(redirect_to=url_with_params)


@login_required
def unarchive_project_monthly_report_view(request, report):
    """Unarchive View for Project Reports"""
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    if monthly_report:
        monthly_report.is_active = True
        monthly_report.state = "todo"
        monthly_report.save()
    url = reverse_lazy("project_reports_home", kwargs={"project": monthly_report.project.pk})
    url_with_params = f"{url}?state=todo&state=pending&state=submit&state=reject"

    return HTTPResponseHXRedirect(redirect_to=url_with_params)


@login_required
def submit_monthly_report_view(request, report):
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    # TODO: Handle with access rights and groups
    monthly_report.state = "complete"
    monthly_report.submitted_on = timezone.now()
    monthly_report.approved_on = timezone.now()
    monthly_report.save()
    messages.success(request, "Report Submitted and Approved!")

    # Return the URL in a JSON response
    url = reverse_lazy(
        "view_monthly_report", kwargs={"project": monthly_report.project.pk, "report": monthly_report.pk}
    )
    return HTTPResponseHXRedirect(redirect_to=url)


@login_required
def approve_monthly_report_view(request, report):
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    # TODO: Handle with access rights and groups
    monthly_report.state = "complete"
    monthly_report.approved_on = timezone.now()
    monthly_report.save()
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


@login_required
def reject_monthly_report_view(request, report):
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    message = ""
    if request.GET.get("message", ""):
        message = request.GET.get("message")

    # TODO: Handle with access rights and groups
    monthly_report.state = "reject"
    monthly_report.rejected_on = timezone.now()
    monthly_report.comments = message

    monthly_report.save()

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


@login_required
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
