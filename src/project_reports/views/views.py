import csv
from django.contrib import messages
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.urls import reverse

from rh.models import (
    ActivityDomain,
    ActivityPlan,
    ActivityType,
    Disaggregation,
    FacilitySiteType,
    Indicator,
    Location,
    LocationType,
    BeneficiaryType,
    TargetLocation,
    PackageType,
    UnitType,
    GrantType,
    TransferCategory,
    Currency,
    TransferMechanismType,
    ImplementationModalityType,
    Organization,
)

from ..models import (
    ActivityPlanReport,
    DisaggregationLocationReport,
    ProjectMonthlyReport,
    TargetLocationReport,
    ResponseType,
)

RECORDS_PER_PAGE = 10


@login_required
def export_report_activities_import_template(request, report):
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=report)
    columns = [
        "project_code",
        "indicator",
        "activity_domain",
        "activity_type",
        "response_types",
        "implementing_partners",
        "package_type",
        "unit_type",
        "units",
        "no_of_transfers",
        "grant_type",
        "transfer_category",
        "currency",
        "transfer_mechanism_type",
        "implement_modility_type",
        "beneficiary_status",
        "admin0name",
        "admin0pcode",
        "admin1pcode",
        "admin1name",
        "admin2pcode",
        "admin2name",
        "zone",
        "location_type",
        "facility_site_type",
        "facility_monitoring",
        "facility_id",
        "facility_name",
        "facility_lat",
        "facility_long",
    ]

    disaggregation_columns = list(
        Disaggregation.objects.filter(clusters__in=monthly_report.project.clusters.all())
        .distinct()
        .values_list("name", flat=True)
    )

    all_columns = columns + disaggregation_columns

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=activity_plans_import_template.csv"

    writer = csv.writer(response)
    writer.writerow(all_columns)

    return response


