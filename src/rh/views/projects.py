import json
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from rh.resources import ProjectResource

from ..filters import ProjectsFilter
from ..forms import ProjectForm
from ..models import ActivityPlan, Project, Cluster
from .views import (
    copy_project_target_location,
    copy_target_location_disaggregation_locations,
)

from ..utils import has_permission
from django.utils.safestring import mark_safe
from extra_settings.models import Setting

RECORDS_PER_PAGE = Setting.get("RECORDS_PER_PAGE", default=10)


@login_required
@permission_required("rh.view_project", raise_exception=True)
def projects_detail(request, pk):
    """View for viewing a project.
    url: projects/<int:pk>/
    """
    project = get_object_or_404(
        Project.objects.select_related("organization").prefetch_related(
            "clusters",
            "donors",
            "programme_partners",
            "implementing_partners",
            "user",
            Prefetch(
                "activityplan_set",
                ActivityPlan.objects.select_related("activity_domain", "indicator")
                .prefetch_related("activity_type", "activity_detail")
                .annotate(target_location_count=Count("targetlocation")),
            ),
        ),
        pk=pk,
    )

    if not has_permission(request.user, project):
        raise PermissionDenied

    context = {
        "project": project,
    }
    return render(request, "rh/projects/views/project_view.html", context)


@login_required
def cluster_projects_list(request, cluster: str):
    """List Project's of a specified {cluster}
    url: /projects/clusters/{cluster}
    """
    # check if req.user is in the {cluster}_CLUSTER_LEADS group
    if not has_permission(request.user, clusters=[cluster]):
        raise PermissionDenied

    cluster = Cluster.objects.get(code=cluster)

    # Setup Filter
    project_filter = ProjectsFilter(
        request.GET,
        request=request,
        queryset=Project.objects.filter(
            clusters__in=[
                cluster,
            ]
        )
        .select_related("organization")
        .prefetch_related("clusters", "programme_partners", "implementing_partners")
        .order_by("-id"),
    )

    # Setup Pagination
    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    p = Paginator(project_filter.qs, per_page=per_page)
    page = request.GET.get("page", 1)
    p_projects = p.get_page(page)
    p_projects.adjusted_elided_pages = p.get_elided_page_range(page)

    projects = Project.objects.filter(
        clusters__in=[
            cluster,
        ]
    ).aggregate(
        projects_count=Count("id"),
        draft_projects_count=Count("id", filter=Q(state="draft")),
        active_projects_count=Count("id", filter=Q(state="in-progress")),
        completed_projects_count=Count("id", filter=Q(state="done")),
        archived_projects_count=Count("id", filter=Q(state="archive")),
    )

    context = {
        "projects": p_projects,
        "projects_count": projects["projects_count"],
        "draft_projects_count": projects["draft_projects_count"],
        "active_projects_count": projects["active_projects_count"],
        "completed_projects_count": projects["completed_projects_count"],
        "archived_projects_count": projects["archived_projects_count"],
        "project_filter": project_filter,
    }

    return render(request, "rh/projects/views/projects_list_cluster.html", context)


@login_required
@permission_required("rh.view_clusters_projects", raise_exception=True)
def users_clusters_projects_list(request):
    """List Projects for user's cluster
    url: /projects/clusters
    """
    user_clusters = request.user.profile.clusters.all()

    # Setup Filter
    project_filter = ProjectsFilter(
        request.GET,
        request=request,
        queryset=Project.objects.filter(clusters__in=user_clusters)
        .select_related("organization")
        .prefetch_related("clusters", "programme_partners", "implementing_partners")
        .order_by("-id"),
    )

    # Setup Pagination
    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    p = Paginator(project_filter.qs, per_page=per_page)
    page = request.GET.get("page", 1)
    p_projects = p.get_page(page)
    p_projects.adjusted_elided_pages = p.get_elided_page_range(page)

    projects = Project.objects.filter(clusters__in=user_clusters).aggregate(
        projects_count=Count("id"),
        draft_projects_count=Count("id", filter=Q(state="draft")),
        active_projects_count=Count("id", filter=Q(state="in-progress")),
        completed_projects_count=Count("id", filter=Q(state="done")),
        archived_projects_count=Count("id", filter=Q(state="archive")),
    )

    context = {
        "projects": p_projects,
        "projects_count": projects["projects_count"],
        "draft_projects_count": projects["draft_projects_count"],
        "active_projects_count": projects["active_projects_count"],
        "completed_projects_count": projects["completed_projects_count"],
        "archived_projects_count": projects["archived_projects_count"],
        "project_filter": project_filter,
    }

    return render(request, "rh/projects/views/projects_list_cluster.html", context)


@login_required
@permission_required("rh.view_org_projects", raise_exception=True)
def org_projects_list(request):
    """List Projects for user's organization
    url: /projects
    """

    user_org = request.user.profile.organization

    # Setup Filter
    project_filter = ProjectsFilter(
        request.GET,
        request=request,
        queryset=Project.objects.filter(organization=user_org)
        .select_related("organization")
        .prefetch_related("clusters", "programme_partners", "implementing_partners")
        .order_by("-id"),
    )

    # Setup Pagination
    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    p = Paginator(project_filter.qs, per_page=per_page)
    page = request.GET.get("page", 1)
    p_projects = p.get_page(page)
    p_projects.adjusted_elided_pages = p.get_elided_page_range(page)

    projects = Project.objects.filter(organization=user_org).aggregate(
        projects_count=Count("id"),
        draft_projects_count=Count("id", filter=Q(state="draft")),
        active_projects_count=Count("id", filter=Q(state="in-progress")),
        completed_projects_count=Count("id", filter=Q(state="done")),
        archived_projects_count=Count("id", filter=Q(state="archive")),
    )

    context = {
        "projects": p_projects,
        "projects_count": projects["projects_count"],
        "draft_projects_count": projects["draft_projects_count"],
        "active_projects_count": projects["active_projects_count"],
        "completed_projects_count": projects["completed_projects_count"],
        "archived_projects_count": projects["archived_projects_count"],
        "project_filter": project_filter,
    }

    return render(request, "rh/projects/views/projects_list_org.html", context)


