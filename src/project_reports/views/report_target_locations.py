import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Q, Sum
from django.forms import inlineformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django_htmx.http import HttpResponseClientRedirect

from rh.models import (
    Disaggregation,
    DisaggregationLocation,
    Project,
    TargetLocation,
)

from ..filters import TargetLocationReportFilter
from ..forms import (
    BaseDisaggregationLocationReportFormSet,
    DisaggregationLocationReportForm,
    TargetLocationReportForm,
)
from ..models import (
    ActivityPlanReport,
    DisaggregationLocationReport,
    ProjectMonthlyReport,
    TargetLocationReport,
)


@login_required
def get_target_and_reached_of_disaggregationlocation(request):
    data = json.loads(request.body)

    target_location_id = data.get("target_location_id")
    disaggregation_id = data.get("disaggregation_id")

    if not target_location_id or not disaggregation_id:
        return JsonResponse({"error": "Both target_location_id and disaggregation_id are required."}, status=400)

    try:
        target_location_id = int(target_location_id)
        disaggregation_id = int(disaggregation_id)
    except ValueError:
        return JsonResponse({"error": "Both target_location_id and disaggregation_id must be integers."}, status=400)

    dis_loc = DisaggregationLocation.objects.filter(
        disaggregation_id=disaggregation_id, target_location_id=target_location_id
    ).first()

    total_reached = (
        DisaggregationLocationReport.objects.filter(
            target_location_report__target_location_id=target_location_id,
            disaggregation_id=disaggregation_id,
        )
        .filter(
            target_location_report__beneficiary_status="new_beneficiary",
        )
        .aggregate(total_reached=Sum("reached"))["total_reached"]
    )

    return JsonResponse({"target": dis_loc.target, "reached": total_reached})


@login_required
def list_report_target_locations(request, project, report, plan=None):
    project = get_object_or_404(Project, pk=project)
    monthly_report_instance = get_object_or_404(ProjectMonthlyReport, pk=report)

    tl_filter = TargetLocationReportFilter(
        request.GET,
        request=request,
        queryset=TargetLocationReport.objects.filter(activity_plan_report__monthly_report=report)
        .select_related(
            "activity_plan_report",
            "activity_plan_report__activity_plan",
            "target_location",
        )
        .order_by("-updated_at")
        .annotate(
            total_target_reached=Sum(
                "disaggregationlocationreport__reached",
                filter=Q(
                    disaggregationlocationreport__target_location_report__target_location_id=F("target_location_id")
                ),
            )
        ),
        report=monthly_report_instance,
    )

    # Get the target location total_target here

    per_page = request.GET.get("per_page", 10)
    paginator = Paginator(tl_filter.qs, per_page=per_page)
    page = request.GET.get("page", 1)
    report_locations = paginator.get_page(page)
    report_locations.adjusted_elided_pages = paginator.get_elided_page_range(page)

    context = {
        "project": project,
        "monthly_report": monthly_report_instance,
        "report_target_locations": report_locations,
        "location_report_filter": tl_filter,
    }

    return render(request, "project_reports/report_target_locations/report_target_locations_list.html", context)


@login_required
def hx_diaggregation_tabular_form(request):
    target_location = None
    report_disaggregation_formset = None

    try:
        target_location_id = request.POST.get("target_location", None)
        target_location = get_object_or_404(TargetLocation, pk=target_location_id)

        related_disaggregations = target_location.disaggregations.all()

        DisaggregationReportFormSet = inlineformset_factory(
            parent_model=TargetLocationReport,
            model=DisaggregationLocationReport,
            form=DisaggregationLocationReportForm,
            formset=BaseDisaggregationLocationReportFormSet,
            extra=len(related_disaggregations),
            can_delete=False,
        )

        report_disaggregation_formset = DisaggregationReportFormSet(
            target_location=target_location,
            initial=[{"disaggregation": disaggregation} for disaggregation in related_disaggregations],
        )
    except Exception:
        pass

    context = {"target_location": target_location, "report_disaggregation_formset": report_disaggregation_formset}

    return render(
        request, "project_reports/report_target_locations/partials/_disaggregation_tabular_form.html", context
    )


