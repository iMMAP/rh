import datetime
import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from openpyxl.styles import Font, NamedStyle
from rh.models import Cluster, Organization, Project
from rh.utils import is_cluster_lead
from stock.models import StockMonthlyReport, StockReport
from stock.utils import write_csv_columns_and_rows

from project_reports.filters import MonthlyReportsFilter

from .models import ActivityPlanReport, DisaggregationLocationReport, ProjectMonthlyReport, TargetLocationReport
from .utils import write_projects_reports_to_csv

#############################################
############### Export Views #################
#############################################

# Define the header style
header_style = NamedStyle(name="header")
header_style.font = Font(bold=True)


@login_required
def cluster_5w_dashboard_export(request, code):
    cluster = get_object_or_404(Cluster, code=code)

    body = json.loads(request.body)

    from_date = body.get("from")
    if not from_date:
        from_date = datetime.date(datetime.datetime.now().year, 1, 1)

    to_date = body.get("to")
    if not to_date:
        to_date = datetime.datetime.now().date()

    user_country = request.user.profile.country

    filter_params = {
        "project__clusters__in": [cluster],
        "state__in": ["submited", "completed"],
        "from_date__lte": to_date,
        "to_date__gte": from_date,
        "project__user__profile__country": user_country,
        "activityplanreport__activity_plan__activity_domain__clusters__in": [cluster],
    }

    organization_code = body.get("organization")
    if organization_code:
        filter_params["project__organization__code"] = organization_code

    if not is_cluster_lead(
        user=request.user,
        clusters=[
            cluster.code,
        ],
    ):
        raise PermissionDenied

    try:
        project_reports = (
            ProjectMonthlyReport.objects.select_related("project")
            .prefetch_related(
                Prefetch(
                    "activityplanreport_set",
                    queryset=ActivityPlanReport.objects.prefetch_related(
                        Prefetch(
                            "targetlocationreport_set",
                            queryset=TargetLocationReport.objects.prefetch_related(
                                Prefetch(
                                    "disaggregationlocationreport_set",
                                    DisaggregationLocationReport.objects.select_related("disaggregation"),
                                )
                            ),
                        )
                    ),
                )
            )
            .filter(**filter_params)
            .distinct()
        )

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=reports.csv"
        write_projects_reports_to_csv(project_reports, response)
        return response

    except Exception as e:
        response = {"error": str(e)}
        return HttpResponse(response, status=500)


@login_required
def cluster_5w_stock_report_export(request, code):
    cluster = get_object_or_404(Cluster, code=code)

    body = json.loads(request.body)

    from_date = body.get("from")
    if not from_date:
        from_date = datetime.date(datetime.datetime.now().year, 1, 1)

    to_date = body.get("to")
    if not to_date:
        to_date = datetime.datetime.now().date()

    user_country = request.user.profile.country

    filter_params = {
        "stockreport__cluster__in": [cluster],
        "state__in": ["submitted"],
        "from_date__lte": to_date,
        "due_date__gte": from_date,
        "warehouse_location__user__profile__country": user_country,
    }

    organization_code = body.get("organization")
    if organization_code:
        filter_params["warehouse_location__organization__code"] = organization_code

    if not is_cluster_lead(
        user=request.user,
        clusters=[
            cluster.code,
        ],
    ):
        raise PermissionDenied
    try:
        stock_monthly_reports = (
            StockMonthlyReport.objects.select_related("warehouse_location")
            .prefetch_related(Prefetch("stockreport_set", queryset=StockReport.objects.all()))
            .filter(**filter_params)
            .distinct()
        )
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=reports.csv"
        write_csv_columns_and_rows(stock_monthly_reports, response)
        return response
    except Exception as e:
        response = {"error": str(e)}
        return HttpResponse(response, status=500)


