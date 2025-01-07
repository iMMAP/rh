import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from openpyxl.styles import Font, NamedStyle

from project_reports.filters import MonthlyReportsFilter, Organization5WFilter
from rh.models import Cluster, Organization, Project
from users.utils import is_cluster_lead

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

    user_country = request.user.profile.country

    filter_params = {
        "project__clusters__in": [cluster],
        "state__in": ["submited", "completed"],
        "project__user__profile__country": user_country,
        "activityplanreport__activity_plan__activity_domain__clusters__in": [cluster],
    }

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

        monthly_reports_filter = Organization5WFilter(request.GET, queryset=project_reports, user=request.user)

        today = datetime.datetime.now()
        today_date = today.today().strftime("%d-%m-%Y")

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={cluster.code}_5w_reports_data_{today_date}.csv"

        write_projects_reports_to_csv(monthly_reports_filter.qs, response)

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
            .filter(project__organization=org)
            .distinct()
        )

        monthly_reports_filter = Organization5WFilter(request.GET, queryset=project_reports, user=request.user)

        today = datetime.datetime.now()
        today_date = today.today().strftime("%d-%m-%Y")
        monthly_reports_queryset = monthly_reports_filter.qs

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={org.code}_5w_reports_data_{today_date}.csv"

        write_projects_reports_to_csv(monthly_reports_queryset, response)

        return response
    except Exception as e:
        print(f"Error: {e}")
        return HttpResponse(status=500, content=e)


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
