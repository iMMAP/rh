import base64
import csv
import json
import datetime
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.views import View
from openpyxl import Workbook
from openpyxl.styles import Font, NamedStyle
from openpyxl.utils import get_column_letter
from rh.utils import DateTimeEncoder
from ..models import ActivityPlan, Disaggregation, DisaggregationLocation, Project, TargetLocation
from django.db.models import Prefetch

#############################################
############### Export Views #################
#############################################

# Define the header style
header_style = NamedStyle(name="header")
header_style.font = Font(bold=True)


class ProjectExportExcelView(View):
    def post(self, request, format):
        selected_projects_id = json.loads(request.body)
        user_org = request.user.profile.organization
        projects = (
            Project.objects.select_related("organization", "budget_currency", "user")
            .prefetch_related(
                "implementing_partners",
                "programme_partners",
                "donors",
                "clusters",
                Prefetch(
                    "activityplan_set",
                    queryset=ActivityPlan.objects.prefetch_related(
                        Prefetch(
                            "targetlocation_set",
                            queryset=TargetLocation.objects.prefetch_related(
                                Prefetch(
                                    "disaggregationlocation_set",
                                    queryset=DisaggregationLocation.objects.select_related("disaggregation"),
                                )
                            ),
                        )
                    ),
                ),
            )
            .filter(organization=user_org)
        )

        if selected_projects_id:
            projects = projects.filter(id__in=selected_projects_id)

        try:
            # selectedData = json.loads(request.POST.get("exportData"))

            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Project"

            # form the filename with today date
            today_date = datetime.date.today()
            # define CSV file
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename='project.csv'"
            writer = csv.writer(response)

            # defining columns
            columns = [
                {"header": "Project Title", "type": "string", "width": 40},
                {"header": "Code", "type": "string", "width": 20},
                {"header": "Focal Person", "type": "string", "width": 20},
                {"header": "Email", "type": "string", "width": 25},
                {"header": "Organization", "type": "string", "width": 40},
                {"header": "Organization Type", "type": "string", "width": 40},
                {"header": "Project Description", "type": "string", "width": 50},
                {"header": "Cluster", "type": "string", "width": 50},
                {"header": "HRP project", "type": "string", "width": 50},
                {"header": "Project HRP Code", "type": "string", "width": 20},
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
                {"header": "Beneficiary", "type": "string", "width": 40},
                {"header": "HRP Beneficiary", "type": "string", "width": 40},
                {"header": "Beneficiary category", "type": "string", "width": 40},
                {"header": "Activity description", "type": "string", "width": 40},
                {"header": "Package Type", "type": "string", "width": 20},
                {"header": "Unit Type", "type": "string", "width": 20},
                {"header": "Grant Type", "type": "string", "width": 20},
                {"header": "Transfer Category", "type": "string", "width": 20},
                {"header": "Currency", "type": "string", "width": 20},
                {"header": "Transfer mechanism type", "type": "string", "width": 20},
                {"header": "implement modility type", "type": "string", "width": 20},
                {"header": "admin0code", "type": "string", "width": 20},
                {"header": "admin0name", "type": "string", "width": 20},
                {"header": "admin1pcode", "type": "string", "width": 20},
                {"header": "admin1name", "type": "string", "width": 20},
                {"header": "region", "type": "string", "width": 20},
                {"header": "admin2pcode", "type": "string", "width": 20},
                {"header": "admin2name", "type": "string", "width": 20},
                {"header": "NHS Code", "type": "string", "width": 20},
                {"header": "classification", "type": "string", "width": 20},
                {"header": "Zone/Ward", "type": "string", "width": 20},
                {"header": "facility site type", "type": "string", "width": 20},
                {"header": "facility monitoring", "type": "string", "width": 20},
                {"header": "facility name", "type": "string", "width": 20},
                {"header": "facility id", "type": "string", "width": 20},
                {"header": "facility/site latitude", "type": "string", "width": 20},
                {"header": "facility/site longitude", "type": "string", "width": 20},
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

            for idx, column in enumerate(columns, start=1):
                cell = sheet.cell(row=1, column=idx, value=column["header"])
                cell.style = header_style

                column_letter = get_column_letter(idx)
                if column["type"] == "number":
                    sheet.column_dimensions[column_letter].number_format = "General"
                elif column["type"] == "date":
                    sheet.column_dimensions[column_letter].number_format = "mm-dd-yyyy"

                sheet.column_dimensions[column_letter].width = column["width"]

            # defining the csv header file
            if format == "csv":
                header_list = []
                for item in columns:
                    header_list.append(item["header"])
                writer.writerow(header_list)

            # defining rows
            rows = []
            for project in projects:
                disaggregation_data = {}
                # check the selectedData if the field exist in the list then add to the row otherwise set it None
                row = [
                    project.title,
                    project.code,
                    project.user.username,
                    project.user.email,
                    project.user.profile.organization.code
                    if project.user and project.user.profile and project.user.profile.organization
                    else None,
                    project.user.profile.organization.type
                    if project.user and project.user.profile and project.user.profile.organization
                    else None,
                    project.description if project.description else None,
                    ", ".join([clusters.code for clusters in project.clusters.all()]),
                    "yes" if project.is_hrp_project == 1 else None,
                    project.hrp_code if project.hrp_code else None,
                    project.start_date.astimezone(datetime.timezone.utc).replace(tzinfo=None),
                    project.end_date.astimezone(datetime.timezone.utc).replace(tzinfo=None),
                    project.budget if project.budget else None,
                    project.budget_received if project.budget_received else None,
                    project.budget_gap if project.budget_gap else None,
                    project.budget_currency.name if project.budget_currency else None,
                    ", ".join([donor.name for donor in project.donors.all()]),
                    ", ".join(
                        [implementing_partner.code for implementing_partner in project.implementing_partners.all()]
                    ),
                    ", ".join([programme_partner.code for programme_partner in project.programme_partners.all()]),
                    project.state,
                ]
                plans = project.activityplan_set.all()
                activityplan_row = [
                    ", ".join([plan.activity_domain.name for plan in plans if plan.activity_domain]),
                    ", ".join([plan.activity_type.name for plan in plans if plan.activity_type]),
                    ", ".join([plan.activity_detail.name for plan in plans if plan.activity_detail]),
                    ", ".join([plan.indicator.name for plan in plans if plan.indicator]),
                    ", ".join([plan.beneficiary.name for plan in plans if plan.beneficiary]),
                    ", ".join([plan.hrp_beneficiary.name for plan in plans if plan.hrp_beneficiary]),
                    ", ".join([plan.beneficiary_category for plan in plans if plan.beneficiary_category]),
                    ", ".join([plan.description for plan in plans if plan.description]),
                    ", ".join([str(plan.package_type) for plan in plans if plan.package_type]),
                    ", ".join([str(plan.unit_type) for plan in plans if plan.unit_type]),
                    ", ".join([str(plan.grant_type) for plan in plans if plan.grant_type]),
                    ", ".join([str(plan.transfer_category) for plan in plans if plan.transfer_category]),
                    ", ".join([plan.currency.name for plan in plans if plan.currency]),
                    ", ".join([str(plan.transfer_mechanism_type) for plan in plans if plan.transfer_mechanism_type]),
                    ", ".join([str(plan.implement_modility_type) for plan in plans if plan.implement_modility_type]),
                    ", ".join(
                        [
                            location.country.code
                            for plan in plans
                            for location in plan.targetlocation_set.all()
                            if location.province
                        ]
                    ),
                    ", ".join(
                        [
                            location.country.name
                            for plan in plans
                            for location in plan.targetlocation_set.all()
                            if location.province
                        ]
                    ),
                    ", ".join(
                        [
                            location.province.code
                            for plan in plans
                            for location in plan.targetlocation_set.all()
                            if location.province
                        ]
                    ),
                    ", ".join(
                        [
                            location.province.name
                            for plan in plans
                            for location in plan.targetlocation_set.all()
                            if location.province
                        ]
                    ),
                    ", ".join(
                        [
                            location.province.region_name
                            for plan in plans
                            for location in plan.targetlocation_set.all()
                            if location.province
                        ]
                    ),
                    ", ".join(
                        [
                            location.district.code
                            for plan in plans
                            for location in plan.targetlocation_set.all()
                            if location.district
                        ]
                    ),
                    ", ".join(
                        [
                            location.district.name
                            for plan in plans
                            for location in plan.targetlocation_set.all()
                            if location.district
                        ]
                    ),
                    ", ".join(
                        [
                            location.nhs_code
                            for plan in plans
                            for location in plan.targetlocation_set.all()
                            if location.nhs_code
                        ]
                    ),
                    ", ".join(
                        [
                            location.location_type
                            for plan in plans
                            for location in plan.targetlocation_set.all()
                            if location.location_type
                        ]
                    ),
                    ", ".join(
                        [
                            location.zone.name
                            for plan in plans
                            for location in plan.targetlocation_set.all()
                            if location.zone
                        ]
                    ),
                    ", ".join(
                        [
                            location.facility_site_type.name
                            for plan in plans
                            for location in plan.targetlocation_set.all()
                            if location.facility_site_type
                        ]
                    ),
                    ", ".join(
                        [
                            "yes"
                            for plan in plans
                            for location in plan.targetlocation_set.all()
                            if location.facility_monitoring
                        ]
                    ),
                    ", ".join(
                        [
                            location.facility_name
                            for plan in plans
                            for location in plan.targetlocation_set.all()
                            if location.facility_name
                        ]
                    ),
                    ", ".join(
                        [
                            location.facility_id
                            for plan in plans
                            for location in plan.targetlocation_set.all()
                            if location.facility_id
                        ]
                    ),
                    ", ".join(
                        [
                            str(location.facility_lat)
                            for plan in plans
                            for location in plan.targetlocation_set.all()
                            if location.facility_lat
                        ]
                    ),
                    ", ".join(
                        [
                            str(location.facility_long)
                            for plan in plans
                            for location in plan.targetlocation_set.all()
                            if location.facility_long
                        ]
                    ),
                ]
                row = row + activityplan_row
                # Iterate through disaggregation locations and get disaggregation values
                # for plan in plans:
                #     for location in plan.targetlocation_set.all():
                #         disaggregation_locations = location.disaggregationlocation_set.all()
                #         disaggregation_location_list = {
                #             disaggregation_location.disaggregation.name: disaggregation_location.target
                #             for disaggregation_location in disaggregation_locations
                #         }

                new_disaggregation_location_list = {}
                for plan in plans:
                    for location in plan.targetlocation_set.all():
                        for dl in location.disaggregationlocation_set.all():
                            if dl.disaggregation.name in new_disaggregation_location_list:
                                new_disaggregation_location_list[dl.disaggregation.name] += f", {str(dl.target)}"
                            else:
                                new_disaggregation_location_list[dl.disaggregation.name] = str(dl.target)

                for disaggregation_entry in disaggregation_list:
                    if disaggregation_entry not in new_disaggregation_location_list:
                        disaggregation_data[disaggregation_entry] = None

                # disaggregation_location_list.update(disaggregation_data)

                # Append disaggregation values to the row in the order of columns
                for column in columns:
                    header = column["header"]
                    if header in new_disaggregation_location_list:
                        row.append(new_disaggregation_location_list[header])

                # Add row to the list of rows
                rows.append(row)

                # write row for CSV file
                writer.writerow(row)

            for row_idx, row in enumerate(rows, start=2):
                for col_idx, value in enumerate(row, start=1):
                    try:
                        sheet.cell(row=row_idx, column=col_idx, value=value)
                    except Exception as e:
                        print("Error:", e)

            sheet.freeze_panes = sheet["A2"]
            excel_file = BytesIO()
            workbook.save(excel_file)
            excel_file.seek(0)
            # form the filename with today date
            today_date = datetime.date.today()
            # check the requested format
            if format == "xls":
                response = {
                    "file_url": "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,"
                    + base64.b64encode(excel_file.read()).decode("utf-8"),
                    "file_name": f"project_bulk_export_{today_date}.xlsx",
                }
                return JsonResponse(response)
            elif format == "csv":
                return response
            elif format == "json":
                # serialize the none serialze data and create dump data
                json_data = json.dumps(rows, cls=DateTimeEncoder, indent=4)

                response = HttpResponse(json_data, content_type="application/json")
                response["Content-Disposition"] = 'attachment; filename="projects.json"'
                return response

        except Exception as e:
            response = {"error": str(e)}
        return JsonResponse(response, status=500)


class ProjectFilterExportView(View):
    def post(self, request, projectId):
        project = Project.objects.get(id=projectId)

        try:
            selectedData = json.loads(request.POST.get("exportData"))

            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Project"

            # form the filename with today date
            today_date = datetime.date.today()
            # define CSV file
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename='project.csv'"
            writer = csv.writer(response)

            # defining columns
            columns = [
                {"header": "Project Title", "type": "string", "width": 40},
                {"header": "Code", "type": "string", "width": 20},
                {"header": "Focal Person", "type": "string", "width": 20},
                {"header": "Email", "type": "string", "width": 25},
                {"header": "Organization", "type": "string", "width": 40},
                {"header": "Organization Type", "type": "string", "width": 40},
                {"header": "Project Description", "type": "string", "width": 50},
                {"header": "Cluster", "type": "string", "width": 50},
                {"header": "HRP project", "type": "string", "width": 50},
                {"header": "Project HRP Code", "type": "string", "width": 20},
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
                {"header": "Beneficiary", "type": "string", "width": 40},
                {"header": "HRP Beneficiary", "type": "string", "width": 40},
                {"header": "Beneficiary category", "type": "string", "width": 40},
                {"header": "Activity description", "type": "string", "width": 40},
                {"header": "Package Type", "type": "string", "width": 20},
                {"header": "Unit Type", "type": "string", "width": 20},
                {"header": "Grant Type", "type": "string", "width": 20},
                {"header": "Transfer Category", "type": "string", "width": 20},
                {"header": "Currency", "type": "string", "width": 20},
                {"header": "Transfer mechanism type", "type": "string", "width": 20},
                {"header": "implement modility type", "type": "string", "width": 20},
                {"header": "admin0code", "type": "string", "width": 20},
                {"header": "admin0name", "type": "string", "width": 20},
                {"header": "admin1pcode", "type": "string", "width": 20},
                {"header": "admin1name", "type": "string", "width": 20},
                {"header": "region", "type": "string", "width": 20},
                {"header": "admin2pcode", "type": "string", "width": 20},
                {"header": "admin2name", "type": "string", "width": 20},
                {"header": "NHS Code", "type": "string", "width": 20},
                {"header": "classification", "type": "string", "width": 20},
                {"header": "Zone/Ward", "type": "string", "width": 20},
                {"header": "facility site type", "type": "string", "width": 20},
                {"header": "facility monitoring", "type": "string", "width": 20},
                {"header": "facility name", "type": "string", "width": 20},
                {"header": "facility id", "type": "string", "width": 20},
                {"header": "facility/site latitude", "type": "string", "width": 20},
                {"header": "facility/site longitude", "type": "string", "width": 20},
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

            for idx, column in enumerate(columns, start=1):
                cell = sheet.cell(row=1, column=idx, value=column["header"])
                cell.style = header_style

                column_letter = get_column_letter(idx)
                if column["type"] == "number":
                    sheet.column_dimensions[column_letter].number_format = "General"
                elif column["type"] == "date":
                    sheet.column_dimensions[column_letter].number_format = "mm-dd-yyyy"

                sheet.column_dimensions[column_letter].width = column["width"]

            # defining the csv header file
            if selectedData["format"] == "csv":
                header_list = []
                for item in columns:
                    header_list.append(item["header"])
                writer.writerow(header_list)

            # defining rows
            rows = []
            plans = project.activityplan_set.all()
            for plan in plans:
                locations = plan.targetlocation_set.all()
                for location in locations:
                    # Create a dictionary to hold disaggregation data
                    disaggregation_data = {}
                    # check the selectedData if the field exist in the list then add to the row otherwise set it None
                    row = [
                        project.title if "title" in selectedData else None,
                        project.code if "code" in selectedData else None,
                        project.user.username if "user" in selectedData and project.user else None,
                        project.user.email if "user" in selectedData and project.user else None,
                        project.user.profile.organization.code
                        if project.user
                        and "user" in selectedData
                        and project.user.profile
                        and project.user.profile.organization
                        else None,
                        project.user.profile.organization.type
                        if project.user
                        and "user" in selectedData
                        and project.user.profile
                        and project.user.profile.organization
                        else None,
                        project.description if "pdescription" in selectedData and project.description else None,
                        ", ".join([clusters.code for clusters in project.clusters.all() if "clusters" in selectedData]),
                        "yes" if "is_hrp_project" in selectedData and project.is_hrp_project == 1 else None,
                        project.hrp_code if "hrp_code" in selectedData else None,
                        project.start_date.astimezone(datetime.timezone.utc).replace(tzinfo=None)
                        if "start_date" in selectedData
                        else None,
                        project.end_date.astimezone(datetime.timezone.utc).replace(tzinfo=None)
                        if "end_date" in selectedData
                        else None,
                        project.budget if "budget" in selectedData else None,
                        project.budget_received if "budget_received" in selectedData else None,
                        project.budget_gap if "budget_gap" in selectedData else None,
                        project.budget_currency.name
                        if "budget_currency" in selectedData and project.budget_currency
                        else None,
                        ", ".join([donor.name for donor in project.donors.all() if "donors" in selectedData]),
                        ", ".join(
                            [
                                implementing_partner.code
                                for implementing_partner in project.implementing_partners.all()
                                if "implementing_partners" in selectedData
                            ]
                        ),
                        ", ".join(
                            [
                                programme_partner.code
                                for programme_partner in project.programme_partners.all()
                                if "programme_partners" in selectedData
                            ]
                        ),
                        project.state if "state" in selectedData else None,
                        plan.activity_domain.name
                        if "activity_domain" in selectedData and plan.activity_domain
                        else None,
                        plan.activity_type.name if "activity_type" in selectedData and plan.activity_type else None,
                        plan.activity_detail.name
                        if "activity_detail" in selectedData and plan.activity_detail
                        else None,
                        plan.indicator.name if "indicator" in selectedData and plan.indicator else None,
                        plan.beneficiary.name if "beneficiary" in selectedData and plan.beneficiary else None,
                        plan.hrp_beneficiary.name
                        if "hrp_beneficiary" in selectedData and plan.hrp_beneficiary
                        else None,
                        plan.beneficiary_category
                        if "beneficiary_category" in selectedData and plan.beneficiary_category
                        else None,
                        plan.description if "description" in selectedData and plan.description else None,
                        plan.package_type if "indicator" in selectedData and plan.package_type else None,
                        plan.unit_type if "indicator" in selectedData and plan.unit_type else None,
                        plan.grant_type if "indicator" in selectedData and plan.grant_type else None,
                        plan.transfer_category if "indicator" in selectedData and plan.transfer_category else None,
                        plan.currency if "indicator" in selectedData and plan.currency else None,
                        plan.transfer_mechanism_type
                        if "indicator" in selectedData and plan.transfer_mechanism_type
                        else None,
                        plan.implement_modility_type
                        if "indicator" in selectedData and plan.implement_modility_type
                        else None,
                        location.country.code if "admin0code" in selectedData and location.province else None,
                        location.country.name if "admin0name" in selectedData and location.province else None,
                        location.province.code if "admin1code" in selectedData and location.province else None,
                        location.province.name if "admin1name" in selectedData and location.province else None,
                        location.province.region_name if "admin1code" in selectedData and location.province else None,
                        location.district.code if "admin2code" in selectedData and location.district else None,
                        location.district.name if "admin2name" in selectedData and location.district else None,
                        location.nhs_code if "nhs_code" in selectedData and location.nhs_code else None,
                        location.location_type if "admin1code" in selectedData and location.location_type else None,
                        location.zone.name if location.zone and "admin1code" in selectedData else None,
                        location.facility_site_type
                        if "facility_site_type" in selectedData and location.facility_site_type
                        else None,
                        "Yes" if "facility_monitoring" in selectedData and location.facility_monitoring else None,
                        location.facility_name if "facility_name" in selectedData and location.facility_name else None,
                        location.facility_id if "facility_id" in selectedData and location.facility_id else None,
                        location.facility_lat if "facility_lat" in selectedData and location.facility_lat else None,
                        location.facility_long if "facility_long" in selectedData and location.facility_long else None,
                    ]
                    if "disaggregation" in selectedData:
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

                    # write row for CSV file
                    writer.writerow(row)

            for row_idx, row in enumerate(rows, start=2):
                for col_idx, value in enumerate(row, start=1):
                    try:
                        sheet.cell(row=row_idx, column=col_idx, value=value)
                    except Exception as e:
                        print("Error:", e)

            sheet.freeze_panes = sheet["A2"]
            excel_file = BytesIO()
            workbook.save(excel_file)
            excel_file.seek(0)
            # form the filename with today date
            today_date = datetime.date.today()
            # check the requested format
            if selectedData["format"] == "xlsx":
                response = {
                    "file_url": "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,"
                    + base64.b64encode(excel_file.read()).decode("utf-8"),
                    "file_name": f"custom_project_export_{today_date}.xlsx",
                }
                return JsonResponse(response)
            elif selectedData["format"] == "csv":
                return response

        except Exception as e:
            response = {"error": str(e)}
        return JsonResponse(response, status=500)
