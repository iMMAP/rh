import csv
from copy import copy

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseClientRedirect
from extra_settings.models import Setting

from ..filters import ProjectsFilter
from ..forms import ProjectForm
from ..models import (
    ActivityPlan,
    BeneficiaryType,
    Cluster,
    Currency,
    Disaggregation,
    DisaggregationLocation,
    GrantType,
    ImplementationModalityType,
    Location,
    Organization,
    PackageType,
    Project,
    TargetLocation,
    TransferCategory,
    TransferMechanismType,
    UnitType,
)
from ..utils import has_permission


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
                    activity_domain = project.activity_domains.filter(name=row["activity_domain"]).first()
                    if not activity_domain:
                        errors.append(
                            f"Row {reader.line_num}: Activity domain '{row['activity_domain']}' does not exist in your project plan."
                        )
                        continue

                    activity_type = activity_domain.activitytype_set.filter(name=row["activity_type"]).first()
                    if not activity_type:
                        errors.append(
                            f"Row {reader.line_num}:Activity Domain {activity_domain.name} does not have Activity Type '{row['activity_type']}'"
                        )
                        continue

                    indicator = activity_type.indicator_set.filter(name=row["indicator"]).first()
                    if not indicator:
                        errors.append(
                            f"Row {reader.line_num}: Activity Type {activity_type.name} does not have Indicator '{row['indicator']}'"
                        )
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
                        country=Location.objects.get(code=row["country_code"]),
                        province=Location.objects.get(code=row["province_code"]),
                        district=Location.objects.get(code=row["district_code"]),
                        zone=Location.objects.filter(code=row["zone_code"]).first(),
                        implementing_partner=Organization.objects.filter(code=row["implementing_partner_code"]).first(),
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
@csrf_protect
def export_activity_plans_import_template(request, pk):
    project = get_object_or_404(Project.objects.prefetch_related("clusters"), pk=pk)

    # Add column names for ActivityPlan and TargetLocation models
    all_columns = [
        "activity_domain",
        "activity_type",
        "activity_detail",
        "indicator",
        "beneficiary",
        "hrp_beneficiary",
        "beneficiary_category",
        "description",
        "package_type",
        "unit_type",
        "units",
        "no_of_transfers",
        "grant_type",
        "transfer_category",
        "currency",
        "transfer_mechanism_type",
        "implement_modility_type",
        "country_name",
        "country_code",
        "province_name",
        "province_code",
        "district_name",
        "district_code",
        "zone_name",
        "zone_code",
        "location_type",
        "implementing_partner_code",
        "facility_site_type",
        "facility_monitoring",
        "facility_name",
        "facility_id",
        "facility_lat",
        "facility_long",
        "nhs_code",
    ]

    disaggregation_columns = list(
        Disaggregation.objects.filter(clusters__in=project.clusters.all()).distinct().values_list("name", flat=True)
    )

    filtered_columns = all_columns + disaggregation_columns

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename=project_{project.code}_activity_plans_import_template.csv"

    writer = csv.writer(response)
    writer.writerow(filtered_columns)

    return response


