import calendar
import json
from datetime import datetime, timedelta
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import cache_control

# from .filter import ReportFilterForm
from rh.models import ImplementationModalityType, Indicator, Location, Project

from .forms import (
    ActivityPlanReportForm,
    DisaggregationReportFormSet,
    IndicatorsForm,
    ProjectMonthlyReportForm,
    TargetLocationReportFormSet,
)
from .models import ActivityPlanReport, DisaggregationLocationReport, ProjectMonthlyReport, TargetLocationReport

# from django.core.paginator import Paginator
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


def copy_project_monthly_report_view(request, report):
    """Copy report view"""
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)

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
                        copy_disaggregation_location_reports(new_location_report, disaggregation_location_report)

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
        response_data = {"redirect_url": url}
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


def get_target_locations_doamin(target_locations):
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
    ) = get_target_locations_doamin(target_locations)

    activity_plans = activity_plans.prefetch_related("indicators")
    project_indicators = list(chain.from_iterable(activity.indicators.all() for activity in activity_plans))

    # Create the activity plan formset with initial data from the project
    ActivityReportFormset = inlineformset_factory(
        ProjectMonthlyReport,
        ActivityPlanReport,
        form=ActivityPlanReportForm,
        extra=len(project_indicators),
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
        # Create a dictionary to map indicator IDs to ActivityPlans
        indicator_activity_plan_map = {
            indicator.id: activity_plan
            for activity_plan in activity_plans
            for indicator in activity_plan.indicators.all()
        }
        for i, form in enumerate(activity_report_formset.forms):
            if i < len(project_indicators):
                indicator = project_indicators[i]
                activity_plan = indicator_activity_plan_map.get(indicator.id)

                if activity_plan:
                    if not form.instance.pk:
                        form.initial = {
                            "activity_plan": activity_plan,
                            "project_id": project,
                            "indicator": indicator,
                        }
                    form.fields["indicator"].queryset = activity_plan.indicators.all()

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
                                                    and disaggregation_report_form.cleaned_data.get("target")
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
    ) = get_target_locations_doamin(target_locations)

    activity_plans = activity_plans.prefetch_related("indicators")
    project_indicators = list(chain.from_iterable(activity.indicators.all() for activity in activity_plans))

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
        # Create a dictionary to map indicator IDs to ActivityPlans
        indicator_activity_plan_map = {
            indicator.id: activity_plan
            for activity_plan in activity_plans
            for indicator in activity_plan.indicators.all()
        }
        for i, form in enumerate(activity_report_formset.forms):
            if i < len(project_indicators):
                indicator = project_indicators[i]
                activity_plan = indicator_activity_plan_map.get(indicator.id)

                if activity_plan:
                    if not form.instance.pk:
                        form.initial = {
                            "activity_plan": activity_plan,
                            "project_id": project,
                            "indicator": indicator,
                        }
                form.fields["indicator"].queryset = activity_plan.indicators.all().select_related("package_type")

    if request.method == "POST":
        if activity_report_formset.is_valid():
            for activity_report_form in activity_report_formset:
                indicator_data = activity_report_form.cleaned_data.get("indicator", "")
                if indicator_data:
                    activity_report = activity_report_form.save(commit=False)
                    activity_report.monthly_report = monthly_report_instance
                    activity_report.save()

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
    ) = get_target_locations_doamin(target_locations)

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

    # Create an instance of TargetLocationFormSet with a prefixed name
    location_report_formset = TargetLocationReportFormSet(
        prefix=f"locations_report_{activity_report_formset.prefix}-{prefix_index}"
    )

    # for target_location_form in target_location_formset.forms:
    # Create a disaggregation formset for each target location form
    location_report_form = location_report_formset.empty_form

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
def get_disaggregations_report_empty_forms(request):
    """Get target location empty form"""

    # Create a dictionary to hold disaggregation forms per location prefix
    location_disaggregation_report_dict = {}
    if request.POST.get("indicator"):
        # Get selected indicators
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
    monthly_report.state = "submit"
    monthly_report.submitted_on = timezone.now()
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


def get_indicator_reference(request):
    if request.method == "POST":
        indicator = json.loads(request.POST.get("id"))
        im = ImplementationModalityType.objects.all().values()
        print(im)
        indicator_refereces = (
            Indicator.objects.select_related(
                "package_type",
                "unit_type",
                "grant_type",
                "transfer_category",
                "transfer_mechanism_type",
                "implement_modility_type",
                "location_type",
                "currency",
            )
            .filter(id=indicator)
            .values()
        )
        print(indicator_refereces)
        data = {"data": list(indicator_refereces), "message": "success", "status": 200}
        return JsonResponse(data, safe=False)
