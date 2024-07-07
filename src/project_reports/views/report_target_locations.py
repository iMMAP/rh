from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Count

from django.contrib import messages
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from django.forms import inlineformset_factory

from rh.models import (
    Project,
)

from ..forms import (
    TargetLocationReportForm,
    DisaggregationLocationReportForm,
    BaseDisaggregationLocationReportFormSet,
)

from rh.models import (
    TargetLocation,
)

from ..models import (
    ActivityPlanReport,
    ProjectMonthlyReport,
    TargetLocationReport,
    DisaggregationLocationReport,
)


@login_required
def create_report_target_locations(request, project, report, plan):
    """Create View"""
    monthly_report = get_object_or_404(ProjectMonthlyReport.objects.select_related("project"), pk=report)
    plan_report = get_object_or_404(ActivityPlanReport.objects.select_related("monthly_report"), pk=plan)
    DisaggregationReportFormSet = inlineformset_factory(
        parent_model=TargetLocationReport,
        model=DisaggregationLocationReport,
        form=DisaggregationLocationReportForm,
        formset=BaseDisaggregationLocationReportFormSet,
        extra=1,
        can_delete=True,
    )

    initial_data = []
    # Loop through each Indicator and retrieve its related Disaggregations
    indicator = plan_report.indicator
    related_disaggregations = indicator.disaggregation_set.all()
    for disaggregation in related_disaggregations:
        initial_data.append({"disaggregation": disaggregation})
    DisaggregationReportFormSet.extra = len(related_disaggregations)

    if request.method == "POST":
        location_report_form = TargetLocationReportForm(request.POST or None)
        report_disaggregation_formset = DisaggregationReportFormSet(
            request.POST, instance=location_report_form.instance, plan_report=plan_report
        )
        if location_report_form.is_valid() and report_disaggregation_formset.is_valid():
            location_report = location_report_form.save(commit=False)
            location_report.activity_plan_report = plan_report
            location_report.save()

            report_disaggregation_formset.instance = location_report
            report_disaggregation_formset.save()
            messages.success(
                request,
                mark_safe(
                    f'The Report Target Location "<a href="{reverse("create_report_target_locations", args=[project, report, plan])}">{location_report}</a>" was added successfully.'
                ),
            )
            if "_continue" in request.POST:
                return redirect(
                    "update_report_target_locations",
                    project=monthly_report.project.pk,
                    report=monthly_report.pk,
                    plan=plan_report.pk,
                )
            elif "_save" in request.POST:
                return redirect(
                    "list_report_target_locations", project=monthly_report.project.pk, report=monthly_report.pk
                )
            elif "_addanother" in request.POST:
                return redirect(
                    "create_report_target_locations", project=monthly_report.project.pk, report=monthly_report.pk
                )
        else:
            messages.error(request, "The form is invalid. Please check the fields and try again.")
    else:
        location_report_form = TargetLocationReportForm(
            request.POST or None,
            report_plan=plan_report,
        )

        report_disaggregation_formset = DisaggregationReportFormSet(plan_report=plan_report, initial=initial_data)

    return render(
        request,
        "project_reports/report_target_locations/target_location_form.html",
        {
            "location_report_form": location_report_form,
            "report_disaggregation_formset": report_disaggregation_formset,
            "report_plan": plan_report,
            "monthly_report": monthly_report,
            "project": monthly_report.project,
            "report_view": False,
            "report_activities": False,
            "report_locations": True,
        },
    )


@login_required
def list_report_target_locations(request, project, report, plan=None):
    """Create View"""
    project = get_object_or_404(Project, pk=project)
    monthly_report_instance = get_object_or_404(ProjectMonthlyReport, pk=report)
    report_plan = None
    if plan:
        report_plan = get_object_or_404(ActivityPlanReport.objects.select_related("monthly_report"), pk=plan)
    if report_plan:
        report_locations = (
            TargetLocationReport.objects.filter(activity_plan_report_id=report_plan.pk)
            .order_by("-id")
            .annotate(report_disaggregation_locations_count=Count("disaggregationlocationreport"))
        )
    else:
        report_locations = (
            TargetLocationReport.objects.filter(activity_plan_report__monthly_report=report)
            .order_by("-id")
            .annotate(report_disaggregation_locations_count=Count("disaggregationlocationreport"))
        )

    paginator = Paginator(report_locations, 10)  # Show 10 activity plans per page
    page = request.GET.get("page", 1)
    report_locations = paginator.get_page(page)
    report_locations.adjusted_elided_pages = paginator.get_elided_page_range(page)

    context = {
        "project": project,
        "monthly_report": monthly_report_instance,
        "report_plan": report_plan,
        "report_target_locations": report_locations,
        "report_view": False,
        "report_activities": False,
        "report_locations": True,
    }

    return render(request, "project_reports/report_target_locations/target_locations_list.html", context)


