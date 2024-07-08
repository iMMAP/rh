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

from ..filters import TargetLocationReportFilter


@login_required
def list_report_target_locations(request, project, report, plan=None):
    """Create View"""
    project = get_object_or_404(Project, pk=project)
    monthly_report_instance = get_object_or_404(ProjectMonthlyReport, pk=report)

    report_plan = None
    if plan:
        report_plan = get_object_or_404(ActivityPlanReport.objects.select_related("monthly_report"), pk=plan)
    if report_plan:
        tl_filter = TargetLocationReportFilter(
            request.GET,
            request=request,
            queryset=TargetLocationReport.objects.filter(activity_plan_report_id=report_plan.pk)
            .select_related("activity_plan_report", "country", "province", "district")
            .order_by("-id")
            .annotate(report_disaggregation_locations_count=Count("disaggregationlocationreport")),
            report=monthly_report_instance,
        )

    else:
        tl_filter = TargetLocationReportFilter(
            request.GET,
            request=request,
            queryset=TargetLocationReport.objects.filter(activity_plan_report__monthly_report=report)
            .select_related("activity_plan_report", "country", "province", "district")
            .order_by("-id")
            .annotate(report_disaggregation_locations_count=Count("disaggregationlocationreport")),
            report=monthly_report_instance,
        )

    per_page = request.GET.get("per_page", 10)
    paginator = Paginator(tl_filter.qs, per_page=per_page)
    page = request.GET.get("page", 1)
    report_locations = paginator.get_page(page)
    report_locations.adjusted_elided_pages = paginator.get_elided_page_range(page)

    context = {
        "project": project,
        "monthly_report": monthly_report_instance,
        "report_plan": report_plan,
        "report_target_locations": report_locations,
        "location_report_filter": tl_filter,
        "report_view": False,
        "report_activities": False,
        "report_locations": True,
    }

    return render(request, "project_reports/report_target_locations/target_locations_list.html", context)


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
