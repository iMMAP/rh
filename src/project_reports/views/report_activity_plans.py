from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.db.models import Count
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

from rh.models import Project, ActivityPlan

from ..forms import (
    ActivityPlanReportForm,
)
from ..models import (
    ActivityPlanReport,
    ProjectMonthlyReport,
)

from ..filters import PlansReportFilter


class HTTPResponseHXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["HX-Redirect"] = self["Location"]

    status_code = 200


@login_required
def list_report_activity_plans(request, project, report):
    """Create View"""
    project = get_object_or_404(Project, pk=project)
    monthly_report_instance = get_object_or_404(ProjectMonthlyReport, pk=report)

    ap_filter = PlansReportFilter(
        request.GET,
        request=request,
        queryset=ActivityPlanReport.objects.filter(monthly_report=monthly_report_instance)
        .select_related(
            "monthly_report",
            "activity_plan",
        )
        .order_by("-id")
        .annotate(report_target_location_count=Count("targetlocationreport"))
        .order_by("-id"),
        report=monthly_report_instance,
    )

    per_page = request.GET.get("per_page", 10)
    paginator = Paginator(ap_filter.qs, per_page=per_page)  # Show 10 activity plans per page
    page = request.GET.get("page", 1)
    report_plans = paginator.get_page(page)
    report_plans.adjusted_elided_pages = paginator.get_elided_page_range(page)

    context = {
        "project": project,
        "monthly_report": monthly_report_instance,
        "report_plans": report_plans,
        "plans_report_filter": ap_filter,
        "report_view": False,
        "report_activities": True,
        "report_locations": False,
    }
    return render(request, "project_reports/report_activity_plans/activity_plans_list.html", context)


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
                return redirect(
                    "list_report_activity_plans", project=report_instance.project.pk, report=report_instance.pk
                )
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

    return render(request, "project_reports/report_activity_plans/activity_plan_form.html", context=context)


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


@login_required
def delete_report_activity_plan(request, plan_report):
    """Delete the target location report"""
    plan_report = get_object_or_404(ActivityPlanReport, pk=plan_report)
    monthly_report = plan_report.monthly_report
    if plan_report:
        plan_report.delete()

    # Generate the URL using reverse
    url = reverse_lazy(
        "list_report_activity_plans", kwargs={"project": monthly_report.project.pk, "report": monthly_report.pk}
    )
    return HTTPResponseHXRedirect(redirect_to=url)


@login_required
def get_activity_details_fields_data(request):
    try:
        activity_plan_id = request.POST.get("activity_plan", False)
        activity_plan = None
        if activity_plan_id:
            activity_plan = ActivityPlan.objects.get(pk=activity_plan_id)

        data = {
            "activity_domain": activity_plan.activity_domain.name
            if activity_plan and activity_plan.activity_domain
            else None,
            "activity_type": activity_plan.activity_type.name
            if activity_plan and activity_plan.activity_type
            else None,
            "activity_detail": activity_plan.activity_detail.name
            if activity_plan and activity_plan.activity_detail
            else None,
            "indicator_id": activity_plan.indicator.pk if activity_plan and activity_plan.indicator else None,
            "indicator_name": activity_plan.indicator.name if activity_plan and activity_plan.indicator else None,
        }
        return JsonResponse(data)
    except ActivityPlan.DoesNotExist:
        return JsonResponse({"error": "Activity Plan not found"}, status=404)
