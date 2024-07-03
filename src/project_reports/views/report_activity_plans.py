from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.db.models import Count

from rh.models import (
    Indicator,
    Location,
    Project,
)

from ..forms import (
    ActivityPlanReportForm,
    DisaggregationReportFormSet,
    IndicatorsForm,
    TargetLocationReportFormSet,
)
from ..models import (
    ActivityPlanReport,
    ProjectMonthlyReport,
)


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


@login_required
def list_report_activity_plans(request, project, report):
    """Create View"""
    (
        project,
        project_state,
        activity_plans,
        target_locations,
        monthly_report_instance,
    ) = get_project_and_report_details(project, report)

    activity_plans = [plan for plan in activity_plans]

    report_plans = ActivityPlanReport.objects.filter(monthly_report=monthly_report_instance.pk).annotate(
        report_target_location_count=Count("targetlocationreport")
    )
    if not report_plans:
        for plan in activity_plans:
            if plan.state == 'in-progress':
                ActivityPlanReport.objects.create(
                    monthly_report_id=monthly_report_instance.pk,
                    activity_plan_id=plan.pk,
                    indicator_id=plan.indicator.pk
                )

        report_plans = ActivityPlanReport.objects.filter(monthly_report=monthly_report_instance.pk).annotate(
            report_target_location_count=Count("targetlocationreport")
        )

    paginator = Paginator(report_plans, 10)  # Show 10 activity plans per page
    page = request.GET.get("page", 1)
    report_plans = paginator.get_page(page)
    report_plans.adjusted_elided_pages = paginator.get_elided_page_range(page)

    context = {
        "project": project,
        "monthly_report": monthly_report_instance,
        "report_plans": report_plans,
        "report_view": False,
        "report_activities": True,
        "report_locations": False,
    }

    return render(request, "project_reports/report_activity_plans/activity_plans_list.html", context)


@login_required
def update_report_activity_plans(request, project, report, plan):
    """Update an existing activity plan"""
    report_instance = get_object_or_404(ProjectMonthlyReport.objects.select_related("project"), pk=report)
    report_plan = get_object_or_404(ActivityPlanReport, pk=plan)

    if request.method == "POST":
        form = ActivityPlanReportForm(request.POST, instance=report_plan)
        if form.is_valid():
            form.save()
            return redirect("list_report_activity_plans", project=report_instance.project.pk,
                            report=report_instance.pk)
    else:
        form = ActivityPlanReportForm(instance=report_plan)
    context = {"form": form,
               "report_activity_plan": report_plan,
               "project": report_instance.project,
               "monthly_report": report_instance,
               "report_view": False,
               "report_activities": True,
               "report_locations": False,
               }
    return render(request, "project_reports/report_activity_plans/activity_plan_form.html", context=context)


