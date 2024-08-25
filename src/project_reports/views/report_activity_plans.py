from django.contrib.auth.decorators import login_required
import uuid
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
from ..forms import (
    ActivityPlanReportForm,
    TargetLocationReportForm,
    DisaggregationLocationReportForm,
    BaseDisaggregationLocationReportFormSet,
)
from ..models import ActivityPlanReport, ProjectMonthlyReport, TargetLocationReport, DisaggregationLocationReport

from ..filters import TargetLocationReportFilter
from django.forms import inlineformset_factory


@login_required
def create_report_activity_plan(request, report):
    report_instance = get_object_or_404(ProjectMonthlyReport, pk=report)

    if request.method == "POST":
        form = ActivityPlanReportForm(request.POST, report=report_instance)
        if form.is_valid():
            report_activity_plan = form.save()
            messages.success(request, mark_safe("The Report Activity Plan created successfully!"))
            return redirect("report_activity_plan_location_reports", report_instance.pk,report_activity_plan.id)
        else:
            messages.error(request, "The form is invalid. Please check the fields and try again.")
    else:
        form = ActivityPlanReportForm(report=report_instance)

    context = {
        "form": form,
        "project": report_instance.project,
        "monthly_report": report_instance,
    }

    return render(request, "project_reports/report_activity_plans/report_activity_plan.html", context=context)


@login_required
@require_http_methods(["POST"])
def update_report_activity_plan(request, report_ap):
    report_ap = get_object_or_404(ActivityPlanReport, pk=report_ap)
    form = ActivityPlanReportForm(request.POST, instance=report_ap,report=report_ap.monthly_report)

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



def report_activity_plan_location_reports(request, report, report_ap):
    report_instance = get_object_or_404(ProjectMonthlyReport, pk=report)
    report_ap = get_object_or_404(ActivityPlanReport, pk=report_ap)

    # get the target_location_reports of report_ap and create forms for it
    form = ActivityPlanReportForm(instance=report_ap, report=report_instance)

    report_target_location_filter = TargetLocationReportFilter(
        request.GET,
        queryset=TargetLocationReport.objects.filter(activity_plan_report=report_ap).order_by("-updated_at"),
    )

    page = request.GET.get("page", 1)
    tl_reports_paginator = Paginator(report_target_location_filter.qs, 10)
    target_location_reports = tl_reports_paginator.page(page)
    target_location_reports.adjusted_elided_pages = tl_reports_paginator.get_elided_page_range(page)

    DisaggregationReportFormSet = inlineformset_factory(
        parent_model=TargetLocationReport,
        model=DisaggregationLocationReport,
        form=DisaggregationLocationReportForm,
        formset=BaseDisaggregationLocationReportFormSet,
        extra=1,
        can_delete=True,
    )

    target_location_report_forms = []
    for report in target_location_reports:
        prefix = f"disaggregation-{uuid.uuid4()}"
        target_location_report_forms.append(
            {
                "target_location_form": TargetLocationReportForm(instance=report, plan_report=report_ap),
                "dis_location_report_formset": DisaggregationReportFormSet(
                    instance=report,
                    queryset=DisaggregationLocationReport.objects.select_related(
                        "target_location_report", "disaggregation"
                    ),
                    plan_report=report_ap,
                    prefix=prefix,
                ),
                "prefix":prefix
            }
        )

    context = {
        "form": form,
        "project": report_instance.project,
        "monthly_report": report_instance,
        "target_location_report_forms": target_location_report_forms,
        "target_location_reports": target_location_reports,
        "plan_report": report_ap,
        "report_target_location_filter": report_target_location_filter,
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



# @login_required
# @require_http_methods(["POST"])
# def store_report_activity_plan(request, report):
#     report_instance = get_object_or_404(ProjectMonthlyReport, pk=report)
#     form = ActivityPlanReportForm(request.POST, report=report_instance)

#     if form.is_valid():
#         form.save()
#         messages.success(request, mark_safe("The Report Activity Plan created successfully!"))
#     else:
#         messages.error(request, "The form is invalid. Please check the fields and try again.")

#     context = {
#         "form": form,
#         "monthly_report": report_instance,
#     }

#     return render(request, "project_reports/report_activity_plans/_report_ap_form.html", context)