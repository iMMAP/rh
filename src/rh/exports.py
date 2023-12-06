import base64
import datetime
from io import BytesIO
import json

from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from openpyxl import Workbook
from openpyxl.styles import Font, NamedStyle
from openpyxl.utils import get_column_letter


from .models import (
    Project,
)

#############################################
############### Export Views #################
#############################################

# Define the header style
header_style = NamedStyle(name="header")
header_style.font = Font(bold=True)


class ProjectExportExcelView(View):
    """
    View class for exporting project data to Excel.
    """

    def post(self, request, project_id):
        """
        Handle POST request to export project data to Excel.

        Args:
            request (HttpRequest): The HTTP request object.
            project_id (int): The ID of the project.

        Returns:
            JsonResponse: The JSON response containing the file URL and name, or an error message.
        """
        try:
            project = Project.objects.get(id=project_id)  # Get the project object

            workbook = Workbook()

            self.write_project_sheet(workbook, project)
            self.write_population_sheet(workbook, project)
            self.write_target_locations_sheet(workbook, project)
            self.write_budget_progress_sheet(workbook, project)

            excel_file = BytesIO()
            workbook.save(excel_file)
            excel_file.seek(0)

            response = {
                "file_url": "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,"
                + base64.b64encode(excel_file.read()).decode("utf-8"),
                "file_name": "export.xlsx",
            }

            return JsonResponse(response)
        except Exception as e:
            response = {"error": str(e)}
            return JsonResponse(response, status=500)

    def write_project_sheet(self, workbook, project):
        """
        Write the project sheet to the workbook.

        Args:
            workbook (Workbook): The Excel workbook object.
            project (Project): The project object.
        """
        sheet = workbook.active
        sheet.title = "Project"

        # Define column headers and types
        columns = [
            {"header": "Project Title", "type": "string", "width": 40},
            {"header": "Code", "type": "string", "width": 20},
            {"header": "Focal Person", "type": "string", "width": 20},
            {"header": "Email", "type": "string", "width": 25},
            {"header": "Project Description", "type": "string", "width": 50},
            {"header": "Organization", "type": "string", "width": 40},
            {"header": "Organization Type", "type": "string", "width": 40},
            {"header": "Cluster", "type": "string", "width": 50},
            {"header": "HRP Project Code", "type": "string", "width": 20},
            {"header": "Project Start Date", "type": "date", "width": 20},
            {"header": "Project End Date", "type": "date", "width": 20},
            {"header": "Project Budget", "type": "float", "width": 10},
            {"header": "Budget Received", "type": "float", "width": 10},
            {"header": "Budget Gap", "type": "float", "width": 10},
            {"header": "Project Budget Currency", "type": "string", "width": 10},
            {"header": "Project Donors", "type": "string", "width": 30},
            {"header": "Implementing Partners", "type": "string", "width": 30},
            {"header": "Programme Partners", "type": "string", "width": 30},
            {"header": "Status", "type": "string", "width": 10},
            {"header": "Activity Domain", "type": "string", "width": 50},
            # {'header': 'Activity Type', 'type': 'string', 'width': 50},
            # {'header': 'Activity Detail', 'type': 'string', 'width': 50},
            # {'header': 'Indicators', 'type': 'string', 'width': 50},
            # {'header': 'Beneficiary', 'type': 'string', 'width': 50},
            # {'header': 'Beneficiary Catagory', 'type': 'string', 'width': 50},
            # {'header': 'Province', 'type': 'string', 'width': 50},
            # {'header': 'District', 'type': 'string', 'width': 50},
            # {'header': 'Word/Zone', 'type': 'string', 'width': 50},
        ]

        self.write_sheet_columns(sheet, columns)
        self.write_project_data_rows(sheet, project)

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

    def write_project_data_rows(self, sheet, project):
        """
        Write project data rows to the sheet.

        Args:
            sheet (Worksheet): The worksheet object.
            project (Project): The project object.
        """

        row = [
            project.title,
            project.code,
            project.user.username,
            project.user.email,
            project.description,
            project.user.profile.organization.code,
            project.user.profile.organization.type,
            ", ".join([clusters.name for clusters in project.clusters.all()]),
            project.hrp_code,
            project.start_date.astimezone(timezone.utc).replace(tzinfo=None) if project.start_date else None,
            project.end_date.astimezone(timezone.utc).replace(tzinfo=None) if project.end_date else None,
            project.budget,
            project.budget_received,
            project.budget_gap,
            project.budget_currency.name,
            ", ".join([donor.name for donor in project.donors.all()]),
            ", ".join([implementing_partner.code for implementing_partner in project.implementing_partners.all()]),
            ", ".join([programme_partner.code for programme_partner in project.programme_partners.all()]),
            project.state,
            ", ".join([ActivityDomain.name for ActivityDomain in project.activity_domains.all()]),
            # ', '.join([ActivityPlan.activity_type for ActivityPlan in project.activity_type.all()]),
        ]

        for col_idx, value in enumerate(row, start=1):
            sheet.cell(row=2, column=col_idx, value=value)

        sheet.freeze_panes = sheet["A2"]

    def write_population_sheet(self, workbook, project):
        """
        Write the population sheet to the workbook.

        Args:
            workbook (Workbook): The Excel workbook object.
            project (Project): The project object.
        """
        sheet = workbook.create_sheet(title="Target Population")

        # Define column headers and types for Sheet 2
        columns = [
            {"header": "Activity Domain", "type": "string", "width": 20},
            {"header": "Activity Type", "type": "string", "width": 20},
            {"header": "Activity Detail", "type": "string", "width": 20},
            {"header": "Indicators", "type": "string", "width": 40},
        ]

        self.write_sheet_columns(sheet, columns)
        self.write_population_data_rows(sheet, project)

        sheet.freeze_panes = sheet["A2"]

    def write_population_data_rows(self, sheet, project):
        """
        Write population data rows to the sheet.plan.activity_detail.name if plan.activity_detail else None,
                # "\n".join([indicator.name for indicator in plan.indicators.all()]),

        Args:
            sheet (Worksheet): The worksheet object.
            project (Project): The project object.
        """
        activity_plans = project.activityplan_set.all()
        for plan in activity_plans:
            row = [
                plan.activity_domain.name if plan.activity_domain else None,
                plan.activity_type.name if plan.activity_type else None,
                plan.activity_detail.name if plan.activity_detail else None,
                "\n".join([indicator.name for indicator in plan.indicators.all()]),
            ]

            for col_idx, value in enumerate(row, start=1):
                sheet.cell(row=2, column=col_idx, value=value)

    def write_target_locations_sheet(self, workbook, project):
        """
        Write the target locations sheet to the workbook.

        Args:
            workbook (Workbook): The Excel workbook object.
            project (Project): The project object.
        """

        sheet = workbook.create_sheet(title="Target Locations")

        # Define column headers and types for Sheet 3
        columns = [
            {"header": "Province", "type": "string", "width": 20},
            {"header": "District", "type": "string", "width": 20},
            {"header": "Zone/Ward", "type": "string", "width": 20},
        ]

        self.write_sheet_columns(sheet, columns)
        self.write_target_locations_data_rows(sheet, project)

        sheet.freeze_panes = sheet["A2"]

    def write_target_locations_data_rows(self, sheet, project):
        """
        Write target locations data rows to the sheet.

        Args:
            sheet (Worksheet): The worksheet object.
            project (Project): The project object.
        """
        target_locations = project.targetlocation_set.all()
        for location in target_locations:
            row = [
                location.province.name,
                location.district.name,
                location.zone.name if location.zone else None,
            ]

            for col_idx, value in enumerate(row, start=1):
                sheet.cell(row=2, column=col_idx, value=value)

    def write_budget_progress_sheet(self, workbook, project):
        """
        Write the target locations sheet to the workbook.

        Args:
            workbook (Workbook): The Excel workbook object.
            project (Project): The project object.
        """
        sheet = workbook.create_sheet(title="Budget Progress")

        # Define column headers and types for Sheet 3
        columns = [
            {"header": "Project", "type": "string", "width": 20},
            {"header": "Title", "type": "string", "width": 20},
            {"header": "Donor", "type": "string", "width": 20},
            {"header": "Activity Domain", "type": "string", "width": 20},
            {"header": "Grant", "type": "float", "width": 10},
            {"header": "Amount Recieved", "type": "float", "width": 10},
            {"header": "Budget Currency", "type": "string", "width": 20},
            {"header": "Received Date", "type": "date", "width": 20},
            {"header": "Country", "type": "string", "width": 20},
            {"header": "Description", "type": "string", "width": 20},
        ]

        self.write_sheet_columns(sheet, columns)
        self.write_budget_progress_data_rows(sheet, project)

        sheet.freeze_panes = sheet["A2"]

    def write_budget_progress_data_rows(self, sheet, project):
        """
        Write budget progress data rows to the sheet.

        Args:
            sheet (Worksheet): The worksheet object.
            project (Project): The project object.
        """
        budget_progress = project.budgetprogress_set.all()
        for budget in budget_progress:
            row = [
                budget.project.name,
                budget.title,
                budget.donor.name,
                budget.activity_domain.name,
                budget.grant,
                budget.amount_recieved,
                budget.budget_currency.name,
                budget.received_date,
                budget.country.name,
                budget.description,
            ]

            for col_idx, value in enumerate(row, start=1):
                sheet.cell(row=2, column=col_idx, value=value)


