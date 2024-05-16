import calendar
from collections import defaultdict
from datetime import datetime, timedelta

import pandas as pd
from django import forms
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import cache_control

# from rh.forms import ProjectIndicatorTypeForm
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

from .forms import (
    ActivityPlanReportForm,
    DisaggregationReportFormSet,
    IndicatorsForm,
    MonthlyReportFileUpload,
    ProjectMonthlyReportForm,
    TargetLocationReportFormSet,
)
from .models import (
    ActivityPlanReport,
    DisaggregationLocationReport,
    ProjectMonthlyReport,
    TargetLocationReport,
)

RECORDS_PER_PAGE = 10


@cache_control(no_store=True)
@login_required
def index_project_report_view(request, project):
    """Project Monthly Report View"""
    # report_filter = ReportFilterForm(
    #     request.GET,
    #     queryset=ProjectMonthlyReport.objects.all()
    #     .prefetch_related("project","ActivityPlanReport")
    #     .order_by("-id"),
    # )
    # page_obj = Paginator(report_filter.qs, RECORDS_PER_PAGE)
    # page = request.GET.get('page')
    # project_page = page_obj.get_page(page)
    # total_pages = "a" * project_page.paginator.num_pages

    project = get_object_or_404(Project, pk=project)
    project_reports = ProjectMonthlyReport.objects.filter(project=project.pk)
    active_project_reports = project_reports.filter(active=True)
    project_report_archive = project_reports.filter(active=False)
    project_reports_todo = active_project_reports.filter(state__in=["todo", "pending", "submit", "reject"])
    project_report_complete = active_project_reports.filter(state="complete")

    context = {
        "project": project,
        "project_reports": active_project_reports,
        "project_reports_todo": project_reports_todo,
        "project_report_complete": project_report_complete,
        "project_report_archive": project_report_archive,
        # "report_filter":report_filter,
        "project_view": False,
        "financial_view": False,
        "reports_view": True,
    }

    return render(request, "project_reports/views/monthly_reports_view_base.html", context)


@cache_control(no_store=True)
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
                report.active = True
                report.state = "pending"
                report.save()
                return redirect(
                    "create_project_monthly_report_progress",
                    project=project.pk,
                    report=report.pk,
                )

        context = {
            "project": project,
            "report_form": form,
            "project_view": False,
            "financial_view": False,
            "reports_view": True,
        }
        return render(request, "project_reports/forms/monthly_report_form.html", context)

    return redirect(
        "project_reports_home",
        project=project.pk,
    )


def copy_project_monthly_report_view(request, report):
    """Copy report view"""
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    message = ""
    success = False
    if monthly_report:
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
                        success = copy_disaggregation_location_reports(
                            new_location_report, disaggregation_location_report
                        )

        else:
            message = "Atleast one last month approved report is required."
        # Save the changes made to the new monthly report.
        monthly_report.state = "todo"
        monthly_report.save()

        url = reverse(
            "update_project_monthly_report_progress",
            kwargs={
                "project": monthly_report.project.pk,
                "report": monthly_report.pk,
            },
        )

        # Return the URL in a JSON response
        response_data = {"success": success, "redirect_url": url, "message": message}
        return JsonResponse(response_data)


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
        new_plan_report.active = True

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


def delete_project_monthly_report_view(request, report):
    """Delete View for Project Reports"""
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    project = monthly_report.project
    # TODO: Check access rights before deleting
    if monthly_report:
        monthly_report.delete()
    # Generate the URL using reverse
    url = reverse(
        "project_reports_home",
        kwargs={
            "project": project.pk,
        },
    )

    # Return the URL in a JSON response
    response_data = {"redirect_url": url}
    return JsonResponse(response_data)


def archive_project_monthly_report_view(request, report):
    """Archive View for Project Reports"""
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    project = monthly_report.project
    if monthly_report:
        monthly_report.active = False
        monthly_report.save()
    # Generate the URL using reverse
    url = reverse(
        "project_reports_home",
        kwargs={
            "project": project.pk,
        },
    )

    # Return the URL in a JSON response
    response_data = {"redirect_url": url}
    return JsonResponse(response_data)


