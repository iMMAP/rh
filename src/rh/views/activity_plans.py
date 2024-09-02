from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ..forms import (
    ProjectIndicatorTypeForm,
    ActivityPlanForm,
)

from ..models import (
    ActivityPlan,
    Project,
    Indicator,
    TargetLocation,
    DisaggregationLocation,
)
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib import messages
from django.utils.safestring import mark_safe

from ..filters import ActivityPlansFilter
from django_htmx.http import HttpResponseClientRedirect


from extra_settings.models import Setting


@login_required
def update_activity_plan(request, pk):
    """Update an existing activity plan"""
    activity_plan = get_object_or_404(ActivityPlan.objects.select_related("project"), pk=pk)

    if request.method == "POST":
        form = ActivityPlanForm(request.POST, instance=activity_plan)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                mark_safe(
                    f'The Activity Plan "<a class="underline" href="{reverse("activity-plans-update", args=[activity_plan.pk])}">{activity_plan}</a>" was changed successfully.'
                ),
            )
            if "_continue" in request.POST:
                return redirect("activity-plans-update", pk=activity_plan.pk)
            elif "_save" in request.POST:
                return redirect("activity-plans-list", project=activity_plan.project.pk)
            elif "_addanother" in request.POST:
                return redirect("activity-plans-create", project=activity_plan.project.pk)
        else:
            messages.error(request, "The form is invalid. Please check the fields and try again.")
    else:
        form = ActivityPlanForm(instance=activity_plan)

    return render(
        request,
        "rh/activity_plans/activity_plan_form.html",
        {"form": form, "project": activity_plan.project},
    )


@login_required
def create_activity_plan(request, project):
    """Create a new activity plan for a specific project"""
    project = get_object_or_404(Project, pk=project)

    if request.method == "POST":
        form = ActivityPlanForm(request.POST, project=project)
        if form.is_valid():
            activity_plan = form.save(commit=False)
            activity_plan.project = project
            activity_plan.save()

            messages.success(
                request,
                mark_safe(
                    f'The Activity Plan "<a class="underline" href="{reverse("activity-plans-update", args=[activity_plan.pk])}">{activity_plan}</a>" was added successfully.',
                ),
            )
            if "_save" in request.POST:
                return redirect("activity-plans-list", project=project.pk)
            elif "_addanother" in request.POST:
                return redirect("activity-plans-create", project=project.pk)
        else:
            messages.error(request, "The form is invalid. Please check the fields and try again.")
    else:
        form = ActivityPlanForm(project=project)

    return render(request, "rh/activity_plans/activity_plan_form.html", {"form": form, "project": project})


@login_required
@require_http_methods(["DELETE"])
def delete_activity_plan(request, pk):
    """Delete the specific activity plan"""
    activity_plan = get_object_or_404(ActivityPlan, pk=pk)

    activity_plan.delete()

    messages.success(request, "Activity plan and its target locations has been delete.")

    if request.headers.get("Hx-Trigger", "") == "delete-btn":
        return HttpResponseClientRedirect(reverse("activity-plans-list", args=[activity_plan.project.id]))
    return HttpResponse(status=200)


@require_POST
@login_required
def copy_activity_plan(request, pk):
    """Copy only the activity plan not whole project"""
    new_activity_plan = get_object_or_404(ActivityPlan, pk=pk)

    target_locations = TargetLocation.objects.filter(activity_plan=new_activity_plan)

    new_activity_plan.id = None
    new_activity_plan.state = "draft"

    new_activity_plan.save()

    for location in target_locations:
        disagg_locations = DisaggregationLocation.objects.filter(
            target_location=location,
        )

        location.id = None
        location.state = "draft"
        location.activity_plan = new_activity_plan

        location.save()

        for dl in disagg_locations:
            dl.id = None
            dl.target_location = location

            dl.save()

    messages.success(request, "Activity plan and its Target Locations copied")

    return redirect("activity-plans-update", pk=new_activity_plan.id)


@login_required
def list_activity_plans(request, project):
    """List Activity Plans for a specific project
    url: projects/<pk:project>/activity-plans
    """
    project = get_object_or_404(Project, pk=project)

    ap_filter = ActivityPlansFilter(
        request.GET,
        request=request,
        queryset=ActivityPlan.objects.filter(project=project)
        .select_related("activity_domain", "activity_type", "indicator", "hrp_beneficiary")
        .annotate(target_location_count=Count("targetlocation"))
        .order_by("-id"),
        project=project,
    )

    RECORDS_PER_PAGE = Setting.get("RECORDS_PER_PAGE", default=10)

    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    paginator = Paginator(ap_filter.qs, per_page=per_page)  # Show 10 activity plans per page
    page = request.GET.get("page", 1)
    activity_plans = paginator.get_page(page)
    activity_plans.adjusted_elided_pages = paginator.get_elided_page_range(page)

    context = {"project": project, "activity_plans": activity_plans, "activity_plans_filter": ap_filter}

    return render(request, "rh/activity_plans/activity_plans_list.html", context)


@login_required
def update_indicator_type(request):
    """Indicator related types fields"""
    activity_plan_id = request.GET.get("activity_plan", "")
    indicator_id = request.GET.get("indicator")

    indicator_type_fields = [
        "package_type",
        "unit_type",
        "grant_type",
        "transfer_category",
        "currency",
        "transfer_mechanism_type",
        "implement_modility_type",
    ]

    initial_data = {}
    if activity_plan_id:
        activity_plan = get_object_or_404(ActivityPlan, pk=activity_plan_id)
        if (activity_plan.indicator) and (str(activity_plan.indicator.pk) != indicator_id):
            fields_to_update = {field: None for field in indicator_type_fields}

            # Update the fields in one query
            ActivityPlan.objects.filter(pk=activity_plan.pk).update(**fields_to_update)

        initial_data = {field: getattr(activity_plan, field, None) for field in indicator_type_fields}

    indicator = Indicator.objects.get(id=indicator_id)
    indicator_form = ProjectIndicatorTypeForm(initial=initial_data)
    context = {"indicator": indicator, "indicator_form": indicator_form}

    return render(request, "rh/projects/views/_indicator_types.html", context)
