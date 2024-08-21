from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.db.models import Count
from django.urls import reverse
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django_htmx.http import HttpResponseClientRedirect
from rh.models import (
    Project,
)
from django.views.decorators.http import require_http_methods
from ..forms import ActivityPlanReportForm, TargetLocationReportForm
from ..models import ActivityPlanReport, ProjectMonthlyReport, TargetLocationReport

from ..filters import PlansReportFilter


@login_required
@require_http_methods(["POST"])
def create_report_activity_plan(request, report):
    report_instance = get_object_or_404(ProjectMonthlyReport, pk=report)
    form = ActivityPlanReportForm(request.POST, report=report_instance)

    if form.is_valid():
        form.save()
        messages.success(request, mark_safe("The Report Activity Plan created successfully!"))
    else:
        messages.error(request, "The form is invalid. Please check the fields and try again.")

    context = {
        "form": form,
        "monthly_report": report_instance,
    }

    return render(request, "project_reports/report_activity_plans/_report_ap_form.html", context)


@login_required
@require_http_methods(["POST"])
def update_report_activity_plan(request, report, report_ap):
    report_ap = get_object_or_404(ActivityPlanReport, pk=report_ap)
    form = ActivityPlanReportForm(request.POST, instance=report_ap)

    if form.is_valid():
        form.save()
        messages.success(
            request,
            mark_safe("The Report Activity Plan updated successfully!"),
        )
    else:
        messages.error(request, "The form is invalid. Please check the fields and try again.")

    context = {"form": form}

    return render(request, "project_reports/report_activity_plans/_report_ap_form.html", context)


@login_required
def report_activity_plans(request, report):
    report_instance = get_object_or_404(ProjectMonthlyReport, pk=report)
    form = ActivityPlanReportForm(report=report_instance)

    context = {
        "form": form,
        "project": report_instance.project,
        "monthly_report": report_instance,
    }

    return render(request, "project_reports/report_activity_plans/report_activity_plan.html", context=context)


def update_report_activity_plans(request, report, report_ap):
    report_instance = get_object_or_404(ProjectMonthlyReport, pk=report)
    report_ap = get_object_or_404(ActivityPlanReport, pk=report_ap)

    # get the target_location_reports of report_ap and create forms for it
    form = ActivityPlanReportForm(instance=report_ap, report=report_instance)

    target_location_reports = Paginator(TargetLocationReport.objects.filter(activity_plan_report=report_ap), 4).page(
        request.GET.get("page", 1)
    )
    target_location_report_forms = [
        TargetLocationReportForm(instance=report, plan_report=report_ap) for report in target_location_reports
    ]

    context = {
        "form": form,
        "project": report_instance.project,
        "monthly_report": report_instance,
        "target_location_report_forms": target_location_report_forms,
        "plan_report": report_ap,
    }

    return render(request, "project_reports/report_activity_plans/update_report_activity_plan.html", context=context)


@login_required
@require_http_methods(["DELETE"])
def delete_report_activity_plan(request, ap_report):
    activity_plan_report = get_object_or_404(ActivityPlanReport, pk=ap_report)

    activity_plan_report.delete()

    messages.success(request, "Activity Report and its targeted locations has been delete.")

    if request.headers.get("Hx-Trigger", "") == "delete-btn":
        return HttpResponseClientRedirect(
            reverse(
                "view_monthly_report",
                args=[activity_plan_report.monthly_report.project.id, activity_plan_report.monthly_report.id],
            )
        )

    return HttpResponse(status=200)