@login_required
def org_5w_dashboard_export(request, code):
    org = get_object_or_404(Organization, code=code)

    if not org.code == request.user.profile.organization.code and not is_cluster_lead(
        request.user, org.clusters.values_list("code", flat=True)
    ):
        raise PermissionDenied

    body = json.loads(request.body)

    from_date = body.get("from")
    if not from_date:
        from_date = datetime.date(datetime.datetime.now().year, 1, 1)

    to_date = body.get("to")
    if not to_date:
        to_date = datetime.datetime.now().date()

    filter_params = {
        "project__organization": org,
        "state__in": ["submited", "completed"],
        "from_date__lte": to_date,
        "to_date__gte": from_date,
    }

    cluster_code = body.get("cluster")
    if cluster_code:
        filter_params["project__clusters__code__in"] = [
            cluster_code,
        ]

    try:
        project_reports = (
            ProjectMonthlyReport.objects.select_related("project")
            .prefetch_related(
                Prefetch(
                    "activityplanreport_set",
                    queryset=ActivityPlanReport.objects.prefetch_related(
                        Prefetch(
                            "targetlocationreport_set",
                            queryset=TargetLocationReport.objects.prefetch_related(
                                Prefetch(
                                    "disaggregationlocationreport_set",
                                    DisaggregationLocationReport.objects.select_related("disaggregation"),
                                )
                            ),
                        )
                    ),
                )
            )
            .filter(**filter_params)
            .distinct()
        )

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=reports.csv"
        write_projects_reports_to_csv(project_reports, response)
        return response
    except Exception as e:
        print(f"Error: {e}")
        return HttpResponse(status=500)


# export monthly report for single project
@login_required
def export_monthly_report_view(request, pk):
    # set the query
    project = get_object_or_404(Project, pk=pk)

    monthly_progress_report = (
        ProjectMonthlyReport.objects.select_related("project")
        .prefetch_related(
            Prefetch(
                "activityplanreport_set",
                queryset=ActivityPlanReport.objects.prefetch_related(
                    Prefetch(
                        "targetlocationreport_set",
                        queryset=TargetLocationReport.objects.prefetch_related(
                            Prefetch(
                                "disaggregationlocationreport_set",
                                DisaggregationLocationReport.objects.select_related("disaggregation"),
                            )
                        ),
                    )
                ),
            )
        )
        .filter(project=project, state="completed")
        .order_by("-from_date")
    )
    reports_filter = MonthlyReportsFilter(
        request.GET,
        request=request,
        queryset=monthly_progress_report,
    )
    today = datetime.datetime.now()
    today_date = today.today().strftime("%d-%m-%Y")
    try:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename=project_monthly_reports_{today_date}.csv"
        write_projects_reports_to_csv(reports_filter.qs, response)
        return response
    except Exception as e:
        response = {"error": str(e)}
        return HttpResponse(response, status=500)


def export_org_stock_monthly_report(request, code):
    org = get_object_or_404(Organization, code=code)

    if not org.code == request.user.profile.organization.code and not is_cluster_lead(
        request.user, org.clusters.values_list("code", flat=True)
    ):
        raise PermissionDenied

    body = json.loads(request.body)

    cluster_code = body.get("cluster")
    from_date = body.get("from")
    if not from_date:
        from_date = datetime.date(datetime.datetime.now().year, 1, 1)

    to_date = body.get("to")
    if not to_date:
        to_date = datetime.datetime.now().date()

    filter_params = {
        "warehouse_location__organization": org,
        "state__in": ["submitted"],
        "from_date__lte": to_date,
        "due_date__gte": from_date,
    }

    cluster_code = body.get("cluster")
    if cluster_code:
        filter_params["stockreport__cluster__code__in"] = [
            cluster_code,
        ]
    stock_monthly_report = (
        StockMonthlyReport.objects.select_related("warehouse_location")
        .prefetch_related(Prefetch("stockreport_set", queryset=StockReport.objects.all()))
        .filter(**filter_params)
        .distinct()
    )
    today = datetime.datetime.now()
    filename = today.today().strftime("%d-%m-%Y")

    try:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={code}_stock_reports_exported_on_{filename}.csv"
        write_csv_columns_and_rows(stock_monthly_report, response)
        return response
    except Exception as e:
        print(f"Error: {e}")
        return HttpResponse(status=500)
