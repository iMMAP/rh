from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from ..forms import (
    ProjectIndicatorTypeForm,
    ActivityPlanForm,
)

from ..models import (
    ActivityPlan,
    Project,
    Indicator,
)
from .views import copy_project_target_location, copy_target_location_disaggregation_locations
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib import messages
from django.utils.safestring import mark_safe


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
                    f'The Activity Plan "<a href="{reverse("activity-plans-update", args=[activity_plan.pk])}">{activity_plan}</a>" was changed successfully.'
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
                    f'The Activity Plan "<a href="{reverse("activity-plans-update", args=[activity_plan.pk])}">{activity_plan}</a>" was added successfully.',
                ),
            )
            if "_continue" in request.POST:
                return redirect("activity-plans-update", pk=activity_plan.pk)
            elif "_save" in request.POST:
                return redirect("activity-plans-list", project=project.pk)
            elif "_addanother" in request.POST:
                return redirect("activity-plans-create", project=project.pk)
        else:
            messages.error(request, "The form is invalid. Please check the fields and try again.")
    else:
        form = ActivityPlanForm(project=project)

    return render(request, "rh/activity_plans/activity_plan_form.html", {"form": form, "project": project})


@login_required
def delete_activity_plan(request, pk):
    """Delete the specific activity plan"""
    activity_plan = get_object_or_404(ActivityPlan, pk=pk)
    if activity_plan:
        activity_plan.delete()

    url = reverse("create_project_activity_plan", args=[activity_plan.project.pk])

    # Return the URL in a JSON response
    response_data = {"redirect_url": url}
    return JsonResponse(response_data)


@login_required
def copy_activity_plan(request, project, plan):
    """Copy only the activity plan not whole project"""
    project = get_object_or_404(Project, pk=project)
    activity_plan = get_object_or_404(ActivityPlan, pk=plan)
    new_plan = get_object_or_404(ActivityPlan, pk=activity_plan.pk)

    if new_plan:
        new_plan.pk = None
        new_plan.save()

        # Iterate through target locations and copy them to the new plan.
        target_locations = activity_plan.targetlocation_set.all()
        for location in target_locations:
            new_location = copy_project_target_location(new_plan, location)
            disaggregation_locations = location.disaggregationlocation_set.all()

            # Iterate through disaggregation locations and copy them to the new location.
            for disaggregation_location in disaggregation_locations:
                copy_target_location_disaggregation_locations(new_location, disaggregation_location)

        new_plan.project = project
        new_plan.active = True
        new_plan.state = "draft"
        new_plan.indicator = activity_plan.indicator
        new_plan.save()

    url = reverse("create_project_activity_plan", args=[project.pk])

    # Return the URL in a JSON response
    response_data = {"redirect_url": url}
    return JsonResponse(response_data)


@login_required
def list_activity_plans(request, project):
    """List Activity Plans for a specific project"""
    project = get_object_or_404(Project, pk=project)

    activity_plans = ActivityPlan.objects.filter(project=project).annotate(
        target_location_count=Count("targetlocation")
    )

    paginator = Paginator(activity_plans, 10)  # Show 10 activity plans per page
    page = request.GET.get("page", 1)
    activity_plans = paginator.get_page(page)
    activity_plans.adjusted_elided_pages = paginator.get_elided_page_range(page)

    context = {
        "project": project,
        "activity_plans": activity_plans,
    }

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

    return render(request,"rh/projects/views/_indicator_types.html", context)