class ProjectFilterExportView(View):
    def post(self, request, projectId):
        project = Project.objects.get(id=projectId)

        try:
            selectedData = json.loads(request.POST.get("exportData"))
            i = 0
            projectFields = []
            for keys, values in selectedData.items():
                if not isinstance(values, list):
                    projectFields.insert(i, keys)
                    i += 1
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Project"
            # defining columns

            columns = []
            for keys, values in selectedData.items():
                columns += ({"header": keys, "type": "string", "width": 20},)

            for idx, column in enumerate(columns, start=1):
                cell = sheet.cell(row=1, column=idx, value=column["header"])
                cell.style = header_style

                column_letter = get_column_letter(idx)
                if column["type"] == "number":
                    sheet.column_dimensions[column_letter].number_format = "General"
                elif column["type"] == "date":
                    sheet.column_dimensions[column_letter].number_format = "mm-dd-yyyy"

                sheet.column_dimensions[column_letter].width = column["width"]
            row = []
            # retriving data from database accordeing to selected field by user and defining rows
            try:
                if len(selectedData["focal_point"]) > 0:
                    row += (project.user.username,)
            except Exception:
                pass
            try:
                if len(projectFields) > 0:
                    selected_feild = Project.objects.values_list(*projectFields).get(id=projectId)
                    for field in selected_feild:
                        if isinstance(field, datetime.datetime):
                            row += (field.astimezone(timezone.utc).replace(tzinfo=None),)
                        else:
                            row += (field,)
                else:
                    pass
            except Exception:
                pass

            try:
                if len(selectedData["currency"]) > 0:
                    row += (project.budget_currency.name,)
            except Exception:
                pass
            try:
                donorData = project.donors.values_list("name", flat=True).filter(id__in=selectedData["donors"])
                row += (",".join([donor for donor in donorData]),)
            except Exception:
                pass
            try:
                clusterData = project.clusters.values_list("title", flat=True).filter(id__in=selectedData["clusters"])
                row += (",".join([cluster for cluster in clusterData]),)
            except Exception:
                pass

            try:
                implementingPartner = project.implementing_partners.values_list("code", flat=True).filter(
                    id__in=selectedData["implementing_partners"]
                )
                row += (",".join([implement for implement in implementingPartner]),)
            except Exception:
                pass
            try:
                programPartner = project.programme_partners.values_list("code", flat=True).filter(
                    id__in=selectedData["programme_partners"]
                )
                row += (",".join([program for program in programPartner]),)
            except Exception:
                pass

            activity_plans = project.activityplan_set.all()
            try:
                row += (
                    ",".join(
                        [
                            plan.activity_domain.name
                            for plan in activity_plans
                            if plan.activity_domain.name in selectedData["activity_domain"]
                        ]
                    ),
                )
            except Exception:
                pass

            try:
                row += (
                    ",".join(
                        [
                            plan.activity_type.name
                            for plan in activity_plans
                            if plan.activity_type.name in selectedData["activity_type"]
                        ]
                    ),
                )
            except Exception:
                pass

            try:
                row += (
                    ",".join(
                        [
                            plan.activity_detail.name
                            for plan in activity_plans
                            if plan.activity_detail.name in selectedData["activity_detail"]
                        ]
                    ),
                )
            except Exception:
                pass

            try:
                inds = []
                for plan in activity_plans:
                    for indicator in plan.indicators.all():
                        if indicator.name in selectedData["indicator"]:
                            value = str(indicator.name)
                            inds += (",".join([value]),)
                row += (",".join([i for i in inds]),)
            except Exception:
                pass

            try:
                row += (",".join([ben.name for ben in activity_plans if ben.name in selectedData["beneficiary"]]),)
            except Exception:
                pass
            try:
                row += (",".join([b_category for b_category in selectedData["beneficiary_category"]]),)
            except Exception:
                pass
            try:
                row += (
                    ",".join(
                        [desc.name for desc in activity_plans if desc.name in selectedData["activity_description"]]
                    ),
                )
            except Exception:
                pass
            # # Target location
            targetLocation = project.targetlocation_set.all()

            try:
                row += (
                    ",".join(
                        [
                            target.province.name
                            for target in targetLocation
                            if target.province.name in selectedData["province"]
                        ]
                    ),
                )
            except Exception:
                pass
            try:
                row += (
                    ",".join(
                        [
                            target.district.name
                            for target in targetLocation
                            if target.district.name in selectedData["district"]
                        ]
                    ),
                )
            except Exception:
                pass
            try:
                row += (
                    ",".join(
                        [
                            target.location_type.name
                            for target in targetLocation
                            if target.location_type.name in selectedData["location_type"]
                        ]
                    ),
                )
            except Exception:
                pass
            try:
                row += (
                    ",".join(
                        [target.site_name for target in targetLocation if target.site_name in selectedData["site_name"]]
                    ),
                )
            except Exception:
                pass
            try:
                row += (
                    ",".join(
                        [
                            target.site_lat
                            for target in targetLocation
                            if target.site_lat in selectedData["site_latitude"]
                        ]
                    ),
                )
            except Exception:
                pass
            try:
                row += (
                    ",".join(
                        [
                            target.site_long
                            for target in targetLocation
                            if target.site_long in selectedData["site_longitude"]
                        ]
                    ),
                )
            except Exception:
                pass

            for col_idx, value in enumerate(row, start=1):
                sheet.cell(row=2, column=col_idx, value=value)

            sheet.freeze_panes = sheet["A2"]
            excel_file = BytesIO()
            workbook.save(excel_file)
            excel_file.seek(0)

            response = {
                "file_url": "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,"
                + base64.b64encode(excel_file.read()).decode("utf-8"),
                "file_name": "export.xlsx",
            }

            return JsonResponse(response)
        except Exception as e:
            response = {"error": str(e)}
        return JsonResponse(response, status=500)
