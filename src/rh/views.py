import os

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.forms import modelformset_factory
from django.http import FileResponse, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.cache import cache_control
from project_reports.models import ProjectMonthlyReport as Report

from rh.resources import ProjectResource

from .filters import ProjectsFilter
from .forms import (
    ActivityPlanFormSet,
    BudgetProgressForm,
    DisaggregationFormSet,
    OrganizationRegisterForm,
    ProjectForm,
    ProjectIndicatorTypeForm,
    TargetLocationFormSet,
)
from .models import (
    ActivityDomain,
    ActivityPlan,
    BudgetProgress,
    Cluster,
    DisaggregationLocation,
    FacilitySiteType,
    Indicator,
    Location,
    Project,
    TargetLocation,
)

RECORDS_PER_PAGE = 10


#############################################
#                Index Views
#############################################


@cache_control(no_store=True)
def landing_page(request):
    template = loader.get_template("landing.html")

    users_count = User.objects.all().count()
    locations_count = Location.objects.all().count()
    reports_count = Report.objects.all().count()
    context = {
        "users": users_count,
        "locations": locations_count,
        "reports": reports_count,
    }
    return HttpResponse(template.render(context, request))


#############################################
#               Project Views
#############################################


@cache_control(no_store=True)
@login_required
def load_activity_domains(request):
    cluster_ids = [int(i) for i in request.POST.getlist("clusters[]") if i]

    # Define a Prefetch object to optimize the related activitydomain_set
    prefetch_activitydomain = Prefetch(
        "activitydomain_set",
        queryset=ActivityDomain.objects.order_by("name"),
    )

    clusters = Cluster.objects.filter(pk__in=cluster_ids).prefetch_related(prefetch_activitydomain)

    clusters = [
        {
            "label": cluster.title,
            "choices": [{"value": domain.pk, "label": domain.name} for domain in cluster.activitydomain_set.all()],
        }
        for cluster in clusters
    ]

    return JsonResponse(clusters, safe=False)


@cache_control(no_store=True)
@login_required
def load_locations_details(request):
    parent_ids = [int(i) for i in request.POST.getlist("parents[]") if i]
    parents = Location.objects.filter(pk__in=parent_ids).select_related("parent")

    response = "".join(
        [
            f'<optgroup label="{parent.name}">'
            + "".join(
                [f'<option value="{location.pk}">{location}</option>' for location in parent.children.order_by("name")]
            )
            + "</optgroup>"
            if parent.children.exists()
            else ""
            for parent in parents
        ]
    )

    return JsonResponse(response, safe=False)


@cache_control(no_store=True)
@login_required
def load_facility_sites(request):
    # FIXME: Fix the long url, by post request?
    cluster_ids = [int(i) for i in request.GET.getlist("clusters[]") if i]
    clusters = Cluster.objects.filter(pk__in=cluster_ids)

    response = "".join(
        [
            f'<optgroup label="{cluster.title}">'
            + "".join(
                [
                    f'<option value="{facility.pk}">{facility}</option>'
                    for facility in cluster.facilitysitetype_set.order_by("name")
                ]
            )
            + "</optgroup>"
            for cluster in clusters
        ]
    )

    return JsonResponse(response, safe=False)


@cache_control(no_store=True)
@login_required
def projects_list(request):
    """Projects"""
    # Setup Filter
    project_filter = ProjectsFilter(
        request.GET,
        queryset=Project.objects.all()
        .prefetch_related("clusters", "programme_partners", "implementing_partners")
        .order_by("-id"),
    )

    # Setup Pagination
    p = Paginator(project_filter.qs, RECORDS_PER_PAGE)
    page = request.GET.get("page")
    p_projects = p.get_page(page)
    total_pages = "a" * p_projects.paginator.num_pages

    context = {
        "projects_count": Project.objects.all().count,
        "projects": p_projects,
        "draft_projects_count": Project.objects.filter(state="draft").count(),
        "active_projects_count": Project.objects.filter(state="in-progress").count(),
        "completed_projects_count": Project.objects.filter(state="done").count(),
        "archived_projects_count": Project.objects.filter(state="archive").count(),
        "project_filter": project_filter,
        "total_pages": total_pages,
    }
    return render(request, "rh/projects/views/projects_list.html", context)


