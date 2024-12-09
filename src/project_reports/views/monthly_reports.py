import calendar
import csv
from datetime import datetime

import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django_htmx.http import HttpResponseClientRedirect
from extra_settings.models import Setting
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
from users.utils import is_cluster_lead

from ..filters import ActivityPlanReportFilter, MonthlyReportsFilter
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

RECORDS_PER_PAGE = 10


def notify_focal_point(request, report_id: int):
    report = get_object_or_404(ProjectMonthlyReport.objects.select_related("project"), pk=report_id)
    project_clusters = report.project.clusters.values_list("code", flat=True)
    admin_user = request.user
    focal_point = report.project.user

    # user should be at least admin of one of the project clusters
    if not is_cluster_lead(user=request.user, clusters=project_clusters):
        return PermissionDenied

    # notify the project.user
    html_message = loader.render_to_string(
        template_name="rh/emails/pending_report.html",
        context={
            "report": report,
            "admin_user": admin_user,
            "focal_point": focal_point,
            "domain": f"{request.scheme}://{request.get_host()}",
        },
    )

    focal_point.email_user(
        subject="Pending Report Notification",
        message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        html_message=html_message,
    )

    messages.success(request, "User has been notified")

    return HttpResponse(200)


@login_required
def index_project_report_view(request, project):
    """Project Monthly Report View"""

    project = get_object_or_404(Project, pk=project)

    # Setup Filter
    reports_filter = MonthlyReportsFilter(
        request.GET,
        request=request,
        queryset=ProjectMonthlyReport.objects.filter(project=project).order_by("-from_date"),
    )

    # Setup Pagination
    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    p = Paginator(reports_filter.qs, per_page=per_page)
    page = request.GET.get("page", 1)
    p_reports = p.get_page(page)
    p_reports.adjusted_elided_pages = p.get_elided_page_range(page)

    reports = ProjectMonthlyReport.objects.filter(project=project).aggregate(
        project_reports_todo_count=Count("id", filter=Q(state__in=ProjectMonthlyReport.REPORT_STATES)),
        project_report_complete_count=Count("id", filter=Q(state="complete")),
        project_report_archive_count=Count("id", filter=Q(state="archive")),
    )

    context = {
        "project": project,
        "project_reports": p_reports,
        "project_reports_todo": reports["project_reports_todo_count"],
        "project_report_complete": reports["project_report_complete_count"],
        "project_report_archive": reports["project_report_archive_count"],
        "reports_filter": reports_filter,
        "report_states": ProjectMonthlyReport.REPORT_STATES,
    }

    return render(request, "project_reports/monthly_reports/views/monthly_reports_view_base.html", context)


@login_required
def create_project_monthly_report_view(request, project):
    project = get_object_or_404(Project, pk=project)

    if project.state != "in-progress":
        messages.error(request, "Your project is not ready for reporting! Please submit your project first.")

        return redirect(
            "project_reports_home",
            project=project.pk,
        )

    # Get the current date
    current_date = datetime.now()

    # Calculate the last day of the current month
    last_day = calendar.monthrange(current_date.year, current_date.month)[1]

    # Create a new date representing the end of the current month
    end_of_month = datetime(current_date.year, current_date.month, last_day)

    form = ProjectMonthlyReportForm(
        request.POST or None,
        initial={"to_date": end_of_month, "project": project},
    )
    if request.method == "POST":
        if form.is_valid():
            report = form.save(commit=False)
            report.project = project
            report.state = "pending"
            report.save()

            messages.success(
                request,
                "Monthly report period created successfully. You can add reports activities from the below table.",
            )

            return redirect(
                "view_monthly_report",
                project=project.pk,
                report=report.pk,
            )
        else:
            messages.error(request, "Something went wrong! please check the below form for errors")

    context = {
        "project": project,
        "report_form": form,
    }

    return render(request, "project_reports/monthly_reports/forms/monthly_report_form.html", context)


