from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Sum
from django.urls import reverse_lazy

from django.contrib import messages
from django.utils.safestring import mark_safe
from django.forms import inlineformset_factory
from django_htmx.http import HttpResponseClientRedirect
from django.http import HttpResponse

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

    tl_filter = TargetLocationReportFilter(
        request.GET,
        request=request,
        queryset=TargetLocationReport.objects.filter(activity_plan_report__monthly_report=report)
        .select_related(
            "activity_plan_report",
        )
        .order_by("-id")
        .annotate(total_target_reached=Sum("disaggregationlocationreport__reached")),
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
        "report_target_locations": report_locations,
        "location_report_filter": tl_filter,
    }

    return render(request, "project_reports/report_target_locations/target_locations_list.html", context)


@login_required
def create_report_target_location(request, plan):
    """Create View"""
    plan_report = get_object_or_404(ActivityPlanReport, pk=plan)
    DisaggregationReportFormSet = inlineformset_factory(
        parent_model=TargetLocationReport,
        model=DisaggregationLocationReport,
        form=DisaggregationLocationReportForm,
        formset=BaseDisaggregationLocationReportFormSet,
        extra=2,
        can_delete=True,
    )

    if request.method == "POST":
        location_report_form = TargetLocationReportForm(request.POST, plan_report=plan_report)
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
                mark_safe("The Report Target Location was added successfully."),
            )
            if "_continue" in request.POST:
                return redirect(
                    "update_report_target_locations",
                    project=plan_report.monthly_report.project.pk,
                    report=plan_report.monthly_report.pk,
                    plan=plan_report.pk,
                    location=location_report.pk,
                )
            elif "_save" in request.POST:
                return redirect(
                    "list_report_target_locations",
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

        report_disaggregation_formset = DisaggregationReportFormSet(plan_report=plan_report)

    return render(
        request,
        "project_reports/report_target_locations/report_target_location_form.html",
        {
            "location_report_form": location_report_form,
            "report_disaggregation_formset": report_disaggregation_formset,
            "report_plan": plan_report,
            "monthly_report": plan_report.monthly_report,
            "project": plan_report.monthly_report.project,
        },
    )


@login_required
def update_report_target_locations(request, project, report, plan, location):
    """Update View"""
    monthly_report = get_object_or_404(ProjectMonthlyReport.objects.select_related("project"), pk=report)
    plan_report = get_object_or_404(ActivityPlanReport, pk=plan)

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
        location_report_form = TargetLocationReportForm(
            request.POST or None, instance=location_report, plan_report=plan_report
        )

        # Optimize the queryset to prefetch related target_location_report
        disaggregation_reports = DisaggregationLocationReport.objects.select_related(
            "target_location_report", "disaggregation"
        )

        # When using the formset, pass the optimized queryset
        report_disaggregation_formset = DisaggregationReportFormSet(
            request.POST, queryset=disaggregation_reports, instance=location_report, plan_report=plan_report
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
            request.POST or None, instance=location_report, plan_report=plan_report, queryset=disaggregation_reports
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
            "report_view": False,
            "report_activities": False,
            "report_locations": True,
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


@login_required
def hx_target_location_info(request):
    target_location = None
    try:
        target_location_id = request.POST.get("target_location", None)

        if not target_location_id:
            raise

        target_location = TargetLocation.objects.get(pk=target_location_id)
    except Exception:
        target_location_id = None

    context = {"target_location": target_location}

    return render(request, "project_reports/report_target_locations/partials/_target_location_info.html", context)
