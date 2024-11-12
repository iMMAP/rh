import base64
import datetime
import json
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from openpyxl import Workbook
from openpyxl.styles import Font, NamedStyle
from rh.models import Cluster, Organization, Project
from rh.utils import is_cluster_lead

from .models import ActivityPlanReport, DisaggregationLocationReport, ProjectMonthlyReport, TargetLocationReport
from .utils import write_project_report_sheet

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

        workbook = Workbook()
        # write the data into excel sheet
        write_project_report_sheet(workbook, project_reports)
        excel_file = BytesIO()
        workbook.save(excel_file)
        excel_file.seek(0)

        response = {
            "file_url": "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,"
            + base64.b64encode(excel_file.read()).decode("utf-8"),
            "file_name": f"5w-data-{cluster.code}-{from_date}-to-{to_date}.xlsx",
        }

        return JsonResponse(response)
    except Exception as e:
        response = {"error": str(e)}
        return JsonResponse(response, status=500)


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
        workbook = Workbook()
        # write the data into excel sheet
        write_project_report_sheet(workbook, project_reports)
        excel_file = BytesIO()
        workbook.save(excel_file)
        excel_file.seek(0)

        response = {
            "file_url": "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,"
            + base64.b64encode(excel_file.read()).decode("utf-8"),
            "file_name": f"5w-data-{org.code}-{from_date}-to-{to_date}.xlsx",
        }

        return JsonResponse(response)
    except Exception as e:
        response = {"error": str(e)}
        return JsonResponse(response, status=500)


# export monthly report for single project
@login_required
def export_monthly_report_view(request, pk):
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
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
    )
    try:
        monthly_progress_report = monthly_progress_report.filter(
            Q(from_date__gte=start_date) & Q(to_date__lte=end_date)
        )
    except Exception:
        print("No filter applied.")

    try:
        workbook = Workbook()
        # write the data into excel sheet
        write_project_report_sheet(workbook, monthly_progress_report)
        excel_file = BytesIO()
        workbook.save(excel_file)
        excel_file.seek(0)

        response = {
            "file_url": "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,"
            + base64.b64encode(excel_file.read()).decode("utf-8"),
            "file_name": f"{project.title}_monthly_reports.xlsx",
        }

        return JsonResponse(response)
    except Exception as e:
        response = {"error": str(e)}
        return JsonResponse(response, status=500)