@login_required
def update_project_monthly_report_view(request, project, report):
    """View for updating a project."""

    report = get_object_or_404(ProjectMonthlyReport, pk=report)
    projectt = report.project
    if request.method == "POST":
        form = ProjectMonthlyReportForm(request.POST, instance=report)
        projectt = report.project
        if form.is_valid():
            report = form.save(commit=False)
            report.project_id = project
            report.save()
            return redirect("view_monthly_report", project=project, report=report.pk)
        else:
            messages.error(request, "Something went wrong. Please fix the below errors.")
    else:
        form = ProjectMonthlyReportForm(instance=report)

    context = {
        "form": form,
        "monthly_report": report,
        "project": projectt,
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
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)

    activity_plan_report_list = (
        ActivityPlanReport.objects.filter(monthly_report=monthly_report)
        .select_related("activity_plan__activity_domain", "activity_plan__activity_type")
        .prefetch_related("response_types")
        .order_by("-id")
        .annotate(report_location_count=Count("targetlocationreport"))
    )

    ap_report_filter = ActivityPlanReportFilter(
        request.GET, queryset=activity_plan_report_list, monthly_report=monthly_report
    )

    RECORDS_PER_PAGE = Setting.get("RECORDS_PER_PAGE", default=10)
    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    p = Paginator(ap_report_filter.qs, per_page=per_page)
    page = request.GET.get("page", 1)
    p_ap_plan_report_list = p.get_page(page)
    p_ap_plan_report_list.adjusted_elided_pages = p.get_elided_page_range(page)

    context = {
        "project": project,
        "monthly_report": monthly_report,
        "p_ap_plan_report_list": p_ap_plan_report_list,
        "ap_report_filter": ap_report_filter,
    }

    return render(request, "project_reports/monthly_reports/views/monthly_report_view.html", context)


@login_required
def copy_project_monthly_report_view(request, report):
    """Copy report view"""
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    # Filter the reports for the last month and find the latest submitted report
    # last_month_report = ProjectMonthlyReport.objects.filter(project=monthly_report.project, state="completed").latest(
    #     "approved_on"
    # )

    last_month_report = None

    try:
        last_month_report = (
            ProjectMonthlyReport.objects.select_related("project")
            .prefetch_related(
                Prefetch(
                    "activityplanreport_set",
                    queryset=ActivityPlanReport.objects.prefetch_related(
                        Prefetch(
                            "targetlocationreport_set",
                            queryset=TargetLocationReport.objects.prefetch_related(
                                Prefetch(
                                    "disaggregationlocationreport_set",
                                    DisaggregationLocationReport.objects.select_related("disaggregation"),
                                )
                            ),
                        )
                    ),
                )
            )
            .filter(project=monthly_report.project, state="completed")
            .latest("approved_on")
        )
    except Exception:
        messages.error(request, "At least one last month approved report is required.")
        return HttpResponse(200)

    # Check if the new monthly report was successfully created.
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
        "view_monthly_report", kwargs={"project": monthly_report.project.pk, "report": monthly_report.pk}
    )

    # Save the changes made to the new monthly report.
    monthly_report.state = "pending"
    monthly_report.save()

    return HttpResponseClientRedirect(url)


def copy_monthly_report_activity_plan(monthly_report, plan_report):
    """Copy activity plan reports"""
    try:
        # Duplicate the original activity plan report by retrieving it with the provided primary key.
        new_plan_report = get_object_or_404(ActivityPlanReport, pk=plan_report.pk)
        response_types = new_plan_report.response_types.all()
        new_plan_report.pk = None  # Generate a new primary key for the duplicated plan report.
        new_plan_report.monthly_report = monthly_report

        new_plan_report.save()

        new_plan_report.response_types.set(response_types)

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
        new_location_report.beneficiary_status = "existing_beneficiaries"

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
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)

    # TODO: Check access rights before deleting
    status_code = None
    if monthly_report.state != "archived":
        monthly_report.delete()
        messages.success(request, "The reporting period and its dependencies has been deleted")
        status_code = 200
    elif monthly_report.state == "archived":
        messages.error(request, "The archived report cannot be deleted.")
        status_code = 500
    if request.headers.get("Hx-Trigger", "") == "delete-btn":
        url = reverse_lazy("project_reports_home", kwargs={"project": monthly_report.project.pk})
        return HttpResponseClientRedirect(url)
    return HttpResponse(status=status_code)


