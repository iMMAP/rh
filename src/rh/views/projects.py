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
from ..models import (
    ActivityPlan,
    Project,
    Cluster,
    TargetLocation,
    Disaggregation,
    ActivityDomain,
    Indicator,
    ActivityType,
    DisaggregationLocation,
    Location,
    BeneficiaryType,
    Organization,
    Currency,
    UnitType,
    GrantType,
    ImplementationModalityType,
    TransferCategory,
    TransferMechanismType,
    PackageType,
)
from django.contrib.auth.models import User
from .views import (
    copy_project_target_location,
    copy_target_location_disaggregation_locations,
)

from ..utils import has_permission
from django.utils.safestring import mark_safe
from extra_settings.models import Setting
from django_htmx.http import HttpResponseClientRedirect
import csv


@login_required
@require_http_methods(["GET", "POST"])
def import_activity_plans(request, pk):
    project = get_object_or_404(Project, pk=pk)
    errors = []

    if request.method == "POST":
        file = request.FILES.get("file")

        if file is None:
            messages.error(request, "No file provided for import.")
            return redirect(reverse("projects-ap-import-template", kwargs={"pk": project.pk}))

        decoded_file = file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        activity_plans = {}
        target_locations = []
        disaggregation_locations = []

        try:
            for row in reader:
                try:
                    activity_domain = ActivityDomain.objects.filter(name=row["activity_domain"]).first()
                    if not activity_domain:
                        errors.append(
                            f"Row {reader.line_num}: Activity domain '{row['activity_domain']}' does not exist."
                        )
                        continue

                    activity_type = ActivityType.objects.filter(name=row["activity_type"]).first()
                    if not activity_type:
                        errors.append(f"Row {reader.line_num}: Activity Type '{row['activity_type']}' does not exist.")
                        continue

                    indicator = Indicator.objects.filter(name=row["indicator"]).first()
                    if not indicator:
                        errors.append(f"Row {reader.line_num}: Indicator '{row['indicator']}' does not exist.")
                        continue

                    activity_plan_key = (row["activity_domain"], row["activity_type"], row["indicator"])

                    if activity_plan_key not in activity_plans:
                        activity_plan = ActivityPlan(
                            project=project,
                            activity_domain=activity_domain,
                            activity_type=activity_type,
                            indicator=indicator,
                            beneficiary=BeneficiaryType.objects.filter(name=row["beneficiary"]).first(),
                            hrp_beneficiary=BeneficiaryType.objects.filter(name=row["hrp_beneficiary"]).first(),
                            beneficiary_category=row["beneficiary_category"],
                            package_type=PackageType.objects.filter(name=row["package_type"]).first(),
                            unit_type=UnitType.objects.filter(name=row["unit_type"]).first(),
                            grant_type=GrantType.objects.filter(name=row["grant_type"]).first(),
                            transfer_category=TransferCategory.objects.filter(name=row["transfer_category"]).first(),
                            currency=Currency.objects.filter(name=row["currency"]).first(),
                            transfer_mechanism_type=TransferMechanismType.objects.filter(
                                name=row["transfer_mechanism_type"]
                            ).first(),
                            implement_modility_type=ImplementationModalityType.objects.filter(
                                name=row["implement_modility_type"]
                            ).first(),
                            description=row.get("description", None),
                        )
                        activity_plans[activity_plan_key] = activity_plan
                    else:
                        activity_plan = activity_plans[activity_plan_key]

                    target_location = TargetLocation(
                        activity_plan=activity_plan,
                        country=Location.objects.get(code=row["country"]),
                        province=Location.objects.get(code=row["province"]),
                        district=Location.objects.get(code=row["district"]),
                        zone=Location.objects.filter(code=row["zone"]).first(),
                        implementing_partner=Organization.objects.filter(code=row["implementing_partner"]).first(),
                        facility_name=row.get("facility_name") or None,
                        facility_id=row.get("facility_id") or None,
                        facility_lat=row.get("facility_lat") or None,
                        facility_long=row.get("facility_long") or None,
                        nhs_code=row.get("nhs_code", None),
                    )
                    target_locations.append(target_location)

                    all_disaggs = Disaggregation.objects.all()
                    for disag in all_disaggs:
                        if row.get(disag.name):
                            disaggregation_location = DisaggregationLocation(
                                target_location=target_location,
                                disaggregation=disag,
                                target=row.get(disag.name),
                            )
                            disaggregation_locations.append(disaggregation_location)
                except Exception as e:
                    errors.append(f"Error on row {reader.line_num}: {e}")

            if len(errors) > 0:
                messages.error(request, "Failed to import the Activities! Please check the errors below and try again.")
            else:
                ActivityPlan.objects.bulk_create(activity_plans.values())
                TargetLocation.objects.bulk_create(target_locations)
                DisaggregationLocation.objects.bulk_create(disaggregation_locations)
                messages.success(request, "Activities imported successfully.")
        except Exception as e:
            errors.append(f"Someting went wrong please check your data : {e}")
            messages.error(request, "An error occurred during the import process.")

    return render(request, "rh/activity_plans/import_activity_plans.html", {"project": project, "errors": errors})