@login_required
@permission_required("rh.view_project", raise_exception=True)
def projects_detail(request, pk):
    """View a project details.
    url: projects/<int:pk>
    """
    project = get_object_or_404(
        Project.objects.select_related("organization", "user")
        .prefetch_related(
            "clusters",
            "programme_partners",
            "implementing_partners",
        )
        .annotate(
            activity_plans_count=Count("activityplan", distinct=True),
            target_locations_count=Count("activityplan__targetlocation", distinct=True),
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
        .order_by("-updated_at"),
    )

    # Setup Pagination
    RECORDS_PER_PAGE = Setting.get("RECORDS_PER_PAGE", default=10)
    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    p = Paginator(project_filter.qs, per_page=per_page)
    page = request.GET.get("page", 1)
    p_projects = p.get_page(page)
    p_projects.adjusted_elided_pages = p.get_elided_page_range(page)

    context = {
        "projects": p_projects,
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

    project = get_object_or_404(Project.objects.select_related("user").prefetch_related("clusters"), pk=pk)

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
    }

    return render(request, "rh/projects/forms/project_form.html", context)


@login_required
@permission_required("rh.submit_project", raise_exception=True)
def submit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if not has_permission(user=request.user, project=project):
        raise PermissionDenied

    activity_plans = project.activityplan_set.all()

    if not activity_plans.exists():
        messages.error(
            request,
            mark_safe(
                f"The project must have at least one activity plan and each Activity Plan must have one Target Location.Check project's `<a class='underline' href='{reverse('activity-plans-list', args=[project.pk])}'>Activity Plans</a>`"
            ),
        )
        return redirect("projects-detail", pk=project.pk)

    for plan in activity_plans:
        target_locations = plan.targetlocation_set.all()
        if not target_locations.exists():
            messages.error(
                request,
                mark_safe(
                    f"Each activity plan must have at least one target location. Check project's `<a class='underline' href='{reverse('target-locations-list', args=[project.pk])}'>target locations</a>`."
                ),
            )
            return redirect("projects-detail", pk=project.pk)

    project.state = "in-progress"
    project.save()

    activity_plans.update(state="in-progress")

    target_locations = TargetLocation.objects.filter(activity_plan__in=activity_plans)

    target_locations.update(state="in-progress")

    messages.success(request, "Project submited successfully!. You can start reporting now.")

    return redirect("projects-detail", pk=project.pk)


@login_required
@permission_required("rh.archive_unarchive_project", raise_exception=True)
@require_http_methods(["POST"])
def archive_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    state = "archived"

    activity_plans = project.activityplan_set.all()
    activity_plans.update(state=state)

    target_locations = TargetLocation.objects.filter(activity_plan__in=activity_plans)
    target_locations.update(state=state)

    project.state = state
    project.save()

    messages.success(request, "Project its activities and target locations has been archived")

    return HttpResponseClientRedirect(reverse("projects-detail", args=[project.id]))


@login_required
@permission_required("rh.archive_unarchive_project", raise_exception=True)
@require_http_methods(["POST"])
def unarchive_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    state = "draft"

    activity_plans = project.activityplan_set.all()
    activity_plans.update(state=state)

    target_locations = TargetLocation.objects.filter(activity_plan__in=activity_plans)
    target_locations.update(state=state)

    project.state = state
    project.save()

    messages.success(
        request,
        "Project its activities and target locations has been set to draft. submit the project again to start reporting",
    )

    return HttpResponseClientRedirect(reverse("projects-detail", args=[project.id]))


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
        else:
            messages.error(
                request,
                "The archived project cannot be deleted.",
            )
            return redirect("projects-delete", pk)


@login_required
@require_http_methods(["POST"])
def copy_project(request, pk):
    """Copy Project its Activity Plans and Target Locations"""
    project = get_object_or_404(Project, pk=pk)

    try:
        with transaction.atomic():
            new_project = Project.objects.get(pk=pk)
            new_project.pk = None
            new_project.title = f"DUPLICATED-{project.title}"
            new_project.code = f"DUPLICATED-{project.code}"
            new_project.state = "draft"

            try:
                new_project.full_clean()
            except ValidationError as e:
                messages.error(request, f"Error duplicating project: {e}")
                return HttpResponse(401)

            new_project.save()

            # Copy related data from the original project to the new project.
            new_project.clusters.set(project.clusters.all())
            new_project.activity_domains.set(project.activity_domains.all())
            new_project.donors.set(project.donors.all())
            new_project.programme_partners.set(project.programme_partners.all())
            new_project.implementing_partners.set(project.implementing_partners.all())

            # Copy ActivityPlan
            original_activity_plans = project.activityplan_set.all()
            new_activity_plans = []
            for plan in original_activity_plans:
                new_plan = copy(plan)
                new_plan.pk = None
                new_plan.project = new_project

                new_activity_plans.append(new_plan)

            new_activity_plans = ActivityPlan.objects.bulk_create(new_activity_plans)

            activity_plan_mapping = {}
            for old_plan, new_plan in zip(original_activity_plans, new_activity_plans):
                activity_plan_mapping[old_plan.pk] = new_plan.pk

            # Copy TargetLocation
            original_target_locations = list(TargetLocation.objects.filter(activity_plan__project=project))
            new_target_locations = []
            for location in original_target_locations:
                new_location = copy(location)
                new_location.pk = None
                new_location.project = new_project
                new_location.activity_plan_id = activity_plan_mapping[location.activity_plan_id]

                new_target_locations.append(new_location)

            new_target_locations = TargetLocation.objects.bulk_create(new_target_locations)

            target_location_mapping = {}
            for old, new in zip(original_target_locations, new_target_locations):
                target_location_mapping[old.id] = new.id

            # Copy DisaggregationLocation
            original_disagg_locations = DisaggregationLocation.objects.filter(
                target_location__in=original_target_locations
            )
            new_disagg_locations = []
            for disagg_location in original_disagg_locations:
                new_disagg_location = copy(disagg_location)
                new_disagg_location.pk = None
                new_disagg_location.target_location_id = target_location_mapping[disagg_location.target_location_id]

                new_disagg_locations.append(new_disagg_location)

            DisaggregationLocation.objects.bulk_create(new_disagg_locations)
    except Exception as e:
        messages.error(request, f"Error duplicating project : {str(e)}")
        return HttpResponse(500)

    messages.success(request, "Project its Activity Plans and Target Locations duplicated successfully!")
    return HttpResponseClientRedirect(reverse("projects-detail", args=[new_project.id]))