@cache_control(no_store=True)
@login_required
def projects_detail(request, pk):
    """View for viewing a project.
    url: projects/<str:pk>/
    """
    project = get_object_or_404(
        Project.objects.prefetch_related(
            "clusters",
            "donors",
            "programme_partners",
            "implementing_partners",
            Prefetch(
                "activityplan_set",
                ActivityPlan.objects.select_related("activity_domain", "beneficiary", "indicator").prefetch_related(
                    "targetlocation_set", "activity_type", "activity_detail"
                ),
            ),
        ),
        pk=pk,
    )
    activity_plans = project.activityplan_set.all()

    context = {
        "project": project,
        "project_view": True,
        "financial_view": False,
        "reports_view": False,
        "project_filter": project,
        "activity_plans": activity_plans,
    }
    return render(request, "rh/projects/views/project_view.html", context)


@cache_control(no_store=True)
@login_required
def create_project_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            return redirect("create_project_activity_plan", project=project.pk)

        # Form is not valid
        messages.error(request, "Something went wrong. Please fix the errors below.")
    else:
        # Use user's country and clusters as default values if available
        if request.user.is_authenticated and request.user.profile and request.user.profile.country:
            country = request.user.profile.country
            # clusters = request.user.profile.clusters.all()
            form = ProjectForm(initial={"user": request.user, "country": country})
        else:
            form = ProjectForm()

    context = {
        "form": form,
        "project_planning": True,
        "project_view": True,
        "financial_view": False,
        "reports_view": False,
    }
    return render(request, "rh/projects/forms/project_form.html", context)


@cache_control(no_store=True)
@login_required
def update_project_view(request, pk):
    """View for updating a project."""

    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            return redirect("create_project_activity_plan", project=project.pk)
    else:
        form = ProjectForm(instance=project)

    context = {
        "form": form,
        "project": project,
        "project_planning": True,
        "project_view": True,
        "financial_view": False,
        "reports_view": False,
    }
    return render(request, "rh/projects/forms/project_form.html", context)


@cache_control(no_store=True)
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
            for disaggregation in target_location_form.instance.disaggregationlocation_set.all():
                initial_data.append({"disaggregation": disaggregation})

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
def get_disaggregations_forms(request):
    """Get target location empty form"""
    # Get selected indicators
    indicator = Indicator.objects.get(pk=request.POST.get("indicator"))
    locations_prefix = request.POST.getlist("locations_prefixes[]")

    related_disaggregations = indicator.disaggregation_set.all()

    location_disaggregation_dict = {}

    initial_data = []

    # Populate initial data with related disaggregations
    if len(related_disaggregations) > 0:
        for disaggregation in related_disaggregations:
            initial_data.append({"disaggregation": disaggregation})

        # Create DisaggregationFormSet for each location prefix
        for location_prefix in locations_prefix:
            # Check if is from the add new form or from the activity create
            DisaggregationFormSet.max_num = len(related_disaggregations)
            DisaggregationFormSet.extra = len(related_disaggregations)

            disaggregation_formset = DisaggregationFormSet(
                prefix=f"disaggregation_{location_prefix}", initial=initial_data
            )

            for disaggregation_form in disaggregation_formset.forms:
                # disaggregation_form = modelform_factory(DisaggregationLocation,fields=["target","disaggregation"])
                context = {
                    "disaggregation_form": disaggregation_form,
                }

                html = render_to_string("rh/projects/forms/disaggregation_empty_form.html", context)

                if location_prefix in location_disaggregation_dict:
                    location_disaggregation_dict[location_prefix].append(html)
                else:
                    location_disaggregation_dict.update({location_prefix: [html]})

    # Set back extra to 0 to avoid empty forms if refreshed.

    # Return JSON response containing generated HTML forms
    return JsonResponse(location_disaggregation_dict)


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