@login_required
def update_report_target_locations(request, project, report, plan, location):
    """Update View"""
    monthly_report = get_object_or_404(ProjectMonthlyReport.objects.select_related("project"), pk=report)
    plan_report = get_object_or_404(ActivityPlanReport.objects.select_related("monthly_report"), pk=plan)

    # Get the existing location report to be updated
    location_report = get_object_or_404(TargetLocationReport, pk=location)

    DisaggregationReportFormSet = inlineformset_factory(
        parent_model=TargetLocationReport,
        model=DisaggregationLocationReport,
        form=DisaggregationLocationReportForm,
        formset=BaseDisaggregationLocationReportFormSet,
        extra=1,
        can_delete=True,
    )
    if request.method == "POST":
        location_report_form = TargetLocationReportForm(request.POST or None, instance=location_report)
        report_disaggregation_formset = DisaggregationReportFormSet(
            request.POST, instance=location_report, plan_report=plan_report
        )
        if location_report_form.is_valid() and report_disaggregation_formset.is_valid():
            location_report = location_report_form.save(commit=False)
            location_report.activity_plan_report = plan_report
            location_report.save()

            report_disaggregation_formset.instance = location_report
            report_disaggregation_formset.save()
            messages.success(
                request,
                mark_safe(
                    f'The Report Target Location "<a href="{reverse("update_report_target_locations", args=[project, report, plan, location])}">{location_report}</a>" was updated successfully.'
                ),
            )
            if "_continue" in request.POST:
                return redirect(
                    "update_report_target_locations",
                    project=monthly_report.project.pk,
                    report=monthly_report.pk,
                    plan=plan_report.pk,
                    pk=location_report.pk,
                )
            elif "_save" in request.POST:
                return redirect(
                    "list_report_target_locations", project=monthly_report.project.pk, report=monthly_report.pk
                )
            elif "_addanother" in request.POST:
                return redirect(
                    "create_report_target_locations", project=monthly_report.project.pk, report=monthly_report.pk
                )
        else:
            messages.error(request, "The form is invalid. Please check the fields and try again.")
    else:
        location_report_form = TargetLocationReportForm(request.POST or None, instance=location_report)
        report_disaggregation_formset = DisaggregationReportFormSet(
            request.POST or None, instance=location_report, plan_report=plan_report
        )

    return render(
        request,
        "project_reports/report_target_locations/target_location_form.html",
        {
            "location_report": location_report,
            "location_report_form": location_report_form,
            "report_disaggregation_formset": report_disaggregation_formset,
            "report_plan": plan_report,
            "monthly_report": monthly_report,
            "project": monthly_report.project,
            "report_view": False,
            "report_activities": False,
            "report_locations": True,
        },
    )


@login_required
def delete_location_report_view(request, location_report):
    """Delete the target location report"""
    location_report = get_object_or_404(TargetLocationReport, pk=location_report)
    plan_report = location_report.activity_plan_report
    monthly_report = location_report.activity_plan_report.monthly_report
    if location_report:
        location_report.delete()

        # # Recompute the achieved target for the location_report activity.
        # recompute_target_achieved(plan_report)

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
def get_target_location_auto_fields(request):
    try:
        target_location = TargetLocation.objects.get(pk=request.POST.get("target_location"))
        data = {
            "country": target_location.country.id if target_location.country else None,
            "province": target_location.province.id if target_location.province else None,
            "district": target_location.district.id if target_location.district else None,
            "zone": target_location.zone.id if target_location.zone else None,
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


# @login_required
# def update_project_monthly_report_progress_view(request, project, report):
#     """Update View"""
#
#     (
#         project,
#         project_state,
#         activity_plans,
#         target_locations,
#         monthly_report_instance,
#     ) = get_project_and_report_details(project, report)
#
#     activity_plan_reports = monthly_report_instance.activityplanreport_set.all()
#
#     if not activity_plan_reports:
#         return redirect(
#             "create_project_monthly_report_progress",
#             project=project.pk,
#             report=monthly_report_instance.pk,
#         )
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
#         extra=0,
#         can_delete=True,
#     )
#
#     activity_report_formset = ActivityReportFormset(
#         request.POST or None,
#         instance=monthly_report_instance,
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
#                 if activity_plan.indicator:
#                     form.fields["indicator"].queryset = Indicator.objects.filter(id=activity_plan.indicator.id)
#
#     if request.method == "POST":
#         if activity_report_formset.is_valid():
#             for activity_report_form in activity_report_formset:
#                 indicator_data = activity_report_form.cleaned_data.get("indicator", "")
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
#                                     province = cleaned_data.get("province", "")
#                                     district = cleaned_data.get("district", "")
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
#                                         # Delete the exisiting instances of the disaggregation
#                                         # location reports and create new
#                                         # based on the indicator disaggregations
#                                         new_report_disaggregations = []
#                                         for disaggregation_report_form in disaggregation_report_formset:
#                                             if disaggregation_report_form.is_valid():
#                                                 if (
#                                                         disaggregation_report_form.cleaned_data != {}
#                                                         and disaggregation_report_form.cleaned_data.get("target", 0) > 0
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
#             return redirect(
#                 "view_monthly_report",
#                 project=project.pk,
#                 report=monthly_report_instance.pk,
#             )
#         else:
#             # TODO:
#             # Handle invalid activity_plan_report_formset
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
#     }
#
#     return render(request, "project_reports/forms/monthly_report_progress_form.html", context)
