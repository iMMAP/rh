from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

from rh.models import ActivityPlan

from ..forms import (
    ActivityPlanReportForm,
)
from ..models import (
    ActivityPlanReport,
    ProjectMonthlyReport,
)


class HTTPResponseHXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["HX-Redirect"] = self["Location"]

    status_code = 200


@login_required
def create_report_activity_plan(request, project, report):
    """Create a new activity plan for a specific project"""
    report_instance = get_object_or_404(ProjectMonthlyReport.objects.select_related("project"), pk=report)
    if request.method == "POST":
        form = ActivityPlanReportForm(request.POST, monthly_report=report_instance)
        if form.is_valid():
            report_plan = form.save(commit=False)
            report_plan.monthly_report = report_instance
            report_plan.save()
            form.save_m2m()

            messages.success(
                request,
                mark_safe(
                    f'The Activity Plan Report "<a href="{reverse("update_report_activity_plans",  args=[report_instance.project, report, report_plan])}">{report_plan}</a>" was added successfully.',
                ),
            )
            if "_save" in request.POST:
                return redirect("view_monthly_report", project=report_instance.project.pk, report=report_instance.pk)
            elif "_addanother" in request.POST:
                return redirect("create_report_activity_plan", project=project, report=report_instance.pk)
        else:
            messages.error(request, "The form is invalid. Please check the fields and try again.")
    else:
        form = ActivityPlanReportForm(monthly_report=report_instance)

    context = {
        "form": form,
        "project": report_instance.project,
        "monthly_report": report_instance,
        "report_view": False,
        "report_activities": True,
        "report_locations": False,
    }

    return render(request, "project_reports/report_activity_plans/report_activity_plan_form.html", context=context)


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
                return redirect("view_monthly_report", project=report_instance.project.pk, report=report_instance.pk)
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
    return render(request, "project_reports/report_activity_plans/report_activity_plan_form.html", context=context)


@login_required
def delete_report_activity_plan(request, plan_report):
    """Delete the target location report"""
    plan_report = get_object_or_404(ActivityPlanReport, pk=plan_report)
    monthly_report = plan_report.monthly_report
    if plan_report:
        plan_report.delete()

    # Generate the URL using reverse
    url = reverse_lazy(
        "view_monthly_report", kwargs={"project": monthly_report.project.pk, "report": monthly_report.pk}
    )
    return HTTPResponseHXRedirect(redirect_to=url)


@login_required
def hx_activity_plan_info(request):
    activity_plan = None
    try:
        activity_plan_id = request.POST.get("activity_plan", None)

        if not activity_plan_id:
            raise

        activity_plan = ActivityPlan.objects.get(pk=activity_plan_id)
    except Exception:
        activity_plan = None

    context = {"activity_plan": activity_plan}

    return render(request, "project_reports/report_activity_plans/partials/activity_plan_info.html", context)