@cache_control(no_store=True)
@login_required
def project_planning_review(request, **kwargs):
    """Projects Plans"""

    pk = int(kwargs["project"])
    project = get_object_or_404(Project, pk=pk)
    activity_plans = project.activityplan_set.all()
    target_locations = [activity_plan.targetlocation_set.all() for activity_plan in activity_plans]

    context = {
        "project": project,
        "activity_plans": activity_plans,
        "target_locations": target_locations,
        "project_review": True,
        "project_view": True,
        "financial_view": False,
        "reports_view": False,
    }
    return render(request, "rh/projects/forms/project_review.html", context)


@cache_control(no_store=True)
@login_required
def submit_project(request, pk):
    """Project Submission"""

    project = get_object_or_404(Project, pk=pk)
    if project:
        project.state = "in-progress"
        project.save()

    activity_plans = project.activityplan_set.all()
    for plan in activity_plans:
        target_locations = plan.targetlocation_set.all()
        for target in target_locations:
            target.state = "in-progress"
            target.save()

        plan.state = "in-progress"
        plan.save()
    url = reverse("projects-detail", args=[project.pk])

    # Return the URL in a JSON response
    response_data = {"redirect_url": url}
    return JsonResponse(response_data)


@cache_control(no_store=True)
@login_required
def archive_project(request, pk):
    """Archiving Project"""
    project = get_object_or_404(Project, pk=pk)
    if project:
        activity_plans = project.activityplan_set.all()

        # Iterate through activity plans and archive them.
        for plan in activity_plans:
            target_locations = plan.targetlocation_set.all()

            # Iterate through target locations and archive them.
            for location in target_locations:
                disaggregation_locations = location.disaggregationlocation_set.all()

                # Iterate through disaggregation locations and archive.
                for disaggregation_location in disaggregation_locations:
                    disaggregation_location.active = False
                    disaggregation_location.save()

                location.state = "archive"
                location.active = False
                location.save()

            plan.state = "archive"
            plan.active = False
            plan.save()

        project.state = "archive"
        project.active = False
        project.save()

    url = reverse(
        "projects-list",
    )

    # Return the URL in a JSON response
    response_data = {"redirect_url": url}
    return JsonResponse(response_data)

    # return JsonResponse({"success": True})


@cache_control(no_store=True)
@login_required
def unarchive_project(request, pk):
    """Unarchiving Project"""
    project = get_object_or_404(Project, pk=pk)
    if project:
        activity_plans = project.activityplan_set.all()

        # Iterate through activity plans and archive them.
        for plan in activity_plans:
            target_locations = plan.targetlocation_set.all()

            # Iterate through target locations and archive them.
            for location in target_locations:
                disaggregation_locations = location.disaggregationlocation_set.all()

                # Iterate through disaggregation locations and archive.
                for disaggregation_location in disaggregation_locations:
                    disaggregation_location.active = True
                    disaggregation_location.save()

                location.state = "draft"
                location.active = True
                location.save()

            plan.state = "draft"
            plan.active = True
            plan.save()

        project.state = "draft"
        project.active = True
        project.save()

    url = reverse(
        "projects-list",
    )
    # Return the URL in a JSON response
    response_data = {"redirect_url": url}
    return JsonResponse(response_data)


@cache_control(no_store=True)
@login_required
def delete_project(request, pk):
    """Delete Project View"""
    project = get_object_or_404(Project, pk=pk)
    if project.state != "archive":
        if project:
            project.delete()
        url = reverse(
            "projects-list",
        )

    # Return the URL in a JSON response
    response_data = {"redirect_url": url}
    return JsonResponse(response_data)