# @login_required
# def create_project_monthly_report_progress_view(request, project, report):
#     """Create View"""
#     (
#         project,
#         project_state,
#         activity_plans,
#         target_locations,
#         monthly_report_instance,
#     ) = get_project_and_report_details(project, report)
#
#     (
#         target_location_provinces,
#         target_location_districts,
#         target_location_zones,
#     ) = get_target_locations_domain(target_locations)
#
#     activity_plans = [plan for plan in activity_plans]
#
#     # Create the activity plan formset with initial data from the project
#     ActivityReportFormset = inlineformset_factory(
#         ProjectMonthlyReport,
#         ActivityPlanReport,
#         form=ActivityPlanReportForm,
#         extra=len(activity_plans),
#         can_delete=True,
#     )
#
#     initial_data = []
#     for _ in activity_plans:
#         initial_data.append({"monthly_report": monthly_report_instance.id})
#
#     activity_report_formset = ActivityReportFormset(
#         request.POST or None, instance=monthly_report_instance, initial=initial_data
#     )
#
#     location_report_formsets = []
#     for activity_report in activity_report_formset:
#         # Create a target location formset for each activity plan form
#         location_report_formset = TargetLocationReportFormSet(
#             request.POST or None,
#             instance=activity_report.instance,
#             prefix=f"locations_report_{activity_report.prefix}",
#         )
#         for location_report_form in location_report_formset.forms:
#             # Create a disaggregation formset for each target location form
#             disaggregation_report_formset = DisaggregationReportFormSet(
#                 request.POST or None,
#                 instance=location_report_form.instance,
#                 prefix=f"disaggregation_report_{location_report_form.prefix}",
#             )
#             location_report_form.disaggregation_report_formset = disaggregation_report_formset
#
#         # Loop through the forms in the formset and set queryset values for specific fields
#         if not request.POST:
#             for i, form in enumerate(location_report_formset.forms):
#                 if i < len(target_locations):
#                     form.fields["province"].queryset = Location.objects.filter(id__in=target_location_provinces)
#                     form.fields["district"].queryset = Location.objects.filter(id__in=target_location_districts)
#                     form.fields["zone"].queryset = Location.objects.filter(id__in=target_location_zones)
#
#         location_report_formsets.append(location_report_formset)
#
#     # Loop through the forms in the formset and set initial and queryset values for specific fields
#     if not request.POST:
#         for i, form in enumerate(activity_report_formset.forms):
#             if i < len(activity_plans):
#                 activity_plan = activity_plans[i]
#                 if not form.instance.pk:
#                     form.initial = {
#                         "activity_plan": activity_plan,
#                         "project_id": project,
#                         "indicator": activity_plan.indicator,
#                     }
#                     if activity_plan.indicator:
#                         form.fields["indicator"].queryset = Indicator.objects.filter(id=activity_plan.indicator.id)
#
#     if request.method == "POST":
#         if activity_report_formset.is_valid():
#             for activity_report_form in activity_report_formset:
#                 indicator_data = activity_report_form.cleaned_data.get("indicator")
#                 if indicator_data:
#                     activity_report = activity_report_form.save(commit=False)
#                     activity_report.monthly_report = monthly_report_instance
#                     activity_report.save()
#                     activity_report_form.save_m2m()
#
#                     # Process target location forms and their disaggregation forms
#                     activity_report_target = 0
#                     for location_report_formset in location_report_formsets:
#                         if location_report_formset.instance == activity_report:
#                             if location_report_formset.is_valid():
#                                 for location_report_form in location_report_formset:
#                                     cleaned_data = location_report_form.cleaned_data
#                                     province = cleaned_data.get("province")
#                                     district = cleaned_data.get("district")
#
#                                     if province and district:
#                                         location_report_instance = location_report_form.save(commit=False)
#                                         location_report_instance.activity_plan_report = activity_report
#                                         location_report_instance.save()
#
#                                     if hasattr(
#                                             location_report_form,
#                                             "disaggregation_report_formset",
#                                     ):
#                                         disaggregation_report_formset = (
#                                             location_report_form.disaggregation_report_formset.forms
#                                         )
#
#                                         # Delete the exisiting instances of the disaggregation location
#                                         # reports and create new
#                                         # based on the indicator disaggregations
#                                         new_report_disaggregations = []
#                                         for disaggregation_report_form in disaggregation_report_formset:
#                                             if disaggregation_report_form.is_valid():
#                                                 if (
#                                                         disaggregation_report_form.cleaned_data != {}
#                                                         # and disaggregation_report_form.cleaned_data.get("target")
#                                                         and disaggregation_report_form.cleaned_data.get("target") > 0
#                                                 ):
#                                                     disaggregation_report_instance = disaggregation_report_form.save(
#                                                         commit=False
#                                                     )
#                                                     disaggregation_report_instance.target_location = (
#                                                         location_report_instance
#                                                     )
#                                                     disaggregation_report_instance.save()
#                                                     activity_report_target += disaggregation_report_instance.target
#                                                     new_report_disaggregations.append(disaggregation_report_instance.id)
#
#                                         all_report_disaggregations = (
#                                             location_report_form.instance.disaggregationlocationreport_set.all()
#                                         )
#                                         for disaggregation_report in all_report_disaggregations:
#                                             if disaggregation_report.id not in new_report_disaggregations:
#                                                 disaggregation_report.delete()
#
#                     activity_report.target_achieved = activity_report_target
#                     activity_report.save()
#
#             # activity_report_formset.save()
#             return redirect(
#                 "view_monthly_report",
#                 project=project.pk,
#                 report=monthly_report_instance.pk,
#             )
#         else:
#             # TODO:
#             # Handle invalid activity_plan_formset
#             # Add error handling code here
#             pass
#
#     combined_formset = zip(activity_report_formset.forms, location_report_formsets)
#
#     context = {
#         "project": project,
#         "monthly_report": monthly_report_instance,
#         "activity_plans": activity_plans,
#         "report_form": monthly_report_instance,
#         "activity_report_formset": activity_report_formset,
#         "combined_formset": combined_formset,
#         "project_view": False,
#         "financial_view": False,
#         "reports_view": True,
#         "indicator_form": IndicatorsForm,
#     }
#
#     return render(request, "project_reports/forms/monthly_report_progress_form.html", context)


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