def unarchive_project_monthly_report_view(request, report):
    """Unarchive View for Project Reports"""
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    project = monthly_report.project
    if monthly_report:
        monthly_report.active = True
        monthly_report.state = "todo"
        monthly_report.save()
    # Generate the URL using reverse
    url = reverse(
        "project_reports_home",
        kwargs={
            "project": project.pk,
        },
    )

    # Return the URL in a JSON response
    response_data = {"redirect_url": url}
    return JsonResponse(response_data)


@cache_control(no_store=True)
@login_required
def details_monthly_progress_view(request, project, report):
    """Project Monthly Report Read View"""
    project = get_object_or_404(Project, pk=project)
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    activity_reports = monthly_report.activityplanreport_set.select_related("activity_plan", "indicator")

    context = {
        "project": project,
        "monthly_report": monthly_report,
        "activity_reports": activity_reports,
        "project_view": False,
        "financial_view": False,
        "reports_view": True,
    }

    return render(request, "project_reports/views/monthly_report_view.html", context)


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


@cache_control(no_store=True)
@login_required
def create_project_monthly_report_progress_view(request, project, report):
    """Create View"""
    (
        project,
        project_state,
        activity_plans,
        target_locations,
        monthly_report_instance,
    ) = get_project_and_report_details(project, report)

    (
        target_location_provinces,
        target_location_districts,
        target_location_zones,
    ) = get_target_locations_domain(target_locations)

    activity_plans = [plan for plan in activity_plans]

    # Create the activity plan formset with initial data from the project
    ActivityReportFormset = inlineformset_factory(
        ProjectMonthlyReport,
        ActivityPlanReport,
        form=ActivityPlanReportForm,
        extra=len(activity_plans),
        can_delete=True,
    )

    activity_report_formset = ActivityReportFormset(
        request.POST or None,
        instance=monthly_report_instance,
    )

    location_report_formsets = []
    for activity_report in activity_report_formset:
        # Create a target location formset for each activity plan form
        location_report_formset = TargetLocationReportFormSet(
            request.POST or None,
            instance=activity_report.instance,
            prefix=f"locations_report_{activity_report.prefix}",
        )
        for location_report_form in location_report_formset.forms:
            # Create a disaggregation formset for each target location form
            disaggregation_report_formset = DisaggregationReportFormSet(
                request.POST or None,
                instance=location_report_form.instance,
                prefix=f"disaggregation_report_{location_report_form.prefix}",
            )
            location_report_form.disaggregation_report_formset = disaggregation_report_formset

        # Loop through the forms in the formset and set queryset values for specific fields
        if not request.POST:
            for i, form in enumerate(location_report_formset.forms):
                if i < len(target_locations):
                    form.fields["province"].queryset = Location.objects.filter(id__in=target_location_provinces)
                    form.fields["district"].queryset = Location.objects.filter(id__in=target_location_districts)
                    form.fields["zone"].queryset = Location.objects.filter(id__in=target_location_zones)

        location_report_formsets.append(location_report_formset)

    # Loop through the forms in the formset and set initial and queryset values for specific fields
    if not request.POST:
        for i, form in enumerate(activity_report_formset.forms):
            if i < len(activity_plans):
                activity_plan = activity_plans[i]
                if not form.instance.pk:
                    form.initial = {
                        "activity_plan": activity_plan,
                        "project_id": project,
                        "indicator": activity_plan.indicator,
                    }
                    if activity_plan.indicator:
                        form.fields["indicator"].queryset = Indicator.objects.filter(id=activity_plan.indicator.id)

    if request.method == "POST":
        if activity_report_formset.is_valid():
            for activity_report_form in activity_report_formset:
                indicator_data = activity_report_form.cleaned_data.get("indicator")
                if indicator_data:
                    activity_report = activity_report_form.save(commit=False)
                    activity_report.monthly_report = monthly_report_instance
                    activity_report.save()
                    activity_report_form.save_m2m()

                    # Process target location forms and their disaggregation forms
                    activity_report_target = 0
                    for location_report_formset in location_report_formsets:
                        if location_report_formset.instance == activity_report:
                            if location_report_formset.is_valid():
                                for location_report_form in location_report_formset:
                                    cleaned_data = location_report_form.cleaned_data
                                    province = cleaned_data.get("province")
                                    district = cleaned_data.get("district")

                                    if province and district:
                                        location_report_instance = location_report_form.save(commit=False)
                                        location_report_instance.activity_plan_report = activity_report
                                        location_report_instance.save()

                                    if hasattr(
                                        location_report_form,
                                        "disaggregation_report_formset",
                                    ):
                                        disaggregation_report_formset = (
                                            location_report_form.disaggregation_report_formset.forms
                                        )

                                        # Delete the exisiting instances of the disaggregation location
                                        # reports and create new
                                        # based on the indicator disaggregations
                                        new_report_disaggregations = []
                                        for disaggregation_report_form in disaggregation_report_formset:
                                            if disaggregation_report_form.is_valid():
                                                if (
                                                    disaggregation_report_form.cleaned_data != {}
                                                    # and disaggregation_report_form.cleaned_data.get("target")
                                                    and disaggregation_report_form.cleaned_data.get("target") > 0
                                                ):
                                                    disaggregation_report_instance = disaggregation_report_form.save(
                                                        commit=False
                                                    )
                                                    disaggregation_report_instance.target_location = (
                                                        location_report_instance
                                                    )
                                                    disaggregation_report_instance.save()
                                                    activity_report_target += disaggregation_report_instance.target
                                                    new_report_disaggregations.append(disaggregation_report_instance.id)

                                        all_report_disaggregations = (
                                            location_report_form.instance.disaggregationlocationreport_set.all()
                                        )
                                        for disaggregation_report in all_report_disaggregations:
                                            if disaggregation_report.id not in new_report_disaggregations:
                                                disaggregation_report.delete()

                    activity_report.target_achieved = activity_report_target
                    activity_report.save()

            # activity_report_formset.save()
            return redirect(
                "view_monthly_report",
                project=project.pk,
                report=monthly_report_instance.pk,
            )
        else:
            # TODO:
            # Handle invalid activity_plan_formset
            # Add error handling code here
            pass

    combined_formset = zip(activity_report_formset.forms, location_report_formsets)

    context = {
        "project": project,
        "monthly_report": monthly_report_instance,
        "activity_plans": activity_plans,
        "report_form": monthly_report_instance,
        "activity_report_formset": activity_report_formset,
        "combined_formset": combined_formset,
        "project_view": False,
        "financial_view": False,
        "reports_view": True,
        "indicator_form": IndicatorsForm,
    }

    return render(request, "project_reports/forms/monthly_report_progress_form.html", context)


