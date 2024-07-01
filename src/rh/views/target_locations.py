from django import forms
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect

from ..forms import ActivityPlanFormSet, DisaggregationFormSet, TargetLocationFormSet, TargetLocationForm
from ..models import ActivityDomain, FacilitySiteType, Project, TargetLocation, ActivityPlan

from .views import copy_target_location_disaggregation_locations
from django.core.paginator import Paginator


@login_required
def create_target_location(request, activity_plan):
    """Create a new target location for a specific activity plan within a project"""
    activity_plan = get_object_or_404(ActivityPlan, pk=activity_plan)

    if request.method == "POST":
        form = TargetLocationForm(request.POST)
        if form.is_valid():
            target_location = form.save(commit=False)
            target_location.activity_plan = activity_plan
            target_location.save()
            return redirect("list_target_locations", project=activity_plan.project.pk)
    else:
        form = TargetLocationForm()

    return render(
        request, "rh/target_locations/target_location_create.html", {"form": form, "activity_plan": activity_plan}
    )


@login_required
def list_target_locations(request, project):
    """List Activity Plans for a specific project"""
    project = get_object_or_404(Project, pk=project)

    target_locations = TargetLocation.objects.filter(activity_plan__project=project)

    paginator = Paginator(target_locations, 10)  # Show 10 activity plans per page
    page = request.GET.get("page", 1)
    target_locations = paginator.get_page(page)
    target_locations.adjusted_elided_pages = paginator.get_elided_page_range(page)

    context = {
        "project": project,
        "target_locations": target_locations,
    }

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
        new_location.active = True
        new_location.state = "draft"
        new_location.save()

    url = reverse("create_project_activity_plan", args=[project.pk])

    # Return the URL in a JSON response
    response_data = {"redirect_url": url}
    return JsonResponse(response_data)


@login_required
def get_target_location_empty_form(request):
    """Get an empty target location form for a project"""
    # Get the project object based on the provided project ID
    project = get_object_or_404(Project, pk=request.POST.get("project"))
    activity_domain_id = request.POST.get("activity_domain", None)
    activity_domain = None
    if activity_domain_id:
        activity_domain = get_object_or_404(ActivityDomain, pk=activity_domain_id)

    # Prepare form_kwargs to pass to ActivityPlanFormSet
    form_kwargs = {"project": project}

    # Create an instance of ActivityPlanFormSet using the project instance and form_kwargs
    activity_plan_formset = ActivityPlanFormSet(form_kwargs=form_kwargs, instance=project)

    # Get the prefix index from the request
    prefix_index = request.POST.get("prefix_index")

    # Create an instance of TargetLocationFormSet with a prefixed name
    target_location_formset = TargetLocationFormSet(
        prefix=f"target_locations_{activity_plan_formset.prefix}-{prefix_index}"
    )

    # for target_location_form in target_location_formset.forms:
    # Create a disaggregation formset for each target location form
    target_location_form = target_location_formset.empty_form

    # Check if the activity plan is selected
    if activity_domain:
        # Get clusters associated with the activity plan's domain
        clusters = activity_domain.clusters.all()

        # Get only the relevant facility types - related to cluster
        target_location_form.fields["facility_site_type"].queryset = FacilitySiteType.objects.filter(
            cluster__in=clusters
        )

        cluster_has_nhs_code = any(cluster.has_nhs_code for cluster in clusters)
        # If at least one cluster has NHS code, add the NHS code field to the form
        if cluster_has_nhs_code:
            target_location_form.fields["nhs_code"] = forms.CharField(max_length=200, required=True)
        else:
            target_location_form.fields.pop("nhs_code", None)
    else:
        target_location_form.fields["facility_site_type"].queryset = FacilitySiteType.objects.all()

    disaggregation_formset = DisaggregationFormSet(
        request.POST or None,
        instance=target_location_form.instance,
        prefix=f"disaggregation_{target_location_form.prefix}",
    )

    target_location_form.disaggregation_formset = disaggregation_formset

    # Prepare context for rendering the target location form template
    context = {
        "target_location_form": target_location_form,
        "project": project,
    }

    # Render the target location form template and generate HTML
    html = render_to_string("rh/projects/forms/target_location_empty_form.html", context)

    # Return JSON response containing the generated HTML
    return JsonResponse({"html": html})


@login_required
def delete_target_location(request, pk):
    """Delete the target location"""
    target_location = get_object_or_404(TargetLocation, pk=pk)
    if target_location:
        target_location.delete()

    url = reverse("create_project_activity_plan", args=[target_location.project.pk])

    # Return the URL in a JSON response
    response_data = {"redirect_url": url}
    return JsonResponse(response_data)
