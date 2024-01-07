import base64

# import datetime
# import json
from io import BytesIO

from django.http import JsonResponse

# from django.utils import timezone
from django.views import View
from openpyxl import Workbook
from openpyxl.styles import Font, NamedStyle
from openpyxl.utils import get_column_letter

from .models import ProjectMonthlyReport

#############################################
############### Export Views #################
#############################################

# Define the header style
header_style = NamedStyle(name="header")
header_style.font = Font(bold=True)


class ProjectReportExportExcelView(View):
    """
    View class for exporting project data to Excel.
    """

    def post(self, request, report):
        """
        Handle POST request to export project data to Excel.

        Args:
            request (HttpRequest): The HTTP request object.
            report (int): The ID of the report.

        Returns:
            JsonResponse: The JSON response containing the file URL and name, or an error message.
        """
        try:
            project_report = ProjectMonthlyReport.objects.get(id=report)  # Get the project object

            workbook = Workbook()

            self.write_project_report_sheet(workbook, project_report)
            # self.write_activity_plan_report_sheet(workbook, project_report)
            # self.write_target_locations_report_sheet(workbook, project_report)

            excel_file = BytesIO()
            workbook.save(excel_file)
            excel_file.seek(0)

            response = {
                "file_url": "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,"
                + base64.b64encode(excel_file.read()).decode("utf-8"),
                "file_name": "monthly_report.xlsx",
            }

            return JsonResponse(response)
        except Exception as e:
            response = {"error": str(e)}
            return JsonResponse(response, status=500)

    def write_project_report_sheet(self, workbook, project_report):
        """
        Write the project monthly report sheet to the workbook.

        Args:
            workbook (Workbook): The Excel workbook object.
            project_report (Project): The project_report object.
        """
        sheet = workbook.active
        sheet.title = "Monthly Report"

        # Define column headers and types
        columns = [
            {"header": "Project Code", "type": "string", "width": 20},
            {"header": "activity_domain", "type": "string", "width": 40},
            {"header": "activity_type", "type": "string", "width": 40},
            {"header": "activity_detail", "type": "string", "width": 40},
            {"header": "indicator", "type": "string", "width": 40},
            {"header": "report_types", "type": "string", "width": 20},
            {"header": "country", "type": "string", "width": 20},
            {"header": "province", "type": "string", "width": 20},
            {"header": "district", "type": "string", "width": 20},
            {"header": "zone", "type": "string", "width": 20},
            {"header": "location_type", "type": "string", "width": 20},
            {"header": "disaggregation", "type": "string", "width": 20},
            {"header": "target", "type": "string", "width": 20},
        ]

        self.write_sheet_columns(sheet, columns)
        self.write_project_report_data_rows(sheet, project_report)

    def write_sheet_columns(self, sheet, columns):
        """
        Write column headers and formatting for a sheet.

        Args:
            sheet (Worksheet): The worksheet object.
            columns (list): List of dictionaries containing column header, type, and width information.
        """
        for idx, column in enumerate(columns, start=1):
            cell = sheet.cell(row=1, column=idx, value=column["header"])
            cell.style = header_style

            column_letter = get_column_letter(idx)
            if column["type"] == "number":
                sheet.column_dimensions[column_letter].number_format = "General"
            elif column["type"] == "date":
                sheet.column_dimensions[column_letter].number_format = "mm-dd-yyyy"

            sheet.column_dimensions[column_letter].width = column["width"]

    def write_project_report_data_rows(self, sheet, project_report):
        """
        Write project data rows to the sheet.

        Args:
            sheet (Worksheet): The worksheet object.
            project (Project): The project_report object.
        """
        rows = []
        activity_plans = project_report.project.activityplan_set.all()
        for plan in activity_plans:
            target_locations = plan.targetlocation_set.all()
            for location in target_locations:
                disaggregation_locations = location.disaggregationlocation_set.all()
                for disaggregation in disaggregation_locations:
                    rows.append(
                        project_report.project.code,
                        plan.activity_domain,
                        plan.activity_type,
                        plan.activity_detail,
                        plan.activity_detail,
                        location.country,
                        location.province,
                        location.district,
                    )

        for row in rows:
            for col_idx, value in enumerate(row, start=1):
                sheet.cell(row=2, column=col_idx, value=value)

        sheet.freeze_panes = sheet["A2"]

    # def write_activity_plan_report_sheet(self, workbook, project_report):
    #     """
    #     Write the population sheet to the workbook.

    #     Args:
    #         workbook (Workbook): The Excel workbook object.
    #         project (Project): The project object.
    #     """
    #     sheet = workbook.create_sheet(title="Target Population")

    #     # Define column headers and types for Sheet 2
    #     columns = [
    #         {"header": "Monthly Report ID", "type": "string", "width": 20},
    #         {"header": "Activity Plan", "type": "string", "width": 20},
    #         {"header": "Indicator", "type": "string", "width": 40},
    #         {"header": "Report Types", "type": "string", "width": 40},
    #     ]

    #     self.write_sheet_columns(sheet, columns)
    #     self.write_activity_plan_report_data_rows(sheet, project_report)

    #     sheet.freeze_panes = sheet["A2"]

    # def write_activity_plan_report_data_rows(self, sheet, project_report):
    #     """
    #     Write population data rows to the sheet.plan.activity_detail.name if plan.activity_detail else None,
    #             # "\n".join([indicator.name for indicator in plan.indicators.all()]),

    #     Args:
    #         sheet (Worksheet): The worksheet object.
    #         project (Project): The project object.
    #     """
    #     row = [
    #         project_report.pk,
    #         None,
    #         None,
    #         None,
    #     ]

    #     for col_idx, value in enumerate(row, start=1):
    #         sheet.cell(row=2, column=col_idx, value=value)

    # def write_target_locations_report_sheet(self, workbook, project_report):
    #     """
    #     Write the target locations sheet to the workbook.

    #     Args:
    #         workbook (Workbook): The Excel workbook object.
    #         project (Project): The project object.
    #     """

    #     sheet = workbook.create_sheet(title="Target Locations")

    #     # Define column headers and types for Sheet 3
    #     columns = [
    #         {"header": "Activity Plan Report ID", "type": "string", "width": 20},
    #         {"header": "Country", "type": "string", "width": 20},
    #         {"header": "Province", "type": "string", "width": 20},
    #         {"header": "District", "type": "string", "width": 20},
    #         {"header": "Zone/Ward", "type": "string", "width": 20},
    #         {"header": "Location Type", "type": "string", "width": 20},
    #     ]

    #     self.write_sheet_columns(sheet, columns)
    #     sheet.freeze_panes = sheet["A2"]
