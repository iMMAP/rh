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


@login_required
def list_report_activity_plans(request, project, report):
    """Create View"""
    project = get_object_or_404(Project, pk=project)
    monthly_report_instance = get_object_or_404(ProjectMonthlyReport, pk=report)
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
def update_report_activity_plan(request, project, report, plan):
    """Update an existing activity plan"""
    report_instance = get_object_or_404(ProjectMonthlyReport.objects.select_related("project"), pk=report)
    report_plan = get_object_or_404(ActivityPlanReport, pk=plan)

    if request.method == "POST":
        form = ActivityPlanReportForm(request.POST, instance=report_plan)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                mark_safe(
                    f'The Report Activity Plan "<a href="{reverse("update_report_activity_plans", args=[project, report, plan])}">{report_plan}</a>" was updated successfully.'
                ),
            )
            if "_continue" in request.POST:
                return redirect(
                    "update_report_activity_plans",
                    project=report_instance.project.pk,
                    report=report_instance.pk,
                    plan=report_plan.pk,
                )
            elif "_save" in request.POST:
                return redirect(
                    "list_report_activity_plans", project=report_instance.project.pk, report=report_instance.pk
                )
        else:
            messages.error(request, "The form is invalid. Please check the fields and try again.")
    else:
        form = ActivityPlanReportForm(instance=report_plan)
    context = {
        "form": form,
        "report_activity_plan": report_plan,
        "project": report_instance.project,
        "monthly_report": report_instance,
        "report_view": False,
        "report_activities": True,
        "report_locations": False,
    }
    return render(request, "project_reports/report_activity_plans/activity_plan_form.html", context=context)
