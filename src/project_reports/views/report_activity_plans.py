from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.db.models import Count
from django.urls import reverse
from django.contrib import messages
from django.utils.safestring import mark_safe

from rh.models import (
    Project,
)

from ..forms import (
    ActivityPlanReportForm,
)
from ..models import (
    ActivityPlanReport,
    ProjectMonthlyReport,
)

from ..filters import PlansReportFilter



@login_required
def update_report_activity_plan(request,report,report_ap):
    report_ap = get_object_or_404(ActivityPlanReport, pk=report_ap)

    if request.method == "POST":
        form = ActivityPlanReportForm(request.POST,instance=report_ap)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                mark_safe("The Report Activity Plan created successfully!"),
            )
            if "_continue" in request.POST:
                pass
                # return redirect("view_monthly_report", project=report_ap.project.pk, report=report_instance.pk)
            elif "_save" in request.POST:
                pass
                # return redirect("view_monthly_report", project=report_instance.project.pk, report=report_instance.pk)
        else:
            messages.error(request, "The form is invalid. Please check the fields and try again.")
    else:
        form = ActivityPlanReportForm(instance=report_ap,report=report_ap.monthly_report)

    context = {
        "form": form,
        "project": report_ap.monthly_report.project,
        "monthly_report": report_ap.monthly_report,
        "report_ap":report_ap,
    }

    return render(request, "project_reports/report_activity_plans/report_activity_plan_form.html", context=context)


@login_required
def create_report_activity_plan(request, report):
    report_instance = get_object_or_404(ProjectMonthlyReport, pk=report)

    if request.method == "POST":
        form = ActivityPlanReportForm(request.POST,report=report_instance)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                mark_safe(
                    "The Report Activity Plan created successfully!"
                ),
            )
            if "_continue" in request.POST:
                return redirect(
                    "view_monthly_report", project=report_instance.project.pk, report=report_instance.pk
                )
            elif "_save" in request.POST:
                return redirect(
                    "view_monthly_report", project=report_instance.project.pk, report=report_instance.pk
                )
        else:
            messages.error(request, "The form is invalid. Please check the fields and try again.")
    else:
        form = ActivityPlanReportForm(report=report_instance)

    context = {
        "form": form,
        "project": report_instance.project,
        "monthly_report": report_instance,
    }

    return render(request, "project_reports/report_activity_plans/report_activity_plan_form.html", context=context)
