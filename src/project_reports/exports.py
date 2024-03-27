import base64
from io import BytesIO

from django.http import JsonResponse
from django.views import View
from openpyxl import Workbook
from openpyxl.styles import Font, NamedStyle
from openpyxl.utils import get_column_letter

from rh.models import Disaggregation

from .models import ProjectMonthlyReport

#############################################
############### Export Views #################
#############################################

# Define the header style
header_style = NamedStyle(name="header")
header_style.font = Font(bold=True)


class ReportTemplateExportView(View):
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
            for location in target_locations:
                rows.append(
                    [
                        project_report.project.code if project_report.project else None,
                        plan.indicator.name if plan.indicator else None,
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


class ReportsExportView(View):
    """Report Export"""

    def post(self, request):
        """
        Handle POST request to export project data to Excel.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            JsonResponse: The JSON response containing the file URL and name, or an error message.
        """
        try:
            # Get User Clusters
            user_clusters = request.user.profile.clusters.all()

            # Filter Queryset
            project_reports = ProjectMonthlyReport.objects.filter(project__clusters__in=user_clusters).distinct()

            workbook = Workbook()

            self.write_project_report_sheet(workbook, project_reports)

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

    def write_project_report_sheet(self, workbook, project_reports):
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
            {"header": "Report", "type": "string", "width": 20},
            {"header": "Report Status", "type": "string", "width": 20},
            {"header": "Report Month", "type": "string", "width": 20},
            {"header": "Report Year", "type": "string", "width": 20},
            {"header": "Report Period", "type": "string", "width": 20},
            {"header": "Project Code", "type": "string", "width": 20},
            {"header": "Project Title", "type": "string", "width": 40},
            {"header": "Project Budget", "type": "string", "width": 20},
            {"header": "Project Currency", "type": "string", "width": 20},
            {"header": "Project HRP Code", "type": "string", "width": 40},
            {"header": "Project Start Date", "type": "string", "width": 20},
            {"header": "Project End Date", "type": "string", "width": 20},
            {"header": "Cluster", "type": "string", "width": 20},
            {"header": "Focal Person Name", "type": "string", "width": 20},
            {"header": "Focal Person Phone", "type": "string", "width": 20},
            {"header": "Focal Person Email", "type": "string", "width": 40},
            {"header": "Implementing Partners", "type": "string", "width": 50},
            {"header": "Donors", "type": "string", "width": 40},
            {"header": "Benificiary", "type": "string", "width": 20},
            {"header": "Benificiary Category", "type": "string", "width": 20},
            {"header": "Response Types", "type": "string", "width": 20},
            {"header": "Activity Domain", "type": "string", "width": 60},
            {"header": "Activity Type", "type": "string", "width": 60},
            # {"header": "Activity Detail", "type": "string", "width": 40},
            {"header": "Indicator", "type": "string", "width": 60},
            {"header": "Province", "type": "string", "width": 20},
            {"header": "District", "type": "string", "width": 20},
            {"header": "Facility Site Type", "type": "string", "width": 20},
            {"header": "Facility Site Name", "type": "string", "width": 20},
            {"header": "Facility Site ID", "type": "string", "width": 20},
            # {"header": "Zone", "type": "string", "width": 20},
            {"header": "Location Type", "type": "string", "width": 20},
        ]

        disaggregation_cols = []
        disaggregations = Disaggregation.objects.all()
        disaggregation_list = []

        for disaggregation in disaggregations:
            if disaggregation.name not in disaggregation_list:
                disaggregation_list.append(disaggregation.name)
                disaggregation_cols.append({"header": disaggregation.name, "type": "string", "width": 20})
            else:
                continue

        if disaggregations:
            for disaggregation_col in disaggregation_cols:
                columns.append(disaggregation_col)

        self.write_sheet_columns(sheet, columns)
        self.write_project_report_data_rows(sheet, project_reports, columns, disaggregation_list)

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

    def write_project_report_data_rows(self, sheet, project_reports, columns, disaggregation_list):
        """
        Write project data rows to the sheet.

        Args:
            sheet (Worksheet): The worksheet object.
            project_reports (Project Report): The project_reports objects.
        """
        rows = []

        try:
            for report in project_reports:
                plan_reports = report.activityplanreport_set.all()
                for plan_report in plan_reports:
                    location_reports = plan_report.targetlocationreport_set.all()
                    for location_report in location_reports:
                        # Create a dictionary to hold disaggregation data
                        disaggregation_data = {}
                        row = [
                            report.__str__(),
                            report.get_state_display(),
                            report.report_date.strftime("%B"),
                            report.report_date.strftime("%Y"),
                            report.report_date.strftime("%Y-%m-%d"),
                            report.project.code,
                            report.project.title,
                            report.project.budget,
                            report.project.budget_currency.name if report.project.budget_currency else None,
                            report.project.hrp_code,
                            report.project.start_date.strftime("%Y-%m-%d"),
                            report.project.end_date.strftime("%Y-%m-%d"),
                            ", ".join(str(cluster.title) for cluster in report.project.clusters.all())
                            if report.project.clusters
                            else None,
                            report.project.user.profile.name
                            if report.project.user and report.project.user.profile
                            else None,
                            report.project.user.profile.phone
                            if report.project.user and report.project.user.profile
                            else None,
                            report.project.user.email if report.project.user else None,
                            ", ".join(str(partner.name) for partner in report.project.implementing_partners.all())
                            if report.project.implementing_partners
                            else None,
                            ", ".join(str(donor.name) for donor in report.project.donors.all())
                            if report.project.donors
                            else None,
                            plan_report.activity_plan.beneficiary.name
                            if plan_report.activity_plan.beneficiary
                            else None,
                            plan_report.activity_plan.get_beneficiary_category_display(),
                            ", ".join(str(report_type.name) for report_type in plan_report.report_types.all())
                            if plan_report.report_types
                            else None,
                            plan_report.activity_plan.activity_domain.name,
                            plan_report.activity_plan.activity_type.name,
                            # plan_report.activity_plan.activity_detail.name if plan_report.activity_plan.activity_detail else None,
                            plan_report.activity_plan.indicator.name if plan_report.activity_plan.indicator else None,
                            location_report.province.name if location_report.province else None,
                            location_report.district.name if location_report.district else None,
                            location_report.facility_site_type.name if location_report.facility_site_type else None,
                            location_report.facility_name,
                            location_report.facility_id,
                            # location_report.zone.name if location_report.zone else None,
                            location_report.location_type.name if location_report.location_type else None,
                        ]

                        # Iterate through disaggregation locations and get disaggregation values
                        disaggregation_locations = location_report.disaggregationlocationreport_set.all()
                        disaggregation_location_list = {
                            disaggregation_location.disaggregation.name: disaggregation_location.target
                            for disaggregation_location in disaggregation_locations
                        }

                        # Update disaggregation_data with values from disaggregation_location_list
                        for disaggregation_entry in disaggregation_list:
                            if disaggregation_entry not in disaggregation_location_list:
                                disaggregation_data[disaggregation_entry] = None

                        disaggregation_location_list.update(disaggregation_data)

                        # Append disaggregation values to the row in the order of columns
                        for column in columns:
                            header = column["header"]
                            if header in disaggregation_location_list:
                                row.append(disaggregation_location_list[header])

                        # Add row to the list of rows
                        rows.append(row)

            for row_idx, row in enumerate(rows, start=2):
                for col_idx, value in enumerate(row, start=1):
                    try:
                        sheet.cell(row=row_idx, column=col_idx, value=value)
                    except Exception as e:
                        print("Error:", e)

            # Correct syntax to freeze panes
            sheet.freeze_panes = "A2"

        except Exception as e:
            print("Error:", e)
