from django.core.paginator import Paginator
from django.shortcuts import render

from .filters import ReportFilterForm
from .models import ProjectMonthlyReport

RECORDS_PER_PAGE = 2


def reports_dashboard_view(request):
    """Reports Dashboard"""
    cluster = request.GET.get("cluster", None)
    organization = request.GET.get("organization", None)
    start_date = request.GET.get("Date_min", None)
    end_date = request.GET.get("Date_max", None)

    # Filter Queryset
    queryset = ProjectMonthlyReport.objects.all()

    # Filter by cluster and organization through the Project model
    if cluster:
        queryset = queryset.filter(project__clusters=cluster)
    if organization:
        queryset = queryset.filter(project__organizations=organization)

    # Filter by date range
    if start_date:
        queryset = queryset.filter(month__gte=start_date)
    if end_date:
        queryset = queryset.filter(month__lte=end_date)

    # Setup Filter
    reports_filter = ReportFilterForm(
        # FIXME: FIX THIS PART
        # request.GET,
        queryset=queryset.order_by("-id"),
    )

    # Setup Pagination
    p = Paginator(reports_filter.qs, RECORDS_PER_PAGE)
    page = request.GET.get("page")
    p_reports = p.get_page(page)
    total_pages = "a" * p_reports.paginator.num_pages

    context = {
        "reports_count": queryset.count(),  # Count of filtered queryset
        "project_reports": p_reports,
        "reports_filter": reports_filter,
        "total_pages": total_pages,
    }

    return render(request, "project_reports/dashboards/reports_dashboard.html", context)