@cache_control(no_store=True)
@login_required
def update_project_monthly_report_progress_view(request, project, report):
    """Update View"""

    (
        project,
        project_state,
        activity_plans,
        target_locations,
        monthly_report_instance,
    ) = get_project_and_report_details(project, report)

    activity_plan_reports = monthly_report_instance.activityplanreport_set.all()

    if not activity_plan_reports:
        return redirect(
            "create_project_monthly_report_progress",
            project=project.pk,
            report=monthly_report_instance.pk,
        )

    (
        target_location_provinces,
        target_location_districts,
        target_location_zones,
    ) = get_target_locations_domain(target_locations)

    activity_plans = [plan for plan in activity_plans]

    # Create the activity plan formset with initial data from the project
    ActivityReportFormset = inlineformset_factory(
        ProjectMonthlyReport,
        ActivityPlanReport,
        form=ActivityPlanReportForm,
        extra=0,
        can_delete=True,
    )

    activity_report_formset = ActivityReportFormset(
        request.POST or None,
        instance=monthly_report_instance,
    )

    location_report_formsets = []
    for activity_report in activity_report_formset:
        # Create a target location formset for each activity plan form
        location_report_formset = TargetLocationReportFormSet(
            request.POST or None,
            instance=activity_report.instance,
            prefix=f"locations_report_{activity_report.prefix}",
        )
        for location_report_form in location_report_formset.forms:
            # Create a disaggregation formset for each target location form
            disaggregation_report_formset = DisaggregationReportFormSet(
                request.POST or None,
                instance=location_report_form.instance,
                prefix=f"disaggregation_report_{location_report_form.prefix}",
            )
            location_report_form.disaggregation_report_formset = disaggregation_report_formset

        # Loop through the forms in the formset and set queryset values for specific fields
        if not request.POST:
            for i, form in enumerate(location_report_formset.forms):
                if i < len(target_locations):
                    form.fields["province"].queryset = Location.objects.filter(id__in=target_location_provinces)
                    form.fields["district"].queryset = Location.objects.filter(id__in=target_location_districts)
                    form.fields["zone"].queryset = Location.objects.filter(id__in=target_location_zones)

        location_report_formsets.append(location_report_formset)

    # Loop through the forms in the formset and set initial and queryset values for specific fields
    if not request.POST:
        for i, form in enumerate(activity_report_formset.forms):
            if i < len(activity_plans):
                activity_plan = activity_plans[i]
                if activity_plan.indicator:
                    form.fields["indicator"].queryset = Indicator.objects.filter(id=activity_plan.indicator.id)

    if request.method == "POST":
        if activity_report_formset.is_valid():
            for activity_report_form in activity_report_formset:
                indicator_data = activity_report_form.cleaned_data.get("indicator", "")
                if indicator_data:
                    activity_report = activity_report_form.save(commit=False)
                    activity_report.monthly_report = monthly_report_instance
                    activity_report.save()
                    activity_report_form.save_m2m()

                    # Process target location forms and their disaggregation forms
                    activity_report_target = 0
                    for location_report_formset in location_report_formsets:
                        if location_report_formset.instance == activity_report:
                            if location_report_formset.is_valid():
                                for location_report_form in location_report_formset:
                                    cleaned_data = location_report_form.cleaned_data
                                    province = cleaned_data.get("province", "")
                                    district = cleaned_data.get("district", "")

                                    if province and district:
                                        location_report_instance = location_report_form.save(commit=False)
                                        location_report_instance.activity_plan_report = activity_report
                                        location_report_instance.save()

                                    if hasattr(
                                        location_report_form,
                                        "disaggregation_report_formset",
                                    ):
                                        disaggregation_report_formset = (
                                            location_report_form.disaggregation_report_formset.forms
                                        )

                                        # Delete the exisiting instances of the disaggregation
                                        # location reports and create new
                                        # based on the indicator disaggregations
                                        new_report_disaggregations = []
                                        for disaggregation_report_form in disaggregation_report_formset:
                                            if disaggregation_report_form.is_valid():
                                                if (
                                                    disaggregation_report_form.cleaned_data != {}
                                                    and disaggregation_report_form.cleaned_data.get("target", 0) > 0
                                                ):
                                                    disaggregation_report_instance = disaggregation_report_form.save(
                                                        commit=False
                                                    )
                                                    disaggregation_report_instance.target_location = (
                                                        location_report_instance
                                                    )
                                                    disaggregation_report_instance.save()
                                                    activity_report_target += disaggregation_report_instance.target
                                                    new_report_disaggregations.append(disaggregation_report_instance.id)

                                        all_report_disaggregations = (
                                            location_report_form.instance.disaggregationlocationreport_set.all()
                                        )
                                        for disaggregation_report in all_report_disaggregations:
                                            if disaggregation_report.id not in new_report_disaggregations:
                                                disaggregation_report.delete()

                    activity_report.target_achieved = activity_report_target
                    activity_report.save()

            return redirect(
                "view_monthly_report",
                project=project.pk,
                report=monthly_report_instance.pk,
            )
        else:
            # TODO:
            # Handle invalid activity_plan_report_formset
            # Add error handling code here
            pass

    combined_formset = zip(activity_report_formset.forms, location_report_formsets)

    context = {
        "project": project,
        "monthly_report": monthly_report_instance,
        "activity_plans": activity_plans,
        "report_form": monthly_report_instance,
        "activity_report_formset": activity_report_formset,
        "combined_formset": combined_formset,
        "project_view": False,
        "financial_view": False,
        "reports_view": True,
    }

    return render(request, "project_reports/forms/monthly_report_progress_form.html", context)