@login_required
@require_http_methods(["GET", "POST"])
def import_report_activities(request, pk):
    monthly_report = get_object_or_404(ProjectMonthlyReport, pk=pk)
    errors = []

    if request.method == "POST":
        file = request.FILES.get("file")

        if file is None:
            messages.error(request, "No file provided for import.")
            return redirect(reverse("export_monthly_report_template", kwargs={"report": monthly_report.pk}))

        decoded_file = file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        report_activities = {}
        report_target_locations = []
        disaggregation_locations = []
        activity_plan_reports_list = []
        implementing_partners_mapping = {}
        response_types_list_mapping = {}

        try:
            for row in reader:
                try:
                    activity_domain = ActivityDomain.objects.filter(name=row["activity_domain"]).first()
                    if not activity_domain:
                        errors.append(
                            f"Row {reader.line_num}: Activity domain '{row['activity_domain']}' does not exist."
                        )
                        continue

                    activity_type = ActivityType.objects.filter(name=row["activity_type"]).first()
                    if not activity_type:
                        errors.append(f"Row {reader.line_num}: Activity Type '{row['activity_type']}' does not exist.")
                        continue

                    indicator = Indicator.objects.filter(name=row["indicator"]).first()
                    if not indicator:
                        errors.append(f"Row {reader.line_num}: Indicator '{row['indicator']}' does not exist.")
                        continue

                    # Define the mappings for fields to their corresponding model and field names
                    field_mappings = {
                        "package_type": PackageType,
                        "unit_type": UnitType,
                        "grant_type": GrantType,
                        "transfer_category": TransferCategory,
                        "transfer_mechanism_type": TransferMechanismType,
                        "implement_modility_type": ImplementationModalityType,
                        "beneficiary_type_id": BeneficiaryType,
                        "hrp_beneficiary_type_id": BeneficiaryType,
                    }

                    mapped_data = {}

                    # Iterate through each field mapping
                    for field, model in field_mappings.items():
                        if row.get(field, ""):
                            obj = (
                                model.objects.filter(name=row.get(field, "")).first()
                                if field != "beneficiary_type_id" and field != "hrp_beneficiary_type_id"
                                else model.objects.filter(code=row.get(field, "")).first()
                            )
                            if not obj:
                                errors.append(
                                    f"Row {reader.line_num}: {model.__name__.replace('Type', '')} '{row.get(field, '')}' does not exist."
                                )
                                continue
                            mapped_data[field] = obj
                        else:
                            mapped_data[field] = None

                    # Unpack mapped_data
                    package_type = mapped_data.get("package_type")
                    unit_type = mapped_data.get("unit_type")
                    units = row["units"] or 0
                    no_of_transfers = row["no_of_transfers"] or 0
                    grant_type = mapped_data.get("grant_type")
                    transfer_category = mapped_data.get("transfer_category")
                    transfer_mechanism_type = mapped_data.get("transfer_mechanism_type")
                    implement_modility_type = mapped_data.get("implement_modility_type")

                    beneficiary_status = {
                        label: key for key, label in ActivityPlanReport._meta.get_field("beneficiary_status").choices
                    }.get(row.get("beneficiary_status", ""), None)

                    if beneficiary_status is None:
                        errors.append(
                            f"Row {reader.line_num}: Invalid beneficiary status '{row.get('beneficiary_status', '')}'"
                        )

                    # Handle implementing partners
                    implementing_partners_list = []
                    implementing_partners = row["implementing_partners"]
                    if implementing_partners:
                        implementing_partners_list = [partner.strip() for partner in implementing_partners.split(",")]

                    # Handle Response Types
                    response_types_list = []
                    response_types = row["response_types"]
                    if response_types:
                        response_types_list = [response.strip() for response in response_types.split(",")]

                    facility_site_type = FacilitySiteType.objects.filter(name=row.get("facility_site_type")).first()
                    location_type = LocationType.objects.filter(name=row.get("location_type")).first()

                    project_activity_plan = ActivityPlan.objects.filter(
                        project_id=monthly_report.project.id,
                        state="in-progress",
                        activity_domain_id=activity_domain.id,
                        activity_type_id=activity_type.id,
                        indicator_id=indicator.id,
                    ).first()

                    activity_plan_key = (row["activity_domain"], row["activity_type"], row["indicator"])

                    # Add each implementing partner for later assignment
                    implementing_partners_mapping[activity_plan_key] = implementing_partners_list
                    response_types_list_mapping[activity_plan_key] = response_types_list

                    if activity_plan_key not in report_activities:
                        activity_plan_report = ActivityPlanReport(
                            monthly_report=monthly_report,
                            activity_plan=project_activity_plan,
                            indicator=indicator,
                            package_type=package_type,
                            unit_type=unit_type,
                            units=units,
                            no_of_transfers=no_of_transfers,
                            grant_type=grant_type,
                            transfer_category=transfer_category,
                            currency=Currency.objects.filter(name=row["currency"]).first(),
                            transfer_mechanism_type=transfer_mechanism_type,
                            implement_modility_type=implement_modility_type,
                            beneficiary_status=beneficiary_status,
                        )
                        report_activities[activity_plan_key] = activity_plan_report
                        activity_plan_reports_list.append(activity_plan_report)
                    else:
                        activity_plan_report = report_activities[activity_plan_key]

                    project_target_location = TargetLocation.objects.filter(
                        project=activity_plan_report.activity_plan.project.id,
                        activity_plan=activity_plan_report.activity_plan.id,
                        country_id=Location.objects.get(code=row["admin0pcode"]),
                        province_id=Location.objects.get(code=row["admin1pcode"]),
                        district_id=Location.objects.get(code=row["admin2pcode"]),
                    ).first()

                    target_location = TargetLocationReport(
                        activity_plan_report=activity_plan_report,
                        target_location=project_target_location,
                        country=Location.objects.get(code=row["admin0pcode"]),
                        province=Location.objects.get(code=row["admin1pcode"]),
                        district=Location.objects.get(code=row["admin2pcode"]),
                        zone=Location.objects.filter(code=row["zone"]).first(),
                        location_type=location_type or None,
                        facility_site_type=facility_site_type or None,
                        facility_monitoring=row.get("facility_monitoring") or False,
                        facility_name=row.get("facility_name") or None,
                        facility_id=row.get("facility_id") or None,
                        facility_lat=row.get("facility_lat") or None,
                        facility_long=row.get("facility_long") or None,
                        nhs_code=row.get("nhs_code", None),
                    )
                    report_target_locations.append(target_location)

                    all_disaggs = Disaggregation.objects.all()
                    for disag in all_disaggs:
                        if row.get(disag.name):
                            disaggregation_location = DisaggregationLocationReport(
                                target_location_report=target_location,
                                disaggregation=disag,
                                target=row.get(disag.name),
                            )
                            disaggregation_locations.append(disaggregation_location)
                except Exception as e:
                    errors.append(f"Error on row {reader.line_num}: {e}")

            if len(errors) > 0:
                messages.error(request, "Failed to import the Activities! Please check the errors below and try again.")
            else:
                activities = ActivityPlanReport.objects.bulk_create(report_activities.values())

                # Assign Manytomany fields after bulk_create
                for activity_plan_report in activity_plan_reports_list:
                    partners_list = implementing_partners_mapping.get(
                        (
                            activity_plan_report.activity_plan.activity_domain.name,
                            activity_plan_report.activity_plan.activity_type.name,
                            activity_plan_report.indicator.name,
                        ),
                        [],
                    )
                    if partners_list:
                        partners = Organization.objects.filter(code__in=partners_list)
                        activity_plan_report.implementing_partners.set(partners)

                    responses_list = response_types_list_mapping.get(
                        (
                            activity_plan_report.activity_plan.activity_domain.name,
                            activity_plan_report.activity_plan.activity_type.name,
                            activity_plan_report.indicator.name,
                        ),
                        [],
                    )
                    if responses_list:
                        responses = ResponseType.objects.filter(name__in=responses_list)
                        activity_plan_report.report_types.set(responses)

                TargetLocationReport.objects.bulk_create(report_target_locations)
                DisaggregationLocationReport.objects.bulk_create(disaggregation_locations)
                messages.success(request, f"[{len(activities)}] Activities imported successfully.")
                return redirect(
                    "list_report_activity_plans", project=monthly_report.project.pk, report=monthly_report.pk
                )
        except Exception as e:
            errors.append(f"Someting went wrong please check your data : {e}")
            messages.error(request, "An error occurred during the import process.")
    context = {
        "project": monthly_report.project,
        "monthly_report": monthly_report,
        "report_plans": None,
        "plans_report_filter": None,
        "report_view": False,
        "report_activities": True,
        "report_locations": False,
        "errors": errors,
    }
    return render(request, "project_reports/report_activity_plans/import_report_activity_plans.html", context)
