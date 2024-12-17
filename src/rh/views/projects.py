import csv
from copy import copy

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseClientRedirect
from extra_settings.models import Setting

from project_reports.models import ProjectMonthlyReport

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

IMPORT_ERRORS = {
    "no_file": "No file provided for import.",
    "activity_domain_missing": "Row {line}: Activity domain '{value}' does not exist in the project plan.",
    "activity_type_missing": "Row {line}: Activity Domain {domain} does not have Activity Type '{value}'",
    "indicator_missing": "Row {line}: Activity Type {type} does not have Indicator '{value}'",
    "location_missing": "Row {line}: {level} '{code}' does not exist. Check the {level} code.",
}


def _preload_project_data(project):
    return {
        "activity_domains": {ad.name: ad for ad in project.activity_domains.all()},
        "beneficiaries": {b.name: b for b in BeneficiaryType.objects.all()},
        "package_types": {pt.name: pt for pt in PackageType.objects.all()},
        "unit_types": {ut.name: ut for ut in UnitType.objects.all()},
        "grant_types": {gt.name: gt for gt in GrantType.objects.all()},
        "transfer_categories": {tc.name: tc for tc in TransferCategory.objects.all()},
        "currencies": {c.name: c for c in Currency.objects.all()},
        "transfer_mechanisms": {tm.name: tm for tm in TransferMechanismType.objects.all()},
        "implementation_modalities": {im.name: im for im in ImplementationModalityType.objects.all()},
        "locations": {loc.code: loc for loc in Location.objects.select_related("parent")},
        "organizations": {org.code: org for org in Organization.objects.all()},
        "disaggregations": {d.name: d for d in Disaggregation.objects.all()},
    }


def _validate_activity_data(row, project_data, project, errors, line_num):
    activity_domain = project_data["activity_domains"].get(row["activity_domain"])
    if not activity_domain:
        errors.append(IMPORT_ERRORS["activity_domain_missing"].format(line=line_num, value=row["activity_domain"]))
        return None, None, None

    activity_type = activity_domain.activitytype_set.filter(name=row["activity_type"]).first()
    if not activity_type:
        errors.append(
            IMPORT_ERRORS["activity_type_missing"].format(
                line=line_num, domain=activity_domain.name, value=row["activity_type"]
            )
        )
        return None, None, None

    indicator = activity_type.indicator_set.filter(name=row["indicator"]).first()
    if not indicator:
        errors.append(
            IMPORT_ERRORS["indicator_missing"].format(line=line_num, type=activity_type.name, value=row["indicator"])
        )
        return None, None, None

    return activity_domain, activity_type, indicator


def _validate_location_hierarchy(row, project_data, errors, line_num):
    country = project_data["locations"].get(row["admin0pcode"])
    if not country or country.level != 0:
        errors.append(IMPORT_ERRORS["location_missing"].format(line=line_num, level="Country", code=row["admin0pcode"]))
        return None, None, None, None

    province = None
    if row.get("admin1pcode"):
        province = next(
            (
                loc
                for loc in project_data["locations"].values()
                if loc.parent == country and loc.code == row["admin1pcode"] and loc.level == 1
            ),
            None,
        )
        if not province:
            errors.append(
                IMPORT_ERRORS["location_missing"].format(line=line_num, level="Province", code=row["admin1pcode"])
            )
            return country, None, None, None

    district = None
    if row.get("admin2pcode"):
        district = next(
            (
                loc
                for loc in project_data["locations"].values()
                if loc.parent == province and loc.code == row["admin2pcode"] and loc.level == 2
            ),
            None,
        )
        if not district:
            errors.append(
                IMPORT_ERRORS["location_missing"].format(line=line_num, level="District", code=row["admin2pcode"])
            )
            return country, province, None, None

    zone = None
    if row.get("admin3pcode"):
        zone = next(
            (
                loc
                for loc in project_data["locations"].values()
                if loc.parent == district and loc.code == row["admin3pcode"] and loc.level == 3
            ),
            None,
        )
        if not zone:
            errors.append(
                IMPORT_ERRORS["location_missing"].format(line=line_num, level="Zone", code=row["admin3pcode"])
            )

    return country, province, district, zone