@login_required
def get_location_report_empty_form(request):
    """Get an empty location Report form for a project"""
    # Get the project object based on the provided project ID
    project = get_object_or_404(Project, pk=request.POST.get("project"))

    # Get all existing target locaitions for the project
    target_locations = project.targetlocation_set.select_related("province", "district", "zone").all()

    (
        target_location_provinces,
        target_location_districts,
        target_location_zones,
    ) = get_target_locations_domain(target_locations)

    ActivityReportFormset = inlineformset_factory(
        ProjectMonthlyReport,
        ActivityPlanReport,
        form=ActivityPlanReportForm,
        can_delete=True,
    )

    # Create an instance of ActivityPlanFormSet using the project instance and form_kwargs
    activity_report_formset = ActivityReportFormset()

    # Get the prefix index from the request
    prefix_index = request.POST.get("prefix_index")

    activity_domain_id = request.POST.get("activity_domain", None)
    activity_domain = None
    if activity_domain_id:
        activity_domain = get_object_or_404(ActivityDomain, pk=activity_domain_id)

    # Create an instance of TargetLocationFormSet with a prefixed name
    location_report_formset = TargetLocationReportFormSet(
        prefix=f"locations_report_{activity_report_formset.prefix}-{prefix_index}"
    )

    # for target_location_form in target_location_formset.forms:
    # Create a disaggregation formset for each target location form
    location_report_form = location_report_formset.empty_form

    # Set the Target locations domain based on the activity plan
    activity_plan = request.POST.get("activity_plan", None)
    if activity_plan:
        location_report_form.fields["target_location"].queryset = TargetLocation.objects.filter(
            activity_plan=activity_plan
        )

    # Check if the activity plan is selected
    if activity_domain:
        # Get clusters associated with the activity plan's domain
        clusters = activity_domain.clusters.all()

        # Get only the relevant facility types - related to cluster
        location_report_form.fields["facility_site_type"].queryset = FacilitySiteType.objects.filter(
            cluster__in=clusters
        )

        cluster_has_nhs_code = any(cluster.has_nhs_code for cluster in clusters)
        # If at least one cluster has NHS code, add the NHS code field to the form
        if cluster_has_nhs_code:
            location_report_form.fields["nhs_code"] = forms.CharField(max_length=200, required=True)
        else:
            location_report_form.fields.pop("nhs_code", None)
    else:
        location_report_form.fields["facility_site_type"].queryset = FacilitySiteType.objects.all()

    location_report_form.fields["province"].queryset = Location.objects.filter(id__in=target_location_provinces)
    location_report_form.fields["district"].queryset = Location.objects.filter(id__in=target_location_districts)
    location_report_form.fields["zone"].queryset = Location.objects.filter(id__in=target_location_zones)

    disaggregation_report_formset = DisaggregationReportFormSet(
        request.POST or None,
        instance=location_report_form.instance,
        prefix=f"disaggregation_report_{location_report_form.prefix}",
    )
    location_report_form.disaggregation_report_formset = disaggregation_report_formset

    # Prepare context for rendering the target location form template
    context = {
        "location_report_form": location_report_form,
    }

    # Render the target location form template and generate HTML
    html = render_to_string("project_reports/forms/location_report_empty_form.html", context)

    # Return JSON response containing the generated HTML
    return JsonResponse({"html": html})