@login_required
def create_report_target_location(request, plan):
    """Report for a location of an ActivityPlanReport"""
    plan_report = get_object_or_404(
        ActivityPlanReport.objects.select_related("monthly_report", "activity_plan"), pk=plan
    )

    if request.method == "POST":
        related_disaggregations = Disaggregation.objects.filter(indicators=plan_report.activity_plan.indicator)
        location_report_form = TargetLocationReportForm(request.POST, plan_report=plan_report)

        DisaggregationReportFormSet = inlineformset_factory(
            parent_model=TargetLocationReport,
            model=DisaggregationLocationReport,
            form=DisaggregationLocationReportForm,
            formset=BaseDisaggregationLocationReportFormSet,
            extra=len(related_disaggregations),
            can_delete=False,
        )
        report_disaggregation_formset = DisaggregationReportFormSet(
            request.POST, instance=location_report_form.instance
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
                    f'The Report Target Location "<a class="underline" href="{reverse("update_report_target_locations", args=[plan_report.monthly_report.project_id, plan_report.pk, location_report.pk])}">{location_report}</a>" was updated successfully.'
                ),
            )

            if "_continue" in request.POST:
                return redirect(
                    "update_report_target_locations",
                    project=plan_report.monthly_report.project.pk,
                    plan=plan_report.pk,
                    location=location_report.pk,
                )
            elif "_save" in request.POST:
                return redirect(
                    "view_monthly_report",
                    project=plan_report.monthly_report.project.pk,
                    report=plan_report.monthly_report.pk,
                )
            elif "_addanother" in request.POST:
                return redirect(
                    "create_report_target_location",
                    plan=plan_report.pk,
                )
        else:
            messages.error(request, "The form is invalid. Please check the fields and try again.")
    else:
        location_report_form = TargetLocationReportForm(
            request.POST or None,
            plan_report=plan_report,
        )

    context = {
        "location_report_form": location_report_form,
        "report_plan": plan_report,
        "monthly_report": plan_report.monthly_report,
        "project": plan_report.monthly_report.project,
    }

    return render(request, "project_reports/report_target_locations/report_target_location_form.html", context)


@login_required
def update_report_target_locations(request, project, plan, location):
    """Update View"""
    plan_report = get_object_or_404(ActivityPlanReport.objects.select_related("monthly_report"), pk=plan)
    monthly_report = plan_report.monthly_report

    # Get the existing location report to be updated
    location_report = get_object_or_404(TargetLocationReport.objects.select_related("target_location"), pk=location)

    DisaggregationReportFormSet = inlineformset_factory(
        parent_model=TargetLocationReport,
        model=DisaggregationLocationReport,
        form=DisaggregationLocationReportForm,
        formset=BaseDisaggregationLocationReportFormSet,
        extra=1,
        can_delete=True,
    )
    if request.method == "POST":
        location_report_form = TargetLocationReportForm(
            request.POST or None, instance=location_report, plan_report=plan_report
        )

        # Optimize the queryset to prefetch related target_location_report
        disaggregation_reports = DisaggregationLocationReport.objects.select_related(
            "target_location_report", "disaggregation"
        )

        # When using the formset, pass the optimized queryset
        report_disaggregation_formset = DisaggregationReportFormSet(
            request.POST,
            queryset=disaggregation_reports,
            instance=location_report,
            target_location=location_report.target_location,
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
                    f'The Report Target Location "<a class="underline" href="{reverse("update_report_target_locations", args=[project, plan, location])}">{location_report}</a>" was updated successfully.'
                ),
            )
            if "_continue" in request.POST:
                return redirect(
                    "update_report_target_locations",
                    project=monthly_report.project.pk,
                    plan=plan_report.pk,
                    location=location_report.pk,
                )
            elif "_save" in request.POST:
                return redirect(
                    "list_report_target_locations", project=monthly_report.project.pk, report=monthly_report.pk
                )
            elif "_addanother" in request.POST:
                return redirect(
                    "create_report_target_location",
                    plan=plan_report.pk,
                )
        else:
            messages.error(request, "The form is invalid. Please check the fields and try again.")
    else:
        location_report_form = TargetLocationReportForm(
            request.POST or None, instance=location_report, plan_report=plan_report
        )
        # Optimize the queryset to prefetch related target_location_report
        disaggregation_reports = DisaggregationLocationReport.objects.select_related(
            "target_location_report", "disaggregation"
        )

        # When using the formset, pass the optimized queryset
        report_disaggregation_formset = DisaggregationReportFormSet(
            instance=location_report, target_location=location_report.target_location, queryset=disaggregation_reports
        )

    return render(
        request,
        "project_reports/report_target_locations/report_target_location_form.html",
        {
            "location_report": location_report,
            "location_report_form": location_report_form,
            "report_disaggregation_formset": report_disaggregation_formset,
            "report_plan": plan_report,
            "monthly_report": monthly_report,
            "project": monthly_report.project,
        },
    )


@login_required
def delete_location_report_view(request, location_report):
    location_report = get_object_or_404(TargetLocationReport, pk=location_report)
    monthly_report = location_report.activity_plan_report.monthly_report

    location_report.delete()

    messages.success(request, "Target Location Report has been delete.")

    if request.headers.get("Hx-Trigger", "") == "delete-btn":
        url = reverse_lazy(
            "list_report_target_locations", kwargs={"project": monthly_report.project.pk, "report": monthly_report.pk}
        )
        return HttpResponseClientRedirect(url)

    return HttpResponse(status=200)
