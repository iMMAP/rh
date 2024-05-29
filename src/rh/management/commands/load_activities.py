import os
from pathlib import Path

import pandas as pd
from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from project_reports.models import ResponseType

from rh.models import (  # TargetLocation,
    ActivityDetail,
    ActivityDomain,
    ActivityPlan,
    ActivityType,
    BeneficiaryType,
    Cluster,
    Currency,
    Donor,
    GrantType,
    ImplementationModalityType,
    Indicator,
    Organization,
    PackageType,
    Project,
    TransferCategory,
    TransferMechanismType,
    UnitType,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Command(BaseCommand):
    help = "Import activities from a 'output_2024' CSV file."

    def _import_groups(self):
        groups = ["SUPERADMIN", "iMMAP IMO", "CLUSTER LEAD", "ORGANIZATION LEAD", "ORGANIZATION USER"]
        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Group "{group_name}" created successfully'))
                if group_name == "SUPERADMIN":
                    all_permissions = Permission.objects.all()
                    group.permissions.set(all_permissions)
                    self.stdout.write(self.style.SUCCESS(f'All permissions assigned to group "{group_name}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Group "{group_name}" already exists'))

    def _create_activity_plans(self):
        # Import the actvity_domain, activity_types, activity_details
        path = os.path.join(BASE_DIR.parent, "scripts/data/updated_nov_2023/plans.xlsx")
        df = pd.read_excel(path)
        df.fillna(False, inplace=True)

        plans = df.to_dict(orient="records")
        for index, plan in enumerate(plans):
            project = Project.objects.filter(old_id=plan.get("project_id", "")).first()
            activity_domain = ActivityDomain.objects.filter(code=plan.get("activity_type_id", "")).first()
            activity_type = ActivityType.objects.filter(code=plan.get("activity_description_id", "")).first()
            activity_detail = ActivityDetail.objects.filter(code=plan.get("activity_type_id", "")).first()
            indicator = Indicator.objects.filter(name=plan.get("indicator_id", "")).first()
            package_type = PackageType.objects.filter(name=plan.get("package_type_name", "")).first()
            unit_type = UnitType.objects.filter(name=plan.get("unit_type_name", "")).first()
            grant_type = GrantType.objects.filter(name=plan.get("grant_type_name", "")).first()
            transfer_category = TransferCategory.objects.filter(name=plan.get("transfer_category_name", "")).first()
            transfer_mechanism_type = TransferMechanismType.objects.filter(
                name=plan.get("mpc_mechanism_type_name", "")
            ).first()
            implement_modility_type = ImplementationModalityType.objects.filter(
                name=plan.get("mpc_delivery_type_name", "")
            ).first()
            beneficiary = BeneficiaryType.objects.filter(code=plan.get("beneficiary_type_id", "")).first()
            hrp_beneficiary = BeneficiaryType.objects.filter(code=plan.get("hrp_beneficiary_type_id", "")).first()

            activity_plan, created = ActivityPlan.objects.get_or_create(
                project_id=project.id,
                active=True,
                state="in-progress",
                activity_domain_id=activity_domain.id,
                activity_type_id=activity_type.id,
                activity_detail_id=activity_detail.id if activity_detail else None,
                indicator_id=indicator.id,
                beneficiary_id=beneficiary.id if beneficiary else None,
                hrp_beneficiary_id=hrp_beneficiary.id if hrp_beneficiary else None,
                beneficiary_category=plan.get("beneficiary_category_id", ""),
                total_set_target=plan.get("total_beneficiaries", 0),
                package_type_id=package_type.id if package_type else None,
                unit_type_id=unit_type.id if unit_type else None,
                grant_type_id=grant_type.id if grant_type else None,
                transfer_category_id=transfer_category.id if transfer_category else None,
                transfer_mechanism_type_id=transfer_mechanism_type.id if transfer_mechanism_type else None,
                implement_modility_type_id=implement_modility_type.id if implement_modility_type else None,
            )
            activity_plan.save()

    def _import_projects(self):
        # Import the actvity_domain, activity_types, activity_details
        path = os.path.join(BASE_DIR.parent, "scripts/data/updated_nov_2023/projects.xlsx")
        df = pd.read_excel(path)
        df.fillna(False, inplace=True)

        projects = df.to_dict(orient="records")

        for index, project_vals in enumerate(projects):
            # Convert the naive datetime to an aware datetime using the timezone
            aware_start_date = timezone.make_aware(project_vals.get("project_start_date", "test"))
            aware_end_date = timezone.make_aware(project_vals.get("project_end_date", "test"))

            project_code = project_vals.get("project_code")
            if not project_code:
                project_code = f"TEST-CODE-{index}"

            project, created = Project.objects.get_or_create(
                title=project_vals.get("project_title", "test"),
                code=project_code,
                start_date=aware_start_date,
                end_date=aware_end_date,
                state="in-progress",
                active=True,
                is_hrp_project=True if project_vals.get("project_hrp_project", False) == 1 else None,
                has_hrp_code=True if project_vals.get("project_hrp_project", False) == 1 else None,
                hrp_code=project_vals.get("project_hrp_code", "test"),
                budget=project_vals.get("project_budget", 0),
                description=project_vals.get("project_description", "test"),
                old_id=project_vals.get("_id", "test"),
            )

            # Set ManyToMany field values and related field values
            if created:
                cluster = Cluster.objects.filter(code=project_vals.get("cluster_id"))
                project.clusters.set(cluster)

                activity_types = project_vals.get("activity_type").split(",")
                activity_domains = ActivityDomain.objects.filter(code__in=activity_types)
                project.activity_domains.set(activity_domains)

                implementing_partners = project_vals.get("implementing_partners")
                if not implementing_partners:
                    project.implementing_partners.set([])
                else:
                    implementing_partners = project_vals.get("implementing_partners").split(",")
                    partners = Organization.objects.filter(code__in=implementing_partners)
                    project.implementing_partners.set(partners)

                programme_partners = project_vals.get("programme_partners")
                if not programme_partners:
                    project.programme_partners.set([])
                else:
                    partners = programme_partners.split(",")
                    organizations = Organization.objects.filter(code__in=partners)
                    project.programme_partners.set(organizations)

                project_donors = project_vals.get("project_donor")
                if project_donors:
                    donors_list = project_donors.split(",")
                    donors = Donor.objects.filter(code__in=donors_list)
                    project.donors.set(donors)

                users = User.objects.filter(
                    Q(username=project_vals.get("username", "test")) | Q(email=project_vals.get("email", "test"))
                )

                if users.exists():
                    user = users.first()
                    project.user = user

                budget_currencies = Currency.objects.filter(
                    name=project_vals.get("project_budget_currency", "usd").upper()
                )
                if budget_currencies.exists():
                    budget_currency = budget_currencies.first()
                    project.budget_currency = budget_currency

                project.save()

        self.stdout.write(self.style.SUCCESS(f"{len(projects)} Projects - created successfully"))

    def _import_data(self):
        # Handle groups creation
        self._import_groups()

        ResponseType.objects.bulk_create(
            [
                ResponseType(name="Winterization"),
                ResponseType(name="HRP Response"),
                ResponseType(name="Flood"),
                ResponseType(name="Drought"),
                ResponseType(name="Earthquake Response"),
                ResponseType(name="Cholera"),
            ]
        )

        # (Implementation Modality) MPC Delivery Type id
        ImplementationModalityType.objects.bulk_create(
            [
                ImplementationModalityType(name="Cash"),
                ImplementationModalityType(name="Voucher"),
                ImplementationModalityType(name="In kind"),
                ImplementationModalityType(name="Bonus"),
            ]
        )

        # MechanismType
        TransferMechanismType.objects.bulk_create(
            [
                TransferMechanismType(name="Hawala"),
                TransferMechanismType(name="Cash in Envelope"),
                TransferMechanismType(name="Bank"),
                TransferMechanismType(name="Mobile Cash"),
                TransferMechanismType(name="E Cash"),
                TransferMechanismType(name="Token System"),
                TransferMechanismType(name="Paper Voucher"),
                TransferMechanismType(name="Commodity Voucher"),
                TransferMechanismType(name="Value Voucher"),
                TransferMechanismType(name="Mobile Voucher"),
                TransferMechanismType(name="E Voucher"),
                TransferMechanismType(name="Distribution"),
                TransferMechanismType(name="Electronic Card - Vouchers"),
            ]
        )

        # Package Type
        PackageType.objects.bulk_create(
            [
                PackageType(name="Standard"),
                PackageType(name="Non-standard"),
            ]
        )

        # mpc_transfer_category_id
        TransferCategory.objects.bulk_create(
            [
                TransferCategory(name="Individual"),
                TransferCategory(name="Household"),
            ]
        )

        # Grant Type
        GrantType.objects.bulk_create(
            [
                GrantType(name="Conditional"),
                GrantType(name="Unconditional"),
                GrantType(name="Restrcited"),
                GrantType(name="Unrestricted"),
            ]
        )

        # Unit Types
        UnitType.objects.bulk_create(
            [
                UnitType(name="AF", code="af"),
                UnitType(name="USD", code="usd"),
                UnitType(name="KGs", code="kg"),
                UnitType(name="MTs", code="mt"),
                UnitType(name="EUR", code="eur"),
                UnitType(name="Kit", code="kit"),
            ]
        )

        # Import the actvity_domain, activity_types, activity_details
        path = os.path.join(BASE_DIR.parent, "scripts/data/output_2024.csv")
        df = pd.read_csv(path)
        grouped_by_cluster_data = df.groupby("cluster_id")

        for cluster_id, group_data in grouped_by_cluster_data:
            cluster = Cluster.objects.get(code=cluster_id)
            grouped_by_activity_type_id_data = group_data.groupby(["activity_type_id", "activity_type_name"])

            for activity_type_id, group_data_1 in grouped_by_activity_type_id_data:
                activity_domain, created = ActivityDomain.objects.get_or_create(
                    code=activity_type_id[0], name=activity_type_id[1]
                )
                if created:
                    activity_domain.clusters.add(cluster)
                    activity_domain.save()

                g_by_activity_description_data = group_data_1.groupby(
                    ["activity_description_id", "activity_description_name"]
                )
                for activity_description_id, group_data_2 in g_by_activity_description_data:
                    activity_type, created = ActivityType.objects.get_or_create(
                        code=activity_description_id[0], name=activity_description_id[1]
                    )
                    if created:
                        activity_type.activity_domain = activity_domain
                        activity_type.save()

                    g_by_activity_details_data = group_data_1.groupby(["activity_detail_id", "activity_detail_name"])
                    for activity_detail_id, group_data_3 in g_by_activity_details_data:
                        activity_detail, created = ActivityDetail.objects.get_or_create(
                            code=activity_detail_id[0], name=activity_detail_id[1]
                        )
                        if created:
                            activity_detail.activity_type = activity_type
                            activity_detail.save()

                    for index, row in group_data_2.iterrows():
                        indicator, created = Indicator.objects.get_or_create(name=row["indicator_name"])
                        if created:
                            indicator.activity_types.add(activity_type)

        # Create an admin user
        password = "bcrypt$$2b$12$eRuG.5HPTy3ZaFrQmFMox.3Zvf0p5pj8Z0qYDh/j1Cetr93Jm005a"  # admin
        user = User.objects.update_or_create(
            username="admin", email="admin@admin.com", password=password, is_superuser=1, is_staff=1
        )
        user[0].profile.country_id = 1
        user[0].profile.organization_id = 1
        user[0].profile.clusters.add(Cluster.objects.get(pk=1))
        user[0].profile.save()

        # Import Projects
        self._import_projects()
        self._create_activity_plans()

    def handle(self, *args, **options):
        self._import_data()
