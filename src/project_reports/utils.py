import datetime

from openpyxl.styles import Font, NamedStyle
from openpyxl.utils import get_column_letter
from rh.models import Disaggregation

header_style = NamedStyle(name="header")
header_style.font = Font(bold=True)


def write_project_report_sheet(workbook, monthly_progress_report):
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
        {"header": "project_code", "type": "string", "width": 20},
        {"header": "report_id", "type": "string", "width": 20},
        {"header": "cluster_name", "type": "string", "width": 20},
        {"header": "focal_person_ame", "type": "string", "width": 20},
        {"header": "focal_person_phone", "type": "string", "width": 20},
        {"header": "focal_person_email", "type": "string", "width": 40},
        {"header": "organization", "type": "string", "width": 40},
        {"header": "organization_type", "type": "string", "width": 40},
        {"header": "program_partner", "type": "string", "width": 40},
        {"header": "implementing_partner", "type": "string", "width": 50},
        {"header": "project_hrp-code", "type": "string", "width": 50},
        {"header": "project_title", "type": "string", "width": 40},
        {"header": "project_start_date", "type": "date", "width": 20},
        {"header": "project_end_date", "type": "date", "width": 20},
        {"header": "project_status", "type": "string", "width": 20},
        {"header": "response_types", "type": "string", "width": 20},
        {"header": "project_donor", "type": "string", "width": 20},
        {"header": "project_budget", "type": "string", "width": 20},
        {"header": "project_budget_currency", "type": "string", "width": 20},
        {"header": "report_month_number", "type": "string", "width": 20},
        {"header": "report_month", "type": "string", "width": 20},
        {"header": "report_year", "type": "string", "width": 20},
        {"header": "report_period", "type": "string", "width": 20},
        {"header": "admin0pcode", "type": "string", "width": 20},
        {"header": "admin0name", "type": "string", "width": 20},
        {"header": "region_name", "type": "string", "width": 20},
        {"header": "admin1pcode", "type": "string", "width": 20},
        {"header": "admin1name", "type": "string", "width": 20},
        {"header": "admin2pcode", "type": "string", "width": 20},
        {"header": "admin2name", "type": "string", "width": 20},
        {"header": "site_lat", "type": "string", "width": 20},
        {"header": "site_long", "type": "string", "width": 20},
        {"header": "facility_monitoring", "type": "string", "width": 20},
        {"header": "facility_site_type", "type": "string", "width": 20},
        {"header": "facility_site_name", "type": "string", "width": 20},
        {"header": "facility_site_id", "type": "string", "width": 20},
        {"header": "facility_site_lat", "type": "string", "width": 20},
        {"header": "facility_site_long", "type": "string", "width": 20},
        {"header": "non-hrp_beneficiary_code", "type": "string", "width": 60},
        {"header": "non-hrp_beneficiary_name", "type": "string", "width": 60},
        {"header": "hrp_beneficiary_code", "type": "string", "width": 60},
        {"header": "hrp_beneficiary_name", "type": "string", "width": 60},
        {"header": "beneficiary_category", "type": "string", "width": 20},
        {"header": "activity_domain_code", "type": "string", "width": 60},
        {"header": "activity_domain_name", "type": "string", "width": 60},
        {"header": "activity_type_code", "type": "string", "width": 60},
        {"header": "activity_type_name", "type": "string", "width": 60},
        {"header": "activity_detail_code", "type": "string", "width": 60},
        {"header": "activity_detail_name", "type": "string", "width": 60},
        {"header": "indicator_name", "type": "string", "width": 60},
        {"header": "beneficiary_status", "type": "string", "width": 40},
        {"header": "beneficiaries_retargeted", "type": "string", "width": 40},
        {"header": "units", "type": "string", "width": 20},
        {"header": "unit_type_name", "type": "string", "width": 20},
        {"header": "transfer_type_value", "type": "string", "width": 20},
        {"header": "implementation_modality_type_name", "type": "string", "width": 20},
        {"header": "transfer_mechanism_type_name", "type": "string", "width": 20},
        {"header": "package_type_name", "type": "string", "width": 20},
        {"header": "transfer_category_name", "type": "string", "width": 20},
        {"header": "grant_type", "type": "string", "width": 20},
        {"header": "currency", "type": "string", "width": 20},
        {"header": "updated_at", "type": "string", "width": 20},
        {"header": "created_at", "type": "string", "width": 20},
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
    # write column headers in excel sheet
    for idx, column in enumerate(columns, start=1):
        cell = sheet.cell(row=1, column=idx, value=column["header"])
        cell.style = header_style

    column_letter = get_column_letter(idx)
    if column["type"] == "number":
        sheet.column_dimensions[column_letter].number_format = "General"
    elif column["type"] == "date":
        sheet.column_dimensions[column_letter].number_format = "mm-dd-yyyy"

    sheet.column_dimensions[column_letter].width = column["width"]
    # write the rows with report data

    rows = []

    try:
        for project_reports in monthly_progress_report:
            plan_reports = project_reports.activityplanreport_set.all()
            for plan_report in plan_reports:
                location_reports = plan_report.targetlocationreport_set.all()
                for location_report in location_reports:
                    # Create a dictionary to hold disaggregation data
                    disaggregation_data = {}
                    row = [
                        project_reports.project.code,
                        project_reports.__str__(),
                        ", ".join(
                            [cluster.code for cluster in plan_report.activity_plan.activity_domain.clusters.all()]
                        ),
                        project_reports.project.user.profile.name
                        if project_reports.project.user and project_reports.project.user.profile
                        else None,
                        project_reports.project.user.profile.phone
                        if project_reports.project.user and project_reports.project.user.profile
                        else None,
                        project_reports.project.user.email if project_reports.project.user else None,
                        project_reports.project.user.profile.organization.code
                        if project_reports.project.user
                        else None,
                        project_reports.project.user.profile.organization.type
                        if project_reports.project.user
                        else None,
                        ", ".join([partner.name for partner in project_reports.project.programme_partners.all()]),
                        ", ".join([partner.name for partner in plan_report.implementing_partners.all()]),
                        project_reports.project.hrp_code if project_reports.project.hrp_code else None,
                        project_reports.project.title,
                        project_reports.project.start_date.astimezone(datetime.timezone.utc).replace(tzinfo=None),
                        project_reports.project.end_date.astimezone(datetime.timezone.utc).replace(tzinfo=None),
                        project_reports.project.state,
                        ", ".join([response_type.name for response_type in plan_report.response_types.all()]),
                        ", ".join(str(donor.name) for donor in project_reports.project.donors.all())
                        if project_reports.project.donors
                        else None,
                        project_reports.project.budget,
                        project_reports.project.budget_currency.name
                        if project_reports.project.budget_currency
                        else None,
                        project_reports.from_date.month,
                        project_reports.from_date.strftime("%B"),
                        project_reports.from_date.strftime("%Y"),
                        project_reports.from_date.strftime("%Y-%m-%d"),
                        location_report.target_location.country.code
                        if location_report.target_location.province
                        else None,
                        location_report.target_location.country.name
                        if location_report.target_location.province
                        else None,
                        location_report.target_location.province.region_name
                        if location_report.target_location.province
                        else None,
                        location_report.target_location.province.code
                        if location_report.target_location.province
                        else None,
                        location_report.target_location.province.name
                        if location_report.target_location.province
                        else None,
                        location_report.target_location.district.code
                        if location_report.target_location.district
                        else None,
                        location_report.target_location.district.name
                        if location_report.target_location.district
                        else None,
                        location_report.target_location.district.lat
                        if location_report.target_location.district
                        else None,
                        location_report.target_location.district.long
                        if location_report.target_location.district
                        else None,
                        "yes" if location_report.target_location.facility_monitoring else "No",
                        location_report.target_location.facility_site_type.name
                        if location_report.target_location.facility_site_type
                        else None,
                        location_report.target_location.facility_name
                        if location_report.target_location.facility_name
                        else None,
                        location_report.target_location.facility_id
                        if location_report.target_location.facility_id
                        else None,
                        location_report.target_location.facility_lat
                        if location_report.target_location.facility_lat
                        else None,
                        location_report.target_location.facility_long
                        if location_report.target_location.facility_long
                        else None,
                        plan_report.activity_plan.beneficiary.code if plan_report.activity_plan.beneficiary else None,
                        plan_report.activity_plan.beneficiary.name if plan_report.activity_plan.beneficiary else None,
                        plan_report.activity_plan.hrp_beneficiary.code
                        if plan_report.activity_plan.hrp_beneficiary
                        else None,
                        plan_report.activity_plan.hrp_beneficiary.name
                        if plan_report.activity_plan.hrp_beneficiary
                        else None,
                        plan_report.activity_plan.get_beneficiary_category_display(),
                        plan_report.activity_plan.activity_domain.code,
                        plan_report.activity_plan.activity_domain.name,
                        plan_report.activity_plan.activity_type.code,
                        plan_report.activity_plan.activity_type.name,
                        plan_report.activity_plan.activity_detail.code
                        if plan_report.activity_plan.activity_detail
                        else None,
                        plan_report.activity_plan.activity_detail.name
                        if plan_report.activity_plan.activity_detail
                        else None,
                        plan_report.activity_plan.indicator.name if plan_report.activity_plan.indicator else None,
                        plan_report.get_beneficiary_status_display(),
                        "Yes" if plan_report.seasonal_retargeting else "No",
                        plan_report.units if plan_report.units else None,
                        plan_report.unit_type.name if plan_report.unit_type else None,
                        plan_report.no_of_transfers if plan_report.no_of_transfers else None,
                        plan_report.implement_modility_type.name if plan_report.implement_modility_type else None,
                        plan_report.transfer_mechanism_type.name if plan_report.transfer_mechanism_type else None,
                        plan_report.package_type.name if plan_report.package_type else None,
                        plan_report.transfer_category.name if plan_report.transfer_category else None,
                        plan_report.grant_type.name if plan_report.grant_type else None,
                        plan_report.currency.name if plan_report.currency else None,
                        project_reports.created_at.astimezone(datetime.timezone.utc).replace(tzinfo=None),
                        project_reports.updated_at.astimezone(datetime.timezone.utc).replace(tzinfo=None),
                    ]

                    # Iterate through disaggregation locations and get disaggregation values
                    disaggregation_locations = location_report.disaggregationlocationreport_set.all()
                    disaggregation_location_list = {
                        disaggregation_location.disaggregation.name: disaggregation_location.reached
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
