from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rh.models import Organization, Project


from .filters import MonthlyReportsFilter
from .models import ProjectMonthlyReport, ClusterDashboardReport

RECORDS_PER_PAGE = 5


@login_required
def reports_dashboard_view(request):
    """Reports Dashboard"""
    # Get filter parameters from the request
    clusters = request.GET.getlist("project__clusters")
    implementing_partners = request.GET.getlist("project__implementing_partners")
    start_date = request.GET.get("report_date_min", None)  # 'date_0' for start date
    end_date = request.GET.get("report_date_max", None)  # 'date_1' for end date
    # Get User Clusters
    user_clusters = request.user.profile.clusters.all()
    user_clusters_list = list(request.user.profile.clusters.all())

    selected_cluster = None
    powerbi_report_url = None
    message = None

    if len(user_clusters_list) == 1:
        cluster = user_clusters_list[0]
        powerbi_reports = ClusterDashboardReport.objects.filter(cluster=cluster).first()
        powerbi_report_url = powerbi_reports.report_link if powerbi_reports else None
        selected_cluster = cluster.code
        if not powerbi_report_url:
            message = "No report available for your cluster..."
    else:
        selected_cluster = request.GET.get("cluster")
        if not selected_cluster:
            message = "Please select a cluster to view the report..."
        else:
            cluster = user_clusters.filter(code=selected_cluster).first()
            if cluster:
                report = ClusterDashboardReport.objects.filter(cluster=cluster).first()
                powerbi_report_url = report.report_link if report else None
            if not powerbi_report_url:
                message = "No report available for the selected cluster..."

    # Filter Queryset
    queryset = ProjectMonthlyReport.objects.filter(project__clusters__in=user_clusters).distinct()
    projects = Project.objects.filter(clusters__in=user_clusters).distinct()
    organizations = Organization.objects.all().distinct()

    # Filter by cluster and organization through the Project model
    if clusters:
        queryset = queryset.filter(project__clusters__in=clusters)
    if implementing_partners:
        queryset = queryset.filter(project__implementing_partners__in=implementing_partners)
        projects = projects.filter(implementing_partners__in=implementing_partners)
        organizations = organizations.filter(id__in=implementing_partners)

    # Filter by date range
    if start_date:
        queryset = queryset.filter(report_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(report_date__lte=end_date)

    reports_total = queryset.count()
    reports_todo = queryset.filter(state="todo").count()
    reports_pending = queryset.filter(state="pending").count()
    reports_complete = queryset.filter(state="complete").count()

    # Initialize filter form with filter parameters and queryset
    reports_filter = MonthlyReportsFilter(
        request.GET,
        queryset=queryset.order_by("-id"),
    )

    # Retain filter parameters in pagination links
    query_params = request.GET.copy()
    if "page" in query_params:
        del query_params["page"]
    pagination_query_string = query_params.urlencode()

    context = {
        "reports_count": queryset.count(),  # Count of filtered queryset
        "project_reports": reports_filter.qs,
        "reports_filter": reports_filter,
        "pagination_query_string": pagination_query_string,
        "organizations": organizations.count(),
        "projects": projects.count(),
        "reports_total": reports_total,
        "reports_todo": reports_todo,
        "reports_pending": reports_pending,
        "reports_complete": reports_complete,
        "user_clusters_list": user_clusters_list,
        "powerbi_report_url": powerbi_report_url,
        "selected_cluster": selected_cluster,
        "message": message,
    }

    return render(request, "project_reports/dashboards/reports_dashboard.html", context)