@login_required
def archive_project_monthly_report_view(request, report):
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)

    if monthly_report:
        monthly_report.state = "archived"
        monthly_report.save()

    url = reverse_lazy("project_reports_home", kwargs={"project": monthly_report.project.pk})

    return HttpResponseClientRedirect(url)


@login_required
def unarchive_project_monthly_report_view(request, report):
    """Unarchive View for Project Reports"""
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)

    monthly_report.is_active = True
    monthly_report.state = "todo"
    monthly_report.save()

    url = reverse_lazy("project_reports_home", kwargs={"project": monthly_report.project.pk})

    return HttpResponseClientRedirect(url)


@login_required
def submit_monthly_report_view(request, report):
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)

    report_activity_plans = monthly_report.activityplanreport_set.all()

    if not report_activity_plans.exists():
        messages.error(
            request,
            "The project must have at least one activity plan report and each Activity Plan Report must have one Target Location Report.",
        )
        return HttpResponse(200)

    for plan in report_activity_plans:
        target_locations = plan.targetlocationreport_set.all()
        if not target_locations.exists():
            messages.error(request, "Each activity plan report must have at least one target location report.")
            return HttpResponse(200)

    # TODO: Handle with access rights and groups
    monthly_report.state = "completed"
    monthly_report.submitted_on = timezone.now()
    monthly_report.approved_on = timezone.now()

    monthly_report.save()

    messages.success(request, "Report Submitted and Approved!")

    url = reverse_lazy(
        "view_monthly_report", kwargs={"project": monthly_report.project.pk, "report": monthly_report.pk}
    )

    return HttpResponseClientRedirect(url)


@login_required
def approve_monthly_report_view(request, report):
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    # TODO: Handle with access rights and groups
    monthly_report.state = "completed"
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
    monthly_report.state = "rejected"
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


