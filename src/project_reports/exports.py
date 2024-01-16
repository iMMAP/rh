import base64
from io import BytesIO

from django.http import JsonResponse
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
                "file_name": "monthly_report_template.xlsx",
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
            {"header": "indicator", "type": "string", "width": 40},
            {"header": "activity_domain", "type": "string", "width": 40},
            {"header": "activity_type", "type": "string", "width": 40},
            {"header": "activity_detail", "type": "string", "width": 40},
            {"header": "report_types", "type": "string", "width": 20},
            {"header": "country", "type": "string", "width": 20},
            {"header": "province", "type": "string", "width": 20},
            {"header": "district", "type": "string", "width": 20},
            {"header": "zone", "type": "string", "width": 20},
            {"header": "location_type", "type": "string", "width": 20},
        ]

        activity_plans = project_report.project.activityplan_set.all()
        disaggregations = []
        disaggregation_list = []
        for plan in activity_plans:
            target_locations = plan.targetlocation_set.all()
            for location in target_locations:
                disaggregation_locations = location.disaggregationlocation_set.all()
                for dl in disaggregation_locations:
                    if dl.disaggregation.name not in disaggregation_list:
                        disaggregation_list.append(dl.disaggregation.name)
                        disaggregations.append({"header": dl.disaggregation.name, "type": "string", "width": 20})
                    else:
                        continue
        if disaggregations:
            for disaggregation in disaggregations:
                columns.append(disaggregation)

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
            project_report (Project Report): The project_report object.
        """
        rows = []
        activity_plans = project_report.project.activityplan_set.all()
        for plan in activity_plans:
            target_locations = plan.targetlocation_set.all()
            indicators = plan.indicators.all()
            for indicator in indicators:
                for location in target_locations:
                    rows.append(
                        [
                            project_report.project.code if project_report.project else None,
                            indicator.name if indicator else None,
                            plan.activity_domain.code if plan.activity_domain else None,
                            plan.activity_type.code if plan.activity_type else None,
                            plan.activity_detail.code if plan.activity_detail else None,
                            None,
                            location.country.name if location.country else None,
                            location.province.name if location.province else None,
                            location.district.name if location.district else None,
                            location.zone.name if location.zone else None,
                            location.location_type,
                        ]
                    )

        for row_idx, row in enumerate(rows, start=2):
            for col_idx, value in enumerate(row, start=1):
                try:
                    sheet.cell(row=row_idx, column=col_idx, value=value)
                except Exception as e:
                    print(e)
        sheet.freeze_panes = sheet["A2"]
