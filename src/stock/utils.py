import csv


def write_csv_columns_and_rows(all_monthly_report, response):
    writer = csv.writer(response)
    columns = [
        "project",
        "cluster",
        "stock_item_type",
        "stock_purpose",
        "stock_unit",
        "stock_status",
        "report_month",
        "report_year",
        "reporting_period",
        "admin0pcode",
        "admin0name",
        "admin1pcode",
        "admin1name",
        "admin2pcode",
        "admin2name",
        "warehouse_lat",
        "warehouse_long",
        "organization",
        "username",
        "email",
        "warehouse_name",
        "number_in_stock",
        "number_in_pipline",
        "beneficiary_coverage",
        "stock_targeted_group",
        "number_of_people_assisted",
        "number_of_unit_required",
        "monthly_report_note",
        "created_at",
        "updated_at",
    ]
    writer.writerow(columns)

    for monthly_report in all_monthly_report:
        stock_reports = monthly_report.stockreport_set.all()
        for report in stock_reports:
            row = [
                report.project.code if report.project else None,
                report.cluster if report.cluster else None,
                report.stock_item_type if report.stock_item_type else None,
                report.stock_purpose if report.stock_purpose else None,
                report.stock_unit if report.stock_unit else None,
                report.status if report.status else None,
                # reporting
                monthly_report.from_date.strftime("%B"),
                monthly_report.from_date.strftime("%Y"),
                monthly_report.from_date,
                monthly_report.warehouse_location.province.parent.code,
                monthly_report.warehouse_location.province.parent.name,
                monthly_report.warehouse_location.province.code,
                monthly_report.warehouse_location.province.name,
                monthly_report.warehouse_location.district.code,
                monthly_report.warehouse_location.district.name,
                monthly_report.warehouse_location.district.lat,
                monthly_report.warehouse_location.district.long,
                monthly_report.warehouse_location.organization,
                monthly_report.warehouse_location.user if monthly_report.warehouse_location.user else None,
                monthly_report.warehouse_location.user.email if monthly_report.warehouse_location.user else None,
                monthly_report.warehouse_location.name,
                report.qty_in_stock if report.qty_in_stock else None,
                report.qty_in_pipeline if report.qty_in_pipeline else None,
                report.beneficiary_coverage if report.beneficiary_coverage else None,
                report.targeted_groups if report.targeted_groups else None,
                report.people_to_assisted if report.people_to_assisted else None,
                report.unit_required if report.unit_required else None,
                monthly_report.note if monthly_report.note else None,
                monthly_report.warehouse_location.created_at,
                monthly_report.warehouse_location.updated_at,
            ]
            writer.writerow(row)
