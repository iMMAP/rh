from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect

from ..forms import (
    TargetLocationForm,
    DisaggregationLocationForm,
    BaseDisaggregationLocationFormSet,
)
from ..models import Project, TargetLocation, ActivityPlan, DisaggregationLocation

from .views import copy_target_location_disaggregation_locations
from django.core.paginator import Paginator
from django.forms import inlineformset_factory
from django.contrib import messages
from django.utils.safestring import mark_safe
from ..filters import TargetLocationFilter
from django_htmx.http import HttpResponseClientRedirect
from extra_settings.models import Setting
from django.db.models import Sum


@login_required
def update_target_location(request, pk):
    target_location = get_object_or_404(TargetLocation, pk=pk)

    DisaggregationFormSet = inlineformset_factory(
        parent_model=TargetLocation,
        model=DisaggregationLocation,
        form=DisaggregationLocationForm,
        formset=BaseDisaggregationLocationFormSet,
        extra=1,
        can_delete=True,
        # max_num=2
    )

    if request.method == "POST":
        target_location_form = TargetLocationForm(request.POST, instance=target_location, user=request.user)
        disaggregation_formset = DisaggregationFormSet(
            request.POST, instance=target_location, activity_plan=target_location.activity_plan
        )

        if target_location_form.is_valid() and disaggregation_formset.is_valid():
            new_target_location = target_location_form.save(commit=False)
            new_target_location.activity_plan = target_location.activity_plan
            new_target_location.save()
            disaggregation_formset.save()

            messages.success(
                request,
                mark_safe(
                    f'The Target Location "<a href="{reverse("target-locations-update", args=[target_location.pk])}">{target_location}</a>" was changed successfully.'
                ),
            )
            if "_continue" in request.POST:
                return redirect("target-locations-update", pk=target_location.pk)
            elif "_save" in request.POST:
                return redirect("target-locations-list", project=target_location.activity_plan.project.pk)
            elif "_addanother" in request.POST:
                return redirect("target-locations-create", activity_plan=target_location.activity_plan.pk)
        else:
            messages.error(request, "The form is invalid. Please check the fields and try again.")

    else:
        target_location_form = TargetLocationForm(instance=target_location, user=request.user)
        disaggregation_formset = DisaggregationFormSet(
            instance=target_location, activity_plan=target_location.activity_plan
        )

    return render(
        request,
        "rh/target_locations/target_location_form.html",
        {
            "target_location_form": target_location_form,
            "disaggregation_formset": disaggregation_formset,
            "activity_plan": target_location.activity_plan,
            "project": target_location.activity_plan.project,
        },
    )


def create_target_location(request, activity_plan):
    activity_plan = get_object_or_404(ActivityPlan.objects.select_related("project"), pk=activity_plan)

    DisaggregationFormSet = inlineformset_factory(
        parent_model=TargetLocation,
        model=DisaggregationLocation,
        form=DisaggregationLocationForm,
        formset=BaseDisaggregationLocationFormSet,
        extra=1,
        can_delete=True,
        # max_num=2
    )

    if request.method == "POST":
        target_location_form = TargetLocationForm(request.POST, user=request.user)
        disaggregation_formset = DisaggregationFormSet(
            request.POST, instance=target_location_form.instance, activity_plan=activity_plan
        )

        if target_location_form.is_valid() and disaggregation_formset.is_valid():
            target_location = target_location_form.save(commit=False)
            target_location.activity_plan = activity_plan
            target_location.project = activity_plan.project
            target_location.save()

            disaggregation_formset.save()

            messages.success(
                request,
                mark_safe(
                    f'The Target Location "<a href="{reverse("target-locations-update", args=[target_location.pk])}">{target_location}</a>" was added successfully.'
                ),
            )
            if "_continue" in request.POST:
                return redirect("target-locations-update", pk=target_location.pk)
            elif "_save" in request.POST:
                return redirect("activity-plans-list", project=activity_plan.project.pk)
            elif "_addanother" in request.POST:
                return redirect("target-locations-create", activity_plan=activity_plan.pk)
        else:
            messages.error(request, "The form is invalid. Please check the fields and try again.")
    else:
        target_location_form = TargetLocationForm(user=request.user)
        disaggregation_formset = DisaggregationFormSet(activity_plan=activity_plan)

    return render(
        request,
        "rh/target_locations/target_location_form.html",
        {
            "target_location_form": target_location_form,
            "disaggregation_formset": disaggregation_formset,
            "activity_plan": activity_plan,
            "project": activity_plan.project,
        },
    )


@login_required
def list_target_locations(request, project):
    """List Activity Plans for a specific project"""
    project = get_object_or_404(Project, pk=project)

    tl_filter = TargetLocationFilter(
        request.GET,
        request=request,
        queryset=TargetLocation.objects.filter(activity_plan__project=project)
        .annotate(total_target=Sum("disaggregationlocation__target"))
        .select_related("activity_plan", "country", "province", "district")
        .order_by("-id"),
        project=project,
    )

    RECORDS_PER_PAGE = Setting.get("RECORDS_PER_PAGE", default=10)
    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    paginator = Paginator(tl_filter.qs, per_page=per_page)
    page = request.GET.get("page", 1)
    target_locations = paginator.get_page(page)
    target_locations.adjusted_elided_pages = paginator.get_elided_page_range(page)

    context = {"project": project, "target_locations": target_locations, "target_locations_filter": tl_filter}

    return render(request, "rh/target_locations/target_locations_list.html", context)


@login_required
def copy_target_location(request, project, location):
    project = get_object_or_404(Project, pk=project)
    target_location = get_object_or_404(TargetLocation, pk=location)
    new_location = get_object_or_404(TargetLocation, pk=target_location.pk)
    if new_location:
        new_location.pk = None
        new_location.save()

        disaggregation_locations = target_location.disaggregationlocation_set.all()

        # Iterate through disaggregation locations and copy them to the new location.
        for disaggregation_location in disaggregation_locations:
            copy_target_location_disaggregation_locations(new_location, disaggregation_location)

        new_location.project = project
        new_location.state = "draft"
        new_location.save()

    url = reverse("create_project_activity_plan", args=[project.pk])

    # Return the URL in a JSON response
    response_data = {"redirect_url": url}
    return JsonResponse(response_data)


@login_required
@require_http_methods(["DELETE"])
def delete_target_location(request, pk):
    """Delete the target location"""
    target_location = get_object_or_404(TargetLocation, pk=pk)

    target_location.delete()

    messages.success(request, "Target Location has been deleted.")

    if request.headers.get("Hx-Trigger", "") == "delete-btn":
        return HttpResponseClientRedirect(
            reverse("target-locations-list", args=[target_location.activity_plan.project.id])
        )

    return HttpResponse(status=200)
