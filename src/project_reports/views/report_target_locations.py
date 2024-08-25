from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Count
from django.urls import reverse_lazy

from django.contrib import messages
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from django.forms import inlineformset_factory

from rh.models import (
    Project,
    TargetLocation,
)

from ..forms import (
    TargetLocationReportForm,
    DisaggregationLocationReportForm,
    BaseDisaggregationLocationReportFormSet,
)

from ..models import (
    ActivityPlanReport,
    ProjectMonthlyReport,
    TargetLocationReport,
    DisaggregationLocationReport,
)

from ..filters import TargetLocationReportFilter
from django_htmx.http import HttpResponseClientRedirect
from django.http import  HttpResponse
from django.views.decorators.http import require_http_methods

import uuid

@login_required
def create_report_target_location(request, plan):
    plan_report = get_object_or_404(ActivityPlanReport, pk=plan)
    DisaggregationReportFormSet = inlineformset_factory(
        parent_model=TargetLocationReport,
        model=DisaggregationLocationReport,
        form=DisaggregationLocationReportForm,
        formset=BaseDisaggregationLocationReportFormSet,
        extra=2,
        can_delete=True,
    )

    prefix = request.POST.get("prefix", f"disaggregation-{uuid.uuid4()}")

    if request.method == "POST":
        location_report_form = TargetLocationReportForm(request.POST,plan_report=plan_report)
        report_disaggregation_formset = DisaggregationReportFormSet(
            request.POST,instance=location_report_form.instance ,plan_report=plan_report,prefix=prefix
        )

        if location_report_form.is_valid() and report_disaggregation_formset.is_valid():
            location_report = location_report_form.save(commit=False)
            location_report.activity_plan_report = plan_report
            location_report.save()

            report_disaggregation_formset.instance = location_report
            report_disaggregation_formset.save()

            messages.success(request,'The Report Target Location added successfully.')
        else:
            messages.error(request,"Validation error! Please check the forms bellow")
    else:
        location_report_form = TargetLocationReportForm(plan_report=plan_report)
        report_disaggregation_formset = DisaggregationReportFormSet(plan_report=plan_report, prefix=prefix)
    
    context = {
        "location_report_form": location_report_form,
        "report_disaggregation_formset": report_disaggregation_formset,
        "plan_report": plan_report,
        "prefix":prefix
    }

    return render(request, "project_reports/report_target_locations/_report_target_location_form.html",context)

@login_required
def update_report_target_location(request, location):
    location_report = get_object_or_404(TargetLocationReport, pk=location)

    DisaggregationReportFormSet = inlineformset_factory(
        parent_model=TargetLocationReport,
        model=DisaggregationLocationReport,
        form=DisaggregationLocationReportForm,
        formset=BaseDisaggregationLocationReportFormSet,
        extra=2,
        can_delete=True,
    )

    location_report_form = TargetLocationReportForm(request.POST or None, instance=location_report,plan_report=location_report.activity_plan_report)

    # Optimize the queryset to prefetch related target_location_report
    disaggregation_reports = DisaggregationLocationReport.objects.select_related(
        "target_location_report", "disaggregation"
    )

    prefix = request.POST.get("prefix", f"disaggregation-{uuid.uuid4()}")

    # When using the formset, pass the optimized queryset
    report_disaggregation_formset = DisaggregationReportFormSet(
        request.POST,
        queryset=disaggregation_reports,
        instance=location_report,
        plan_report=location_report.activity_plan_report,
        prefix=prefix
    )

    if location_report_form.is_valid() and report_disaggregation_formset.is_valid():
        updated_location_report = location_report_form.save(commit=False)
        updated_location_report.activity_plan_report=location_report.activity_plan_report
        updated_location_report.save()

        report_disaggregation_formset.save()

        messages.success(request,"Location Report updated successfully!")
    else:
        messages.error(request, "The form is invalid. Please check the fields and try again.")
    
    context = {
        "location_report_form": location_report_form,
        "report_disaggregation_formset": report_disaggregation_formset,
        "plan_report": location_report.activity_plan_report,
        "prefix":prefix
    }

    return render(request, "project_reports/report_target_locations/_report_target_location_form.html",context)



@login_required
@require_http_methods(["DELETE"])
def delete_location_report_view(request, pk):
    report_target_location = get_object_or_404(TargetLocationReport, pk=pk)

    report_target_location.delete()

    messages.success(request, "Target Location Report has been deleted.")

    return HttpResponse(status=200)

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