@login_required
def export_activity_plans_import_template(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Add column names for ActivityPlan and TargetLocation models
    activity_plan_columns = [field.name for field in ActivityPlan._meta.get_fields() if field.concrete]
    target_location_columns = [field.name for field in TargetLocation._meta.get_fields() if field.concrete]

    disaggregation_columns = list(
        Disaggregation.objects.filter(clusters__in=project.clusters.all()).distinct().values_list("name", flat=True)
    )

    all_columns = activity_plan_columns + target_location_columns + disaggregation_columns

    filtered_columns = [
        col
        for col in all_columns
        if col not in ["id", "state", "updated_at", "created_at", "activity_plan", "disaggregations", "project"]
    ]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=activity_plans_import_template.csv"

    writer = csv.writer(response)
    writer.writerow(filtered_columns)

    return response


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
            Prefetch("user", queryset=User.objects.select_related("profile")),
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
    RECORDS_PER_PAGE = Setting.get("RECORDS_PER_PAGE", default=10)
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
        completed_projects_count=Count("id", filter=Q(state="completed")),
        archived_projects_count=Count("id", filter=Q(state="archived")),
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
    RECORDS_PER_PAGE = Setting.get("RECORDS_PER_PAGE", default=10)
    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    p = Paginator(project_filter.qs, per_page=per_page)
    page = request.GET.get("page", 1)
    p_projects = p.get_page(page)
    p_projects.adjusted_elided_pages = p.get_elided_page_range(page)

    projects = Project.objects.filter(clusters__in=user_clusters).aggregate(
        projects_count=Count("id"),
        draft_projects_count=Count("id", filter=Q(state="draft")),
        active_projects_count=Count("id", filter=Q(state="in-progress")),
        completed_projects_count=Count("id", filter=Q(state="completed")),
        archived_projects_count=Count("id", filter=Q(state="archived")),
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
    p_queryset = Project.objects.filter(organization=user_org)

    # Setup Filter
    project_filter = ProjectsFilter(
        request.GET,
        request=request,
        queryset=p_queryset.select_related("organization")
        .prefetch_related("clusters", "programme_partners", "implementing_partners")
        .order_by("-id"),
    )

    # Setup Pagination
    RECORDS_PER_PAGE = Setting.get("RECORDS_PER_PAGE", default=10)
    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    p = Paginator(project_filter.qs, per_page=per_page)
    page = request.GET.get("page", 1)
    p_projects = p.get_page(page)
    p_projects.adjusted_elided_pages = p.get_elided_page_range(page)

    projects_counts = project_filter.qs.aggregate(
        # draft_projects_count=Count("id", filter=Q(state="draft")),
        # active_projects_count=Count("id", filter=Q(state="in-progress")),
        pending_reports_count=Count("projectmonthlyreport", filter=Q(state="pending")),
        implementing_partners_count=Count("implementing_partners", distinct=True),
        activity_plans_count=Count("activityplan", distinct=True),
        target_locations_count=Count("targetlocation__province", distinct=True),
    )

    context = {
        "projects": p_projects,
        "counts": projects_counts,
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
            return redirect("activity-plans-list", project=project.pk)
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
        return redirect("activity-plans-list", project=project.pk)

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
            return redirect("activity-plans-list", project=project.pk)

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
                    disaggregation_location.save()

                location.state = "archived"
                location.save()

            plan.state = "archived"
            plan.save()

        project.state = "archived"
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
                    disaggregation_location.save()

                location.state = "draft"
                location.save()

            plan.state = "draft"
            plan.save()

        project.state = "draft"
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
        if project.state != "archived":
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
@require_http_methods(["POST"])
def copy_project(request, pk):
    """Copying Project"""
    project = get_object_or_404(Project, pk=pk)

    # Create a new project by duplicating the original project.
    new_project = get_object_or_404(Project, pk=pk)
    new_project.pk = None  # Generate a new primary key for the new project.

    # Modify the title, code, and state of the new project to indicate it's a copy.
    new_project.title = f"DUPLICATED-{project.title}"
    new_project.code = f"DUPLICATED-{project.code}"  # Generate a new primary key for the new project.
    new_project.state = "draft"

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

    messages.success(request, "Project its Activity Plans and Target Locations duplicated successfully!")
    return HttpResponseClientRedirect(reverse("projects-detail", args=[new_project.id]))


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
    user_org = request.user.profile.organization
    p_queryset = Project.objects.filter(organization=user_org)
    # projects = Project.objects.filter(organization=request.user.profile.organization)

    projects = ProjectsFilter(
        request.GET,
        request=request,
        queryset=p_queryset.select_related("organization")
        .prefetch_related("clusters", "programme_partners", "implementing_partners")
        .order_by("-id"),
    )

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
