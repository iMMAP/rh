import csv
import datetime

from openpyxl.styles import Font, NamedStyle
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from rh.models import Currency, Disaggregation, FacilitySiteType, GrantType, ImplementationModalityType, PackageType, TransferCategory, TransferMechanismType, UnitType

from project_reports.models import ResponseType

header_style = NamedStyle(name="header")
header_style.font = Font(bold=True)


def write_projects_reports_to_csv(monthly_progress_report, response):
    writer = csv.writer(response)
    columns = [
        "project_code",
        "report_id",
        "cluster_name",
        "focal_person_ame",
        "focal_person_phone",
        "focal_person_email",
        "organization",
        "organization_type",
        "program_partner",
        "project_hrp-code",
        "project_title",
        "project_start_date",
        "project_end_date",
        "project_status",
        "response_types",
        "project_donor",
        "project_budget",
        "project_budget_currency",
        "report_month_number",
        "report_month",
        "report_year",
        "report_period",
        "implementing_partner",
        "admin0pcode",
        "admin0name",
        "region_name",
        "admin1pcode",
        "admin1name",
        "admin2pcode",
        "admin2name",
        "site_lat",
        "site_long",
        "facility_monitoring",
        "facility_site_type",
        "facility_site_name",
        "facility_site_id",
        "facility_site_lat",
        "facility_site_long",
        "non-hrp_beneficiary_code",
        "non-hrp_beneficiary_name",
        "hrp_beneficiary_code",
        "hrp_beneficiary_name",
        "beneficiary_status",
        "seasnol_re-assisting",
        "beneficiary_re-assisted_by",
        "activity_domain_code",
        "activity_domain_name",
        "activity_type_code",
        "activity_type_name",
        "activity_detail_code",
        "activity_detail_name",
        "indicator_name",
        "units",
        "unit_type_name",
        "transfer_type_value",
        "implementation_modality_type_name",
        "transfer_mechanism_type_name",
        "package_type_name",
        "transfer_category_name",
        "grant_type",
        "currency",
        "updated_at",
        "created_at",
    ]
    disaggregation_cols = []
    disaggregations = Disaggregation.objects.all()
    disaggregation_list = []

    for disaggregation in disaggregations:
        if disaggregation.name not in disaggregation_list:
            disaggregation_list.append(disaggregation.name)
            disaggregation_cols.append(disaggregation.name)
        else:
            continue

    disaggregation_list.append("total")
    disaggregation_cols.append("total")

    if disaggregations:
        for disaggregation_col in disaggregation_cols:
            columns.append(disaggregation_col)

    # write csv columns
    writer.writerow(columns)

    try:
        for project_reports in monthly_progress_report:
            plan_reports = project_reports.activityplanreport_set.all()
            for plan_report in plan_reports:
                location_reports = plan_report.targetlocationreport_set.all()
                for location_report in location_reports:
                    # Create a dictionary to hold disaggregation data
                    disaggregation_data = {}
                    row = [
                        project_reports.project.code if project_reports.project.code else None,
                        project_reports.__str__(),
                        ", ".join(
                            [str(cluster.code) for cluster in plan_report.activity_plan.activity_domain.clusters.all()]
                        )
                        if project_reports.project.clusters
                        else None,
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
                        ", ".join([partner.name for partner in project_reports.project.programme_partners.all()])
                        if project_reports.project.programme_partners
                        else None,
                        project_reports.project.hrp_code if project_reports.project.hrp_code else None,
                        project_reports.project.title if project_reports.project.title else None,
                        project_reports.project.start_date.astimezone(datetime.timezone.utc).replace(tzinfo=None)
                        if project_reports.project.start_date
                        else None,
                        project_reports.project.end_date.astimezone(datetime.timezone.utc).replace(tzinfo=None)
                        if project_reports.project.end_date
                        else None,
                        project_reports.project.state if project_reports.project.state else None,
                        ", ".join(
                            [response_type.name for response_type in plan_report.response_types.all() if response_type]
                        )
                        if plan_report.response_types
                        else None,
                        ", ".join(str(donor.name) for donor in project_reports.project.donors.all())
                        if project_reports.project.donors
                        else None,
                        project_reports.project.budget if project_reports.project.budget else None,
                        project_reports.project.budget_currency.name
                        if project_reports.project.budget_currency
                        else None,
                        project_reports.from_date.month if project_reports.from_date else None,
                        project_reports.from_date.strftime("%B") if project_reports.from_date else None,
                        project_reports.from_date.strftime("%Y") if project_reports.from_date else None,
                        project_reports.from_date.strftime("%Y-%m-%d") if project_reports.from_date else None,
                        location_report.target_location.implementing_partner.code
                        if location_report.target_location.implementing_partner
                        else None,
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
                        location_report.beneficiary_status if location_report.beneficiary_status else None,
                        "Yes" if location_report.seasonal_retargeting else "No",
                        location_report.prev_assisted_by if location_report.prev_assisted_by else None,
                        plan_report.activity_plan.activity_domain.code
                        if plan_report.activity_plan.activity_domain
                        else None,
                        plan_report.activity_plan.activity_domain.name
                        if plan_report.activity_plan.activity_domain
                        else None,
                        plan_report.activity_plan.activity_type.code
                        if plan_report.activity_plan.activity_type
                        else None,
                        plan_report.activity_plan.activity_type.name
                        if plan_report.activity_plan.activity_type
                        else None,
                        plan_report.activity_plan.activity_detail.code
                        if plan_report.activity_plan.activity_detail
                        else None,
                        plan_report.activity_plan.activity_detail.name
                        if plan_report.activity_plan.activity_detail
                        else None,
                        plan_report.activity_plan.indicator.name if plan_report.activity_plan.indicator else None,
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
                    total_disaggregation = 0
                    for value in disaggregation_location_list.values():
                        total_disaggregation += value
                    disaggregation_location_list["total"] = total_disaggregation
                    # Update disaggregation_data with values from disaggregation_location_list
                    for disaggregation_entry in disaggregation_list:
                        if disaggregation_entry not in disaggregation_location_list:
                            disaggregation_data[disaggregation_entry] = None

                    disaggregation_location_list.update(disaggregation_data)

                    # Append disaggregation values to the row in the order of columns
                    for column_name in columns:
                        if column_name in disaggregation_location_list:
                            row.append(disaggregation_location_list[column_name])

                    writer.writerow(row)

    except Exception as e:
        print("Error:", e)


def write_import_report_template_sheet(workbook, monthly_report):
    sheet = workbook.active
    sheet.title = "import-report-template"
    columns = [
        {"header": "project_code", "type": "string", "width": 40},
        {"header": "indicator", "type": "string", "width": 60},
        {"header": "activity_domain", "type": "string", "width": 40},
        {"header": "activity_type", "type": "string", "width": 60},
        {"header": "response_types", "type": "string", "width": 30},
        {"header": "implementing_partners", "type": "string", "width": 30},
        {"header": "package_type", "type": "string", "width": 30},
        {"header": "unit_type", "type": "string", "width": 30},
        {"header": "units", "type": "string", "width": 30},
        {"header": "no_of_transfers", "type": "string", "width": 30},
        {"header": "grant_type", "type": "string", "width": 30},
        {"header": "transfer_category", "type": "string", "width": 30},
        {"header": "currency", "type": "string", "width": 30},
        {"header": "transfer_mechanism_type", "type": "string", "width": 30},
        {"header": "implement_modility_type", "type": "string", "width": 30},
        {"header": "beneficiary_status", "type": "string", "width": 30},
        {"header": "previously_assisted_by", "type": "string", "width": 40},
        {"header": "seasonal_re-assisting", "type": "string", "width": 30},
        {"header": "admin0name", "type": "string", "width": 30},
        {"header": "admin0pcode", "type": "string", "width": 30},
        {"header": "admin1pcode", "type": "string", "width": 30},
        {"header": "admin1name", "type": "string", "width": 30},
        {"header": "admin2pcode", "type": "string", "width": 30},
        {"header": "admin2name", "type": "string", "width": 30},
        {"header": "admin3pcode", "type": "string", "width": 30},
        {"header": "location_type", "type": "string", "width": 30},
        {"header": "facility_site_type", "type": "string", "width": 30},
        {"header": "facility_id", "type": "string", "width": 30},
        {"header": "facility_name", "type": "string", "width": 30},
        {"header": "facility_lat", "type": "string", "width": 30},
        {"header": "facility_long", "type": "string", "width": 30},
    ]

    disaggregation_cols = []
    disaggregations = Disaggregation.objects.filter(clusters__in=monthly_report.project.clusters.all()).distinct()
    for disaggregation in disaggregations:
        disaggregation_cols.append({"header": disaggregation.name, "type": "string", "width": 20})

    columns = columns + disaggregation_cols
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
    container_dictionary = {
        "indicatorList": ["B"],
        "activityDomainList": ["C"],
        "activityTypeList": ["D"],
        "beneficiary_status_list": ["P", "New Beneficiary", "Existing Beneficiaries"],
        "re-assisted_list": ["Q"],
        "seasonal_re-assting_list": ["R", "Yes", "No"],
        "admin0nameList": ["S"],
        "admin0pcodeList": ["T"],
        "admin1pcodeList": ["U"],
        "admin1nameList": ["V"],
        "admin2pcodeList": ["W"],
        "admin2nameList": ["X"],
        "facilitySiteTypeList": ["AA"],
        "reponseTypeList": ["E"],
    }
    project = monthly_report.project
    project_partners_list = list(project.implementing_partners.values_list("code", flat=True))
    container_dictionary["package_type"].extend(list(PackageType.objects.values_list("name", flat=True)))
    container_dictionary["unit_type"].extend(list(UnitType.objects.values_list("name", flat=True)))
    container_dictionary["grant_type"].extend(list(GrantType.objects.values_list("name", flat=True)))
    container_dictionary["im_modility_type"].extend(
        list(ImplementationModalityType.objects.values_list("name", flat=True))
    )

    container_dictionary["transfer_mc_type"].extend(list(TransferMechanismType.objects.values_list("name", flat=True)))
    container_dictionary["transfer_category"].extend(list(TransferCategory.objects.values_list("name", flat=True)))
    container_dictionary["currency"].extend(list(Currency.objects.values_list("name", flat=True)))
    facility = list(FacilitySiteType.objects.values_list("name", flat=True))
    responseType = list(ResponseType.objects.values_list("name", flat=True))
    num_rows = 2
    project_code = project.code
    for plan in project.activityplan_set.all():
        container_dictionary["indicatorList"].append(plan.indicator.name)
        container_dictionary["activityDomainList"].append(plan.activity_domain.name)
        container_dictionary["activityTypeList"].append(plan.activity_type.name)

        for location in plan.targetlocation_set.all():
            container_dictionary["admin0pcodeList"].append(location.country.code)
            container_dictionary["admin0nameList"].append(location.country.name)
            container_dictionary["admin1nameList"].append(location.province.name)
            container_dictionary["admin1pcodeList"].append(location.province.code)
            container_dictionary["admin2pcodeList"].append(location.district.code)
            container_dictionary["admin2nameList"].append(location.district.name)
            num_rows += 1
    container_dictionary["re-assisted_list"].extend(container_dictionary["indicatorList"][1:])
    container_dictionary["facilitySiteTypeList"].extend(facility)
    container_dictionary["reponseTypeList"].extend(responseType)
    sheet["A2"] = project_code
    for key, value in container_dictionary.items():
        column = value[0]
        list_values = ",".join(value[1:])
        if len(list_values) < 255:
            dv = DataValidation(type="list", formula1=f'"{list_values}"')

            for row in range(2, num_rows):
                cell = sheet[f"{column}{row}"]
                dv.add(cell)
            sheet.add_data_validation(dv)