@login_required
def get_target_location_auto_fields(request):
    try:
        target_location = TargetLocation.objects.get(pk=request.POST.get("target_location"))
        data = {
            "country": target_location.country.id if target_location.country else None,
            "province": target_location.province.id if target_location.province else None,
            "district": target_location.district.id if target_location.district else None,
            "zone": target_location.zone.id if target_location.zone else None,
            # 'location_type': target_location.location_type.id if target_location.location_type else None,
            "facility_site_type": target_location.facility_site_type.id if target_location.facility_site_type else None,
            "facility_monitoring": target_location.facility_monitoring,
            "facility_name": target_location.facility_name,
            "facility_id": target_location.facility_id,
            "facility_lat": target_location.facility_lat,
            "facility_long": target_location.facility_long,
            "nhs_code": target_location.nhs_code,
        }
        return JsonResponse(data)
    except TargetLocation.DoesNotExist:
        return JsonResponse({"error": "TargetLocation not found"}, status=404)


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


@login_required
def get_disaggregations_report_empty_forms(request):
    """Get target location empty form"""

    # Create a dictionary to hold disaggregation forms per location prefix
    location_disaggregation_report_dict = {}
    if request.POST.get("indicator"):
        indicator = get_object_or_404(Indicator, pk=int(request.POST.get("indicator")))

        # Get selected locations prefixes
        locations_report_prefix = request.POST.getlist("locations_prefixes[]")

        # Loop through each Indicator and retrieve its related Disaggregations
        related_disaggregations = indicator.disaggregation_set.all()

        initial_data = []

        # Populate initial data with related disaggregations
        if related_disaggregations:
            for disaggregation in related_disaggregations:
                initial_data.append({"disaggregation": disaggregation})

            # Create DisaggregationFormSet for each location prefix
            for location_report_prefix in locations_report_prefix:
                DisaggregationReportFormSet.extra = len(related_disaggregations)
                disaggregation_report_formset = DisaggregationReportFormSet(
                    prefix=f"disaggregation_report_{location_report_prefix}",
                    initial=initial_data,
                )

                # Generate HTML for each disaggregation form and store in dictionary
                for disaggregation_report_form in disaggregation_report_formset.forms:
                    context = {
                        "disaggregation_report_form": disaggregation_report_form,
                    }
                    html = render_to_string(
                        "project_reports/forms/disaggregation_report_empty_form.html",
                        context,
                    )

                    if location_report_prefix in location_disaggregation_report_dict:
                        location_disaggregation_report_dict[location_report_prefix].append(html)
                    else:
                        location_disaggregation_report_dict.update({location_report_prefix: [html]})

        # Set back extra to 0 to avoid empty forms if refreshed.
        DisaggregationReportFormSet.extra = 0

    # Return JSON response containing generated HTML forms
    return JsonResponse(location_disaggregation_report_dict)


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


@cache_control(no_store=True)
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


def submit_monthly_report_view(request, report):
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    # TODO: Handle with access rights and groups
    monthly_report.state = "complete"
    monthly_report.submitted_on = timezone.now()
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
                        country_name = row.get("country")
                        province_name = row.get("province")
                        district_name = row.get("district")
                        zone_name = row.get("zone")
                        location_type_name = row.get("location_type")
                        facility_site_type_name = row.get("facility_site_type")

                        # Validate required columns
                        columns_to_check = [
                            "indicator",
                            "activity_domain",
                            "activity_type",
                            "country",
                            "province",
                            "district",
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
                            country = get_object_or_404(Location, name=country_name)
                            province = get_object_or_404(Location, name=province_name)
                            district = get_object_or_404(Location, name=district_name)
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
