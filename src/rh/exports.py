import base64
import datetime
import json
from io import BytesIO

from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from openpyxl import Workbook
from openpyxl.styles import Font, NamedStyle
from openpyxl.utils import get_column_letter

from .models import Disaggregation, Project

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
            {"header": "Project End Date", "type": "date", "width": 30},
            {"header": "Project Budget", "type": "float", "width": 20},
            {"header": "Budget Received", "type": "float", "width": 20},
            {"header": "Budget Gap", "type": "float", "width": 20},
            {"header": "Project Budget Currency", "type": "string", "width": 20},
            {"header": "Project Donors", "type": "string", "width": 30},
            {"header": "Implementing Partners", "type": "string", "width": 30},
            {"header": "Programme Partners", "type": "string", "width": 30},
            {"header": "Status", "type": "string", "width": 10},
            {"header": "Activity Domain", "type": "string", "width": 50},
            {"header": "Activity Type", "type": "string", "width": 20},
            {"header": "Activity Detail", "type": "string", "width": 20},
            {"header": "Indicators", "type": "string", "width": 40},
            {"header": "admin1pcode", "type": "string", "width": 20},
            {"header": "admin1name", "type": "string", "width": 20},
            {"header": "region", "type": "string", "width": 20},
            {"header": "admin2pcode", "type": "string", "width": 20},
            {"header": "admin2name", "type": "string", "width": 20},
            {"header": "Zone/Ward", "type": "string", "width": 20},
        ]

        disaggregation_cols = []
        disaggregations = Disaggregation.objects.all()
        disaggregation_list = []

        for disaggregation in disaggregations:
            if disaggregation.name not in disaggregation_list:
                disaggregation_list.append(disaggregation.name)
                disaggregation_cols.append({"header": disaggregation.name, "type": "string", "width": 30})
            else:
                continue

        if disaggregations:
            for disaggregation_col in disaggregation_cols:
                columns.append(disaggregation_col)

        self.write_sheet_columns(sheet, columns)
        self.write_project_data_rows(sheet, project, columns, disaggregation_list)

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

    def write_project_data_rows(self, sheet, project, columns, disaggregation_list):
        """
        Write project data rows to the sheet.

        Args:
            sheet (Worksheet): The worksheet object.
            project (Project): The project object.
        """
        rows = []
        try:
            plans = project.activityplan_set.all()
            for plan in plans:
                locations = plan.targetlocation_set.all()
                for location in locations:
                    # Create a dictionary to hold disaggregation data
                    disaggregation_data = {}

                    row = [
                        project.title,
                        project.code,
                        project.user.username if project.user else None,
                        project.user.email if project.user else None,
                        project.description,
                        project.user.profile.organization.code
                        if project.user and project.user.profile and project.user.profile.organization
                        else None,
                        project.user.profile.organization.type
                        if project.user and project.user.profile and project.user.profile.organization
                        else None,
                        ", ".join([clusters.name for clusters in project.clusters.all()]),
                        project.hrp_code,
                        project.start_date.astimezone(timezone.utc).replace(tzinfo=None)
                        if project.start_date
                        else None,
                        project.end_date.astimezone(timezone.utc).replace(tzinfo=None) if project.end_date else None,
                        project.budget,
                        project.budget_received,
                        project.budget_gap,
                        project.budget_currency.name if project.budget_currency else None,
                        ", ".join([donor.name for donor in project.donors.all()]),
                        ", ".join(
                            [implementing_partner.code for implementing_partner in project.implementing_partners.all()]
                        ),
                        ", ".join([programme_partner.code for programme_partner in project.programme_partners.all()]),
                        project.state,
                        plan.activity_domain.name if plan.activity_domain else None,
                        plan.activity_type.name if plan.activity_type else None,
                        plan.activity_detail.name if plan.activity_detail else None,
                        plan.indicator.name if plan.indicator else None,
                        location.province.code if location.province else None,
                        location.province.name if location.province else None,
                        location.province.region_name if location.province else None,
                        location.district.code if location.district else None,
                        location.district.name if location.district else None,
                        location.zone.name if location.zone else None,
                    ]
                    # Iterate through disaggregation locations and get disaggregation values
                    disaggregation_locations = location.disaggregationlocation_set.all()
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
            print(projectFields)
            try:
                projectFields.remove("admin1pcode")
                projectFields.remove("admin2pcode")
            except Exception:
                pass
            
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Project"
            # defining columns
            columns = []
            for keys, values in selectedData.items():
                if not keys == "disaggregation":
                    columns += ({"header": keys, "type": "string", "width": 20},)
            try:
                if selectedData['disaggregation']:
                    disaggregation_cols = []
                    disaggregations = Disaggregation.objects.all()
                    disaggregation_list = []
                    for disaggregation in disaggregations:
                        if disaggregation.name not in disaggregation_list:
                            disaggregation_list.append(disaggregation.name)
                            disaggregation_cols.append({"header": disaggregation.name, "type": "string", "width": 30})
                        else:
                            continue
                    if disaggregations:
                        for disaggregation_col in disaggregation_cols:
                            columns.append(disaggregation_col)
            except Exception:
                pass
                  
            # adding disaggregation column if it is selected for export

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
            #fetching the selected data from table
            project_planning_rows = []
            try:
                if len(selectedData["focal_point"]) > 0:
                    project_planning_rows += (project.user.username,)
            except Exception:
                pass
            try:
                if len(projectFields) > 0:
                    selected_feild = Project.objects.values_list(*projectFields).get(id=projectId)
                    for field in selected_feild:
                        if isinstance(field, datetime.datetime):
                            project_planning_rows.append(field.astimezone(timezone.utc).replace(tzinfo=None),)
                        else:
                            project_planning_rows += (field, )
                else:
                    pass
            except Exception:
                pass
            
            try:
                if len(selectedData["currency"]) > 0:
                    project_planning_rows += (project.budget_currency.name,)
            except Exception:
                pass
            try:
                donorData = project.donors.values_list("name", flat=True).filter(id__in=selectedData["donors"])
                project_planning_rows += (",".join([donor for donor in donorData]),)
            except Exception:
                pass
            try:
                clusterData = project.clusters.values_list("title", flat=True).filter(id__in=selectedData["clusters"])
                project_planning_rows += (",".join([cluster for cluster in clusterData]),)
            except Exception:
                pass

            try:
                implementingPartner = project.implementing_partners.values_list("code", flat=True).filter(
                    id__in=selectedData["implementing_partners"]
                )
                project_planning_rows += (",".join([implement for implement in implementingPartner]),)
            except Exception:
                pass
            try:
                programPartner = project.programme_partners.values_list("code", flat=True).filter(
                    id__in=selectedData["programme_partners"]
                )
                project_planning_rows += (",".join([program for program in programPartner]),)
            except Exception:
                pass
            
            activity_planning_rows = []
            activity_plans = project.activityplan_set.all()
            try:
                activity_planning_rows += (
                    ",".join(
                        [
                            plan.activity_domain.name
                            for plan in activity_plans
                            if str(plan.activity_domain.id) in selectedData["activity_domain"]
                        ]
                    ),
                )
            except Exception:
                pass

            try:
                activity_planning_rows += (
                    ",".join(
                        [
                            plan.activity_type.name
                            for plan in activity_plans
                            if str(plan.activity_type.id) in selectedData["activity_type"]
                        ]
                    ),
                )
            except Exception:
                pass

            try:
                activity_planning_rows += (
                    ",".join(
                        [
                            plan.activity_detail.name
                            for plan in activity_plans
                            if str(plan.activity_detail.id) in selectedData["activity_detail"]
                        ]
                    ),
                )
            except Exception:
                pass

            try:
                
                activity_planning_rows += (
                    ",".join(
                        [
                            plan.indicator.name
                            for plan in activity_plans 
                            if str(plan.indicator.id) in selectedData['indicator']
                        ]
                    ),
                )
            except Exception:
                pass
            
            try:
                activity_planning_rows += (
                    ",".join(
                        [
                            ben.beneficiary.name 
                            for ben in activity_plans
                            if str(ben.beneficiary.id) in selectedData["beneficiary"]
                        ]
                    ),
                )
            except Exception:
                pass
            try:
                activity_planning_rows += (",".join([b_category for b_category in selectedData["beneficiary_category"]]),)
            except Exception:
                pass
            try:
                activity_planning_rows += (
                    ",".join(
                        [
                            plan.description 
                            for plan in activity_plans 
                            if str(plan.id) in selectedData["activity_description"]
                        ]
                    ),
                )
            except Exception:
                pass
            target_location_rows = []
            # # Target location
            targetLocation = project.targetlocation_set.all()

            try:
                target_location_rows += (
                    ",".join(
                        [
                            target.province.name
                            for target in targetLocation
                            if str(target.province.id) in selectedData["admin1name"]
                        ]
                    ),
                )
            except Exception:
                pass
            try:
                target_location_rows += (
                    ",".join(
                        [
                            target.province.code
                            for target in targetLocation
                            if str(target.province.id) in selectedData["admin1name"]
                        ]
                    ),
                )
            except Exception:
                pass
            try:
                target_location_rows += (
                    ",".join(
                        [
                            target.district.name
                            for target in targetLocation
                            if str(target.district.id) in selectedData["admin2name"]
                        ]
                    ),
                )
            except Exception:
                pass
            try:
                target_location_rows += (
                    ",".join(
                        [
                            target.district.code
                            for target in targetLocation
                            if str(target.district.id) in selectedData["admin2name"]
                        ]
                    ),
                )
            except Exception:
                pass
            try:
                target_location_rows += (
                    ",".join(
                        [
                            target.location_type.name
                            for target in targetLocation
                            if str(target.location_type.id) in selectedData["location_type"]
                        ]
                    ),
                )
            except Exception:
                pass
            try:
                target_location_rows += (
                    ",".join(
                        [
                            target.classification
                            for target in targetLocation
                            if str(target.id) in selectedData["classification"]
                        ]
                    ),
                )
            except Exception:
                pass
            
            # facility monitoring
            try:
                row += (
                    ",".join(
                        [
                            target.facility_monitoring
                            for target in targetLocation
                            if target.facility_monitoring in selectedData["facility_monitoring"]
                        ]
                    ),
                )
            except Exception:
                pass
            try:
                row += (
                    ",".join(
                        [
                            target.facility_id
                            for target in targetLocation
                            if target.location_type.name in selectedData["facility_id"]
                        ]
                    ),
                )
            except Exception:
                pass
            try:
                row += (
                    ",".join(
                        [
                            target.facility_name 
                            for target in targetLocation 
                            if target.facility_name in selectedData["facility_name"]]
                    ),
                )
            except Exception:
                pass
            try:
                row += (
                    ",".join(
                        [
                            target.facility_lat
                            for target in targetLocation
                            if target.site_lat in selectedData["facility_latitude"]
                        ]
                    ),
                )
            except Exception:
                pass
            try:
                row += (
                    ",".join(
                        [
                            target.facility_long
                            for target in targetLocation
                            if target.facility_long in selectedData["facility_longitude"]
                        ]
                    ),
                )
            except Exception:
                pass
            row.extend(project_planning_rows)
            row.extend(activity_planning_rows)
            row.extend(target_location_rows)
            print(project_planning_rows)
           
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
