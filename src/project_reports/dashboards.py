from django.core.paginator import Paginator
from django.shortcuts import render

from .filters import ReportFilterForm
from .models import ProjectMonthlyReport

RECORDS_PER_PAGE = 3


def reports_dashboard_view(request):
    """Reports Dashboard"""
    # Setup Filter
    reports_filter = ReportFilterForm(
        request.GET,
        queryset=ProjectMonthlyReport.objects.all().order_by("-id"),
    )

    # Setup Pagination
    p = Paginator(reports_filter.qs, RECORDS_PER_PAGE)
    page = request.GET.get("page")
    p_reports = p.get_page(page)
    total_pages = "a" * p_reports.paginator.num_pages

    context = {
        "reports_count": ProjectMonthlyReport.objects.all().count,
        "project_reports": p_reports,
        "reports_filter": reports_filter,
        "total_pages": total_pages,
    }

    return render(request, "project_reports/dashboards/reports_dashboard.html", context)