@cache_control(no_store=True)
@login_required
def copy_project(request, pk):
    """Copying Project"""
    project = get_object_or_404(Project, pk=pk)

    if project:
        # Create a new project by duplicating the original project.
        new_project = get_object_or_404(Project, pk=pk)
        new_project.pk = None  # Generate a new primary key for the new project.

        # Modify the title, code, and state of the new project to indicate it's a copy.
        new_project.title = f"[COPY] - {project.title}"
        new_project.code = f"[COPY] - {project.code}"  # Generate a new primary key for the new project.
        new_project.state = "draft"
        new_project.hrp_code = ""

        new_project.save()  # Save the new project to the database.

        # Copy related data from the original project to the new project.
        new_project.clusters.set(project.clusters.all())
        new_project.activity_domains.set(project.activity_domains.all())
        new_project.donors.set(project.donors.all())
        new_project.programme_partners.set(project.programme_partners.all())
        new_project.implementing_partners.set(project.implementing_partners.all())

        # Check if the new project was successfully created.
        if new_project:
            # Get all activity plans associated with the original project.
            activity_plans = project.activityplan_set.all()

            # Iterate through each activity plan and copy it to the new project.
            for plan in activity_plans:
                new_plan = copy_project_activity_plan(new_project, plan)
                target_locations = plan.targetlocation_set.all()

                # Iterate through target locations and copy them to the new plan.
                for location in target_locations:
                    new_location = copy_project_target_location(new_plan, location)
                    disaggregation_locations = location.disaggregationlocation_set.all()

                    # Iterate through disaggregation locations and copy them to the new location.
                    for disaggregation_location in disaggregation_locations:
                        copy_target_location_disaggregation_locations(new_location, disaggregation_location)

        # Save the changes made to the new project.
        new_project.save()

        url = reverse("projects-detail", args=[new_project.pk])

        # Return the URL in a JSON response
        response_data = {"redirect_url": url}
        return JsonResponse(response_data)


def copy_project_activity_plan(project, plan):
    """Copy Activity Plans"""
    try:
        # Duplicate the original activity plan by retrieving it with the provided primary key.
        new_plan = get_object_or_404(ActivityPlan, pk=plan.pk)
        new_plan.pk = None  # Generate a new primary key for the duplicated plan.
        new_plan.save()  # Save the duplicated plan to the database.

        # Associate the duplicated plan with the new project.
        new_plan.project = project

        # Set the plan as active and in a draft state to indicate it's a copy.
        new_plan.active = True
        new_plan.state = "draft"

        # Copy indicators from the original plan to the duplicated plan.
        new_plan.indicator = plan.indicator

        # Save the changes made to the duplicated plan.
        new_plan.save()

        # Return the duplicated plan.
        return new_plan
    except Exception as _:
        # If an exception occurs, return False to indicate the copy operation was not successful.
        return False


def copy_project_target_location(plan, location):
    """Copy Target Locations"""
    try:
        # Duplicate the original target location
        # by retrieving it with the provided primary key.
        new_location = get_object_or_404(TargetLocation, pk=location.pk)
        new_location.pk = None  # Generate a new primary key for the duplicated location.
        new_location.save()  # Save the duplicated location to the database.

        # Associate the duplicated location with the new activity plan.
        new_location.activity_plan = plan
        new_location.project = plan.project

        # Set the location as active and in a draft state to indicate it's a copy.
        new_location.active = True
        new_location.state = "draft"

        # Save the changes made to the duplicated location.
        new_location.save()

        # Return the duplicated location.
        return new_location
    except Exception as _:
        # If an exception occurs, return False to indicate the copy operation was not successful.
        return False


def copy_target_location_disaggregation_locations(location, disaggregation_location):
    """Copy Disaggregation Locations"""
    try:
        # Duplicate the original disaggregation location by retrieving it with the provided primary key.
        new_disaggregation_location = get_object_or_404(DisaggregationLocation, pk=disaggregation_location.pk)
        new_disaggregation_location.pk = None  # Generate a new primary key for the duplicated location.
        new_disaggregation_location.save()  # Save the duplicated location to the database.

        # Associate the duplicated disaggregation location with the new target location.
        new_disaggregation_location.target_location = location

        # Save the changes made to the duplicated disaggregation location.
        new_disaggregation_location.save()

        # Return True to indicate that the copy operation was successful.
        return True
    except Exception as _:
        # If an exception occurs, return False to indicate the copy operation was not successful.
        return False


@cache_control(no_store=True)
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


@cache_control(no_store=True)
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


