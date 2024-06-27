from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from ..forms import ActivityPlanFormSet, DisaggregationFormSet, TargetLocationFormSet, ProjectIndicatorTypeForm

from ..models import (
    ActivityPlan,
    Project,
    Indicator,
)
from .views import copy_project_target_location, copy_target_location_disaggregation_locations


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
def create_project_activity_plan(request, project):
    project = get_object_or_404(Project, pk=project)

    # Get all existing activity plans for the project
    # Create the activity plan formset with initial data from the project
    activity_plan_formset = ActivityPlanFormSet(
        request.POST or None, instance=project, form_kwargs={"project": project}
    )

    target_location_formsets = []

    # Iterate over activity plan forms in the formset
    for activity_plan_form in activity_plan_formset.forms:
        # Create a target location formset for each activity plan form
        target_location_formset = TargetLocationFormSet(
            request.POST or None,
            instance=activity_plan_form.instance,
            prefix=f"target_locations_{activity_plan_form.prefix}",
        )
        for target_location_form in target_location_formset.forms:
            # Create a disaggregation formset for each target location form
            # HERE

            initial_data = []

            disaggregation_formset = DisaggregationFormSet(
                request.POST or None,
                instance=target_location_form.instance,
                prefix=f"disaggregation_{target_location_form.prefix}",
                initial=initial_data,
            )
            target_location_form.disaggregation_formset = disaggregation_formset

        target_location_formsets.append(target_location_formset)

    if request.method == "POST":
        # Check if the form was submitted for "Next Step" or "Save & Continue"
        submit_type = request.POST.get("submit_type")

        acitivities_target = {}
        if activity_plan_formset.is_valid():
            # Save valid activity plan forms
            for activity_plan_form in activity_plan_formset:
                if activity_plan_form.cleaned_data.get("activity_domain") and activity_plan_form.cleaned_data.get(
                    "activity_type"
                ):
                    activity_plan = activity_plan_form.save()
                    acitivities_target.update({activity_plan.pk: 0})

            for post_target_location_formset in target_location_formsets:
                if post_target_location_formset.is_valid():
                    for post_target_location_form in post_target_location_formset:
                        if post_target_location_form.cleaned_data != {}:
                            if post_target_location_form.cleaned_data.get(
                                "province"
                            ) and post_target_location_form.cleaned_data.get("district"):
                                target_location_instance = post_target_location_form.save()
                                target_location_instance.project = project
                                target_location_instance.country = request.user.profile.country
                                target_location_instance.save()

                        if hasattr(post_target_location_form, "disaggregation_formset"):
                            post_disaggregation_formset = post_target_location_form.disaggregation_formset.forms

                            # Delete the exisiting instances of the disaggregation location and create new
                            # based on the indicator disaggregations
                            #
                            new_disaggregations = []
                            for disaggregation_form in post_disaggregation_formset:
                                if disaggregation_form.is_valid():
                                    if (
                                        disaggregation_form.cleaned_data != {}
                                        and disaggregation_form.cleaned_data.get("target") > 0
                                    ):
                                        disaggregation_instance = disaggregation_form.save(commit=False)
                                        disaggregation_instance.target_location = target_location_instance
                                        disaggregation_instance.save()
                                        acitivities_target[
                                            target_location_instance.activity_plan_id
                                        ] += disaggregation_instance.target
                                        new_disaggregations.append(disaggregation_instance.id)

                            all_disaggregations = post_target_location_form.instance.disaggregationlocation_set.all()
                            for dis in all_disaggregations:
                                if dis.id not in new_disaggregations:
                                    dis.delete()

            for activity_plan_form in activity_plan_formset:
                activity_plan = activity_plan_form.save()
                activity_plan.total_target = acitivities_target[activity_plan.pk]

            activity_plan_formset.save()

            if submit_type == "next_step":
                # Redirect to the project review page if "Next Step" is clicked
                return redirect("project_plan_review", project=project.pk)
            else:
                # Redirect back to this view if "Save & Continue" is clicked
                return redirect("create_project_activity_plan", project=project.pk)
        else:
            # TODO:
            # Handle invalid activity_plan_formset
            # Add error handling code here
            pass

    # Prepare data for rendering the template
    target_location_formset = TargetLocationFormSet(
        request.POST or None,
    )

    cluster_ids = list(project.clusters.values_list("id", flat=True))

    combined_formset = zip(activity_plan_formset.forms, target_location_formsets)

    context = {
        "project": project,
        "activity_plan_formset": activity_plan_formset,
        "target_location_formset": target_location_formset,
        "combined_formset": combined_formset,
        "clusters": cluster_ids,
        "activity_planning": True,
        "project_view": True,
        "financial_view": False,
        "reports_view": False,
    }
    # Render the template with the context data
    return render(request, "rh/projects/forms/project_activity_plan_form.html", context)


@login_required
def get_activity_empty_form(request):
    """Get an empty activity form"""
    # Get the project object based on the provided project ID
    project = get_object_or_404(Project, pk=request.POST.get("project"))

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

    # Prepare context for rendering the activity empty form template
    context = {
        "form": activity_plan_formset.empty_form,
        "target_location_formset": target_location_formset,
        "project": project,
    }

    # Render the activity empty form template and generate HTML
    html = render_to_string("rh/projects/forms/activity_empty_form.html", context)

    # Return JSON response containing the generated HTML
    return JsonResponse({"html": html})


@login_required
def update_indicator_type(request):
    """Indicator related types fields"""
    if request.method == "POST":
        activity_plan_id = request.POST.get("activity_plan", "")
        indicator_id = request.POST.get("id")
        prefix = request.POST.get("prefix")
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
        indicator_form = ProjectIndicatorTypeForm(prefix=prefix, initial=initial_data)
        context = {"indicator": indicator, "indicator_form": indicator_form}

        html = render_to_string("rh/projects/views/_indicator_types.html", context)

        # Return JSON response containing the generated HTML
        return JsonResponse({"html": html})
