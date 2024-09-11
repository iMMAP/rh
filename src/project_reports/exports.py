import base64
from io import BytesIO
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from openpyxl import Workbook
from openpyxl.styles import Font, NamedStyle

from django.db.models import Q, Prefetch
from rh.models import Project
from .utils import write_project_report_sheet
from .models import ActivityPlanReport, DisaggregationLocationReport, ProjectMonthlyReport, TargetLocationReport

#############################################
############### Export Views #################
#############################################

# Define the header style
header_style = NamedStyle(name="header")
header_style.font = Font(bold=True)


# export all projects monlthly report
def export_all_monthly_reports_view(request):
    try:
        # Get User Clusters
        user_clusters = request.user.profile.clusters.all()

        # Filter Queryset
        # project_reports = ProjectMonthlyReport.objects.filter(project__clusters__in=user_clusters).distinct()
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
            .filter(project__clusters__in=user_clusters)
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
            "file_name": "all_monthly_reports.xlsx",
        }

        return JsonResponse(response)
    except Exception as e:
        response = {"error": str(e)}
        return JsonResponse(response, status=500)


# export monthly report for single project
def export_monthly_report_view(request, pk):
    if request.method == "POST":
        state = None
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        state = request.POST.get("state")
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
            .filter(project=project)
        )
        try:
            monthly_progress_report = monthly_progress_report.filter(
                Q(from_date__gte=start_date) & Q(to_date__lte=end_date)
            )

        except Exception:
            print("No filter applied.")
        # check the state criteria
        if state:
            monthly_progress_report = monthly_progress_report.filter(state=state)

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