@cache_control(no_store=True)
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


@cache_control(no_store=True)
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


#############################################
########## Budget Progress Views ############
#############################################


@cache_control(no_store=True)
@login_required
def create_project_budget_progress_view(request, project):
    project = get_object_or_404(Project, pk=project)

    budget_progress = project.budgetprogress_set.all()

    BudgetProgressFormSet = modelformset_factory(BudgetProgress, form=BudgetProgressForm, extra=1)
    formset = BudgetProgressFormSet(request.POST or None, queryset=budget_progress, form_kwargs={"project": project})

    if request.method == "POST":
        country = request.POST.get("country")

        if formset.is_valid():
            for form in formset:
                if form.cleaned_data.get("save"):
                    if form.cleaned_data.get("activity_domain") and form.cleaned_data.get("donor"):
                        budget_progress = form.save(commit=False)
                        budget_progress.project = project
                        budget_progress.country_id = country
                        budget_progress.title = f"{budget_progress.donor}: {budget_progress.activity_domain}"
                        budget_progress.save()
            return redirect("create_project_budget_progress", project=project.pk)
        else:
            for form in formset:
                for error in form.errors:
                    error_message = f"Something went wrong {formset.errors}"
                    if form.errors[error]:
                        error_message = f"{error}: {form.errors[error][0]}"
                    messages.error(request, error_message)

    # progress = list(budget_progress.values_list("pk", flat=True))

    context = {
        "project": project,
        "formset": formset,
        "project_view": False,
        "financial_view": True,
        "reports_view": False,
    }
    return render(request, "rh/financial_reports/project_budget_progress.html", context)


@cache_control(no_store=True)
@login_required
def copy_budget_progress(request, project, budget):
    project = get_object_or_404(Project, pk=project)
    budget_progress = get_object_or_404(BudgetProgress, pk=budget)
    new_budget_progress = get_object_or_404(BudgetProgress, pk=budget_progress.pk)
    if new_budget_progress:
        new_budget_progress.pk = None
        new_budget_progress.save()
        new_budget_progress.project = project
        new_budget_progress.active = True
        new_budget_progress.state = "draft"
        new_budget_progress.title = f"[COPY] - {budget_progress.title}"
        new_budget_progress.save()
    return JsonResponse({"success": True})


@cache_control(no_store=True)
@login_required
def delete_budget_progress(request, pk):
    budget_progress = get_object_or_404(BudgetProgress, pk=pk)
    # project = budget_progress.project
    if budget_progress:
        budget_progress.delete()
    return JsonResponse({"success": True})


# Registration Organizations
@login_required
def organization_register(request):
    if request.method == "POST":
        org_form = OrganizationRegisterForm(request.POST)
        if org_form.is_valid():
            name = org_form.cleaned_data.get("name")
            code = org_form.cleaned_data.get("code")
            organization = org_form.save()
            if organization:
                messages.success(request, f"[{code}] {name} is registered successfully !")
            else:
                messages.error(request, "Something went wrong ! please try again ")
    else:
        org_form = OrganizationRegisterForm()
    context = {"org_form": org_form}
    return render(request, "rh/projects/forms/organization_register_form.html", context)


@login_required
def ProjectListView(request, flag):
    # project_list =json.loads(request.POST.get("projectList"))
    project = Project.objects.filter(user=request.user.id)
    dataset = ProjectResource().export(project)
    format = flag
    if format == "xls":
        ds = dataset.xls
    elif format == "csv":
        ds = dataset.csv
    else:
        ds = dataset.json
    response = HttpResponse(ds, content_type=f"{format}")
    response["Content-Disposition"] = f"attachment; filename=project.{format}"
    return response


@login_required
def update_indicator_type(request):
    if request.method == "POST":
        indicator_id = request.POST.get("id")

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


@login_required
def download_user_guide(request):
    document_path = os.path.join(settings.MEDIA_ROOT, 'documents', 'ReportHub-User-Guide.pdf')

    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You do not have permission to access this resource.")

    # Open the file in binary mode
    response = FileResponse(open(document_path, "rb"))
    
    return response