# download last month activity report
def download_project_monthly_report_view(request, report):
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)

    # Filter the reports for the last month and find the latest submitted report
    # last_month_report = ProjectMonthlyReport.objects.filter(project=monthly_report.project, state="completed").latest(
    #     "approved_on"
    # )
    last_month_report = None
    # error handling
    try:
        last_month_report = (
            ProjectMonthlyReport.objects.select_related("project")
            .prefetch_related(
                Prefetch(
                    "activityplanreport_set",
                    queryset=ActivityPlanReport.objects.prefetch_related(
                        Prefetch(
                            "targetlocationreport_set",
                            queryset=TargetLocationReport.objects.prefetch_related(
                                Prefetch(
                                    "disaggregationlocationreport_set",
                                    DisaggregationLocationReport.objects.select_related("disaggregation"),
                                )
                            ),
                        )
                    ),
                )
            )
            .filter(project=monthly_report.project, state="completed")
            .latest("approved_on")
        )
    except Exception:
        url = reverse_lazy(
            "view_monthly_report", kwargs={"project": monthly_report.project.pk, "report": monthly_report.pk}
        )
        messages.error(request, "At least one last month approved report is required.")
        return HttpResponseRedirect(url)

    # define csv
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=last_month_activity_report.csv"
    writer = csv.writer(response)
    columns = [
        "project_code",
        "indicator",
        "activity_domain",
        "activity_type",
        "response_types",
        "implementing_partners",
        "package_type",
        "unit_type",
        "units",
        "no_of_transfers",
        "grant_type",
        "transfer_category",
        "currency",
        "transfer_mechanism_type",
        "implement_modility_type",
        "beneficiary_status",
        "admin0name",
        "admin0pcode",
        "admin1pcode",
        "admin1name",
        "admin2pcode",
        "admin2name",
        "zone",
        "location_type",
        "facility_site_type",
        "facility_monitoring",
        "facility_id",
        "facility_name",
        "facility_lat",
        "facility_long",
    ]
    disaggregation_cols = []
    disaggregation_list = []
    plan_reports = last_month_report.activityplanreport_set.all()
    for plan_report in plan_reports:
        location_reports = plan_report.targetlocationreport_set.all()
        for location_report in location_reports:
            disaggregations = location_report.disaggregationlocationreport_set.all()
            for disaggregation in disaggregations:
                if disaggregation.disaggregation.name not in disaggregation_list:
                    disaggregation_list.append(disaggregation.disaggregation.name)
                    disaggregation_cols.append(disaggregation.disaggregation.name)
                else:
                    continue

            if disaggregations:
                for disaggregation_col in disaggregation_cols:
                    if disaggregation_col not in columns:
                        columns.append(disaggregation_col)
    # write the column header to the csv file

    writer.writerow(columns)

    # retrieving the rows from the queryset

    plan_reports = last_month_report.activityplanreport_set.all()
    for plan_report in plan_reports:
        location_reports = plan_report.targetlocationreport_set.all()
        for location_report in location_reports:
            # Create a dictionary to hold disaggregation data
            disaggregation_data = {}
            row = [
                last_month_report.project.code if last_month_report.project.code else None,
                plan_report.activity_plan.indicator.name if plan_report.activity_plan.indicator else None,
                plan_report.activity_plan.activity_domain.name if plan_report.activity_plan.activity_domain else None,
                plan_report.activity_plan.activity_type.name if plan_report.activity_plan.activity_type else None,
                ", ".join([responseType.name for responseType in plan_report.response_types.all() if responseType]),
                location_report.target_location.implementing_partner.name
                if location_report.target_location.implementing_partner
                else None,
                plan_report.activity_plan.package_type,
                plan_report.activity_plan.unit_type,
                plan_report.activity_plan.units,
                plan_report.activity_plan.no_of_transfers,
                plan_report.activity_plan.grant_type,
                plan_report.activity_plan.transfer_category,
                plan_report.activity_plan.currency,
                plan_report.activity_plan.transfer_mechanism_type,
                plan_report.activity_plan.implement_modility_type,
                plan_report.get_beneficiary_status_display(),
                # write target location
                location_report.target_location.country.name,
                location_report.target_location.country.code,
                location_report.target_location.province.code,
                location_report.target_location.province.name,
                location_report.target_location.district.code,
                location_report.target_location.district.name,
                location_report.target_location.zone,
                location_report.target_location.location_type,
                location_report.target_location.facility_site_type,
                location_report.target_location.facility_monitoring,
                location_report.target_location.facility_id,
                location_report.target_location.facility_name,
                location_report.target_location.facility_lat,
                location_report.target_location.facility_long,
            ]
            disaggregation_locations = location_report.disaggregationlocationreport_set.all()
            disaggregation_location_list = {
                disaggregation_location.disaggregation.name: str(disaggregation_location.reached)
                for disaggregation_location in disaggregation_locations
            }

            # Update disaggregation_data with values from disaggregation_location_list
            for disaggregation_entry in disaggregation_list:
                if disaggregation_entry not in disaggregation_location_list:
                    disaggregation_data[disaggregation_entry] = None

            disaggregation_location_list.update(disaggregation_data)

            # Append disaggregation values to the row in the order of columns
            for header in columns:
                if header in disaggregation_location_list:
                    row.append(disaggregation_location_list[header])

            # Add row to the list of rows

            writer.writerow(row)

    return response