def import_activity_plans(request, pk):
    project = get_object_or_404(Project, pk=pk)
    errors = []

    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            messages.error(request, IMPORT_ERRORS["no_file"])
            return redirect(reverse("projects-ap-import-template", kwargs={"pk": project.pk}))

        decoded_file = file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        # Prelooad some data to avoid calling DB in the Loop
        project_data = _preload_project_data(project)

        activity_plans = {}
        target_locations = []
        disaggregation_locations = []

        # Header row is line 1
        for line_num, row in enumerate(reader, start=2):
            try:
                activity_domain, activity_type, indicator = _validate_activity_data(
                    row, project_data, project, errors, line_num
                )
                if not activity_domain:
                    continue

                activity_plan_key = (row["activity_domain"], row["activity_type"], row["indicator"])
                if activity_plan_key not in activity_plans:
                    activity_plan = ActivityPlan(
                        project=project,
                        activity_domain=activity_domain,
                        activity_type=activity_type,
                        indicator=indicator,
                        beneficiary=project_data["beneficiaries"].get(row["beneficiary"]),
                        hrp_beneficiary=project_data["beneficiaries"].get(row["hrp_beneficiary"]),
                        package_type=project_data["package_types"].get(row["package_type"]),
                        unit_type=project_data["unit_types"].get(row["unit_type"]),
                        grant_type=project_data["grant_types"].get(row["grant_type"]),
                        transfer_category=project_data["transfer_categories"].get(row["transfer_category"]),
                        currency=project_data["currencies"].get(row["currency"]),
                        transfer_mechanism_type=project_data["transfer_mechanisms"].get(row["transfer_mechanism_type"]),
                        implement_modility_type=project_data["implementation_modalities"].get(
                            row["implement_modility_type"]
                        ),
                        description=row.get("description", None),
                    )
                    activity_plans[activity_plan_key] = activity_plan
                else:
                    activity_plan = activity_plans[activity_plan_key]

                # Validate locations
                country, province, district, zone = _validate_location_hierarchy(row, project_data, errors, line_num)
                if not country or not province or not district:
                    errors.append(f"Error on row {line_num}: {country} , {province}, {district}")
                    continue

                target_location = TargetLocation(
                    activity_plan=activity_plan,
                    country=country,
                    province=province,
                    district=district,
                    zone=zone,
                    implementing_partner=project_data["organizations"].get(row["implementing_partner_code"]),
                    facility_name=row.get("facility_name") or None,
                    facility_id=row.get("facility_id") or None,
                    facility_lat=row.get("facility_lat") or None,
                    facility_long=row.get("facility_long") or None,
                    nhs_code=row.get("nhs_code") or None,
                )
                target_locations.append(target_location)

                for disaggregation_name, disaggregation in project_data["disaggregations"].items():
                    if row.get(disaggregation_name):
                        disaggregation_location = DisaggregationLocation(
                            target_location=target_location,
                            disaggregation=disaggregation,
                            target=row[disaggregation_name],
                        )
                        disaggregation_locations.append(disaggregation_location)
            except Exception as e:
                errors.append(f"Error on row {line_num}: {e}")

        if errors:
            messages.error(request, "Failed to import the Activities! Please check the errors below and try again.")
        else:
            with transaction.atomic():
                ActivityPlan.objects.bulk_create(activity_plans.values())
                TargetLocation.objects.bulk_create(target_locations)
                DisaggregationLocation.objects.bulk_create(disaggregation_locations)

            messages.success(request, "Activities imported successfully.")

    return render(request, "rh/activity_plans/import_activity_plans.html", {"project": project, "errors": errors})


@login_required
@csrf_protect
def export_activity_plans_import_template(request, pk):
    project = get_object_or_404(Project.objects.prefetch_related("clusters"), pk=pk)

    # Add column names for ActivityPlan and TargetLocation models
    all_columns = [
        "project_code",
        "activity_domain",
        "activity_type",
        "activity_detail",
        "indicator",
        "beneficiary",
        "hrp_beneficiary",
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
        "admin0name",
        "admin0pcode",
        "admin1name",
        "admin1pcode",
        "admin2name",
        "admin2pcode",
        "admin3name",
        "admin3pcode",
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

    # Add the project code by default(This value will not impact the import function. it is just for users reference)
    writer.writerow([project.code])

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
        .select_related("organization", "user")
        .only(
            "id",
            "title",
            "code",
            "state",
            "end_date",
            "user__username",
            "user__email",
            "organization__name",
            "organization__code",
        )
        .prefetch_related(
            Prefetch("clusters", queryset=Cluster.objects.only("title", "code")),
            Prefetch("implementing_partners", queryset=Organization.objects.only("name", "code")),
        )
        .order_by("-updated_at"),
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

    project_filter = ProjectsFilter(
        request.GET,
        request=request,
        queryset=Project.objects.filter(clusters__in=user_clusters)
        .select_related("organization", "user")
        .only(
            "id",
            "title",
            "code",
            "state",
            "end_date",
            "user__username",
            "user__email",
            "organization__name",
            "organization__code",
        )
        .prefetch_related(
            Prefetch("clusters", queryset=Cluster.objects.only("title", "code")),
            Prefetch("implementing_partners", queryset=Organization.objects.only("name", "code")),
        )
        .order_by("-updated_at"),
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
        queryset=p_queryset.select_related("user")
        .only("id", "title", "code", "state", "end_date", "user__username", "user__email")
        .prefetch_related(
            Prefetch("clusters", queryset=Cluster.objects.only("title", "code")),
            Prefetch("implementing_partners", queryset=Organization.objects.only("name", "code")),
        )
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

            messages.success(request, f"Project with code `{project.code}` create successfully")

            return redirect("activity-plans-create", project=project.pk)
        else:
            # Form is not valid
            messages.error(request, "Something went wrong. Please fix the errors below.")
    else:
        form = ProjectForm(user=request.user)

    context = {
        "form": form,
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
                    f"Each activity plan must have at least one target location. Check project's `<a class='underline' href='{reverse('activity-plans-list', args=[project.pk])}'>Activity Plans</a>`."
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


@login_required
@require_http_methods(["POST"])
def complete_project(request, pk):
    project = get_object_or_404(Project.objects.select_related("user"), pk=pk)
    state = "completed"
    pending_reports = ProjectMonthlyReport.objects.filter(project=pk, state="pending")
    if pending_reports:
        messages.warning(
            request, "The project cannot be completed due to pending reports. Please submit all reports before closing."
        )
        return HttpResponseClientRedirect(reverse("project_reports_home", args=[project.id]))
    else:
        if project.state == state:
            messages.success(request, "Project has been marked as completed")
            return HttpResponseClientRedirect(reverse("projects-detail", args=[project.id]))

        # if has_permission(user=request.user,project=project):
        #     messages.error(request,"You do not have permission to mark the project as complete.")
        #     raise PermissionDenied

        project.state = state
        project.save()

        messages.success(request, "Project has been marked as completed")

        return HttpResponseClientRedirect(reverse("projects-detail", args=[project.id]))