@login_required
@permission_required("rh.add_project", raise_exception=True)
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, user=request.user)
        if form.is_valid():
            project = form.save(commit=False)
            project.organization = request.user.profile.organization
            project.save()
            form.save_m2m()
            return redirect("activity-plans-create", project=project.pk)
        # Form is not valid
        messages.error(request, "Something went wrong. Please fix the errors below.")
    else:
        form = ProjectForm(user=request.user)

    context = {
        "form": form,
        "project_planning": True,
        "project_view": True,
        "financial_view": False,
        "reports_view": False,
    }
    return render(request, "rh/projects/forms/project_form.html", context)


@login_required
@permission_required("rh.change_project", raise_exception=True)
def update_project(request, pk):
    """View for updating a project."""

    project = get_object_or_404(Project, pk=pk)

    if not has_permission(user=request.user, project=project):
        raise PermissionDenied

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project, user=request.user)
        if form.is_valid():
            project = form.save()
            return redirect("activity-plans-create", project=project.pk)
        else:
            messages.error(request, "The form is invalid. Please check the fields and try again.")
    else:
        form = ProjectForm(instance=project, user=request.user)

    context = {
        "form": form,
        "project": project,
        "project_planning": True,
        "project_view": True,
        "financial_view": False,
        "reports_view": False,
    }
    return render(request, "rh/projects/forms/project_form.html", context)


@login_required
@permission_required("rh.submit_project", raise_exception=True)
def submit_project(request, pk):
    """Project Submission"""

    project = get_object_or_404(Project, pk=pk)

    if not has_permission(user=request.user, project=project):
        raise PermissionDenied

    activity_plans = project.activityplan_set.all()
    if not activity_plans.exists():
        messages.error(
            request,
            mark_safe(
                f"The project must have at least one activity plan. Check project's <a href=`{reverse('activity-plans-list', args=[project.pk])}`>activity plans</a>'."
            ),
        )
        messages.error(request, "The project must have at least one activity plan.")
        return redirect("projects-detail", pk=project.pk)

    for plan in activity_plans:
        target_locations = plan.targetlocation_set.all()
        if not target_locations.exists():
            messages.error(
                request,
                mark_safe(
                    f"Each activity plan must have at least one target location. Check project's `<a href='{reverse('target-locations-list', args=[project.pk])}'>target locations</a>`."
                ),
            )
            # return redirect("target-locations-create", activity_plan=plan.pk)
            return redirect("projects-detail", pk=project.pk)

    project.state = "in-progress"
    project.save()

    for plan in activity_plans:
        target_locations = plan.targetlocation_set.all()
        for target in target_locations:
            target.state = "in-progress"
            target.save()

        plan.state = "in-progress"
        plan.save()

    return redirect("projects-detail", pk=project.pk)


@login_required
@permission_required("rh.archive_unarchive_project", raise_exception=True)
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


@login_required
@permission_required("rh.archive_unarchive_project", raise_exception=True)
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


@login_required
@permission_required("rh.delete_project", raise_exception=True)
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "GET":
        return render(request, "rh/projects/views/delete_confirmation.html", {"project": project})
    elif request.method == "POST":
        if project.state != "archive":
            project.delete()
            messages.success(request, "Project deleted successfully")
            return redirect("projects-list")


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


@login_required
@require_http_methods(["POST"])
@permission_required("rh.export_clusters_projects", raise_exception=True)
def export_cluster_projects(request, format):
    """Export your all of your org projects and its activities
    url: /projects/bulk_export/<format>/cluster
    name: export-clusters-projects
    """
    selected_projects_id = json.loads(request.body)

    projects = Project.objects.filter(clusters__in=request.user.profile.clusters.all())

    if selected_projects_id:
        projects = projects.filter(id__in=selected_projects_id)

    dataset = ProjectResource().export(projects)

    if format == "xls":
        ds = dataset.xls
    elif format == "csv":
        ds = dataset.csv
    else:
        ds = dataset.json

    today_date = date.today()
    file_name = f"projects_{today_date}"
    response = HttpResponse(ds, content_type=f"{format}")
    response["Content-Disposition"] = f"attachment; filename={file_name}.{format}"

    return response


@login_required
@require_http_methods(["POST"])
@permission_required("rh.export_clusters_projects", raise_exception=True)
def export_org_projects(request, format):
    """Export your all of your org projects and its activities
    url: /projects/bulk_export/<format>/org
    name: export-org-projects
    """
    selected_projects_id = json.loads(request.body)

    projects = Project.objects.filter(organization=request.user.profile.organization)

    if selected_projects_id:
        projects = projects.filter(id__in=selected_projects_id)

    dataset = ProjectResource().export(projects)

    if format == "xls":
        ds = dataset.xls
    elif format == "csv":
        ds = dataset.csv
    else:
        ds = dataset.json

    today_date = date.today()
    file_name = f"projects_{today_date}"
    response = HttpResponse(ds, content_type=f"{format}")
    response["Content-Disposition"] = f"attachment; filename={file_name}.{format}"

    return response
