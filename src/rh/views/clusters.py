from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from extra_settings.models import Setting
from project_reports.filters import MonthlyReportsFilter
from project_reports.models import ProjectMonthlyReport

from ..models import Cluster, Project
from ..utils import has_permission


def pending_reports(request, cluster: str):
    """reports of a cluster project {cluster}
    url: /clusters/{cluster_code}/reports"""

    # check if req.user is in the {cluster}_CLUSTER_LEADS group
    if not has_permission(request.user, clusters=[cluster]):
        raise PermissionDenied

    cluster = get_object_or_404(Cluster, code=cluster)

    reports_filter = MonthlyReportsFilter(
        request.GET,
        request=request,
        queryset=ProjectMonthlyReport.objects.filter(project__clusters__in=[cluster], project__state="in-progress")
        .select_related("project", "project__user")
        .order_by("-from_date"),
    )

    # Setup Pagination
    RECORDS_PER_PAGE = Setting.get("RECORDS_PER_PAGE", default=10)
    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    p = Paginator(reports_filter.qs, per_page=per_page)
    page = request.GET.get("page", 1)
    p_reports = p.get_page(page)
    p_reports.adjusted_elided_pages = p.get_elided_page_range(page)

    context = {"reports": p_reports, "filter": reports_filter}

    return render(request, "rh/clusters/cluster_project_reports.html", context)


def cluster_home(request, cluster: str):
    """Home page and overview of project's for a specified {cluster}
    url: /clusters/{cluster_code}
    """

    # check if req.user is in the {cluster}_CLUSTER_LEADS group
    if not has_permission(request.user, clusters=[cluster]):
        raise PermissionDenied

    cluster = Cluster.objects.get(code=cluster)

    active_projects = (
        Project.objects.filter(state="in-progress").filter(clusters__in=[cluster]).order_by("-updated_at")[:8]
    )

    pending_reports_qs = ProjectMonthlyReport.objects.filter(
        state="pending", project__clusters__in=[cluster], project__state="in-progress"
    )

    projects_qs = Project.objects.filter(state="in-progress", clusters__in=[cluster])
    counts = {
        "implementing_partners_count": projects_qs.aggregate(
            implementing_partners_count=Count("implementing_partners", distinct=True)
        )["implementing_partners_count"],
        "activity_plans_count": projects_qs.aggregate(activity_plans_count=Count("activityplan", distinct=True))[
            "activity_plans_count"
        ],
        "target_locations_count": projects_qs.aggregate(
            target_locations_count=Count("targetlocation__district", distinct=True)
        )["target_locations_count"],
    }

    counts["pending_reports_count"] = pending_reports_qs.count()

    context = {
        "active_projects": active_projects,
        "counts": counts,
        "pending_reports": pending_reports_qs.select_related("project", "project__user").distinct()[:8],
    }

    return render(request, "rh/clusters/cluster_home.html", context)
