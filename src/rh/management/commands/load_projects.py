import os
from pathlib import Path

import pandas as pd
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Q
from django.utils import timezone
from users.models import Profile

from rh.models import (
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
    Location,
    Organization,
    PackageType,
    Project,
    TransferCategory,
    TransferMechanismType,
    UnitType,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Command(BaseCommand):
    help = "Import Projects"

    def _load_target_locations(self):
        # Import the actvity_domain, activity_types, activity_details
        # path = os.path.join(BASE_DIR.parent, "scripts/data/updated_nov_2023/fsac_locations.xlsx")
        # df = pd.read_excel(path)
        # df.fillna(False, inplace=True)
        # locations_created = 0
        # locations = df.to_dict(orient="records")
        # for index, location in enumerate(locations):
        #     project = Project.objects.filter(old_id=location.get("project_id", "")).first()
        #     country = Location.objects.filter(code="AF").first()
        #     province = Location.objects.filter(code=location.get("admin1pcode", "").strip()).first()
        #     district = Location.objects.filter(code=location.get("admin2pcode", "").strip()).first()
        #     activity_plans = project.activityplan_set.all()
        #     for activity_plan in activity_plans:
        #         target_location, created = TargetLocation.objects.get_or_create(
        #             project_id=project.id,
        #             state="in-progress",
        #             activity_plan_id=activity_plan.id,
        #             country_id=country.id,
        #             province_id=province.id,
        #             district_id=district.id,
        #         )
        #         target_location.save()
        #
        #         if created:
        #             locations_created += 1

        path = os.path.join(BASE_DIR.parent, "scripts/data/updated_nov_2023/protection_locations.xlsx")
        df = pd.read_excel(path)
        df.fillna(False, inplace=True)
        locations = df.to_dict(orient="records")

        locations_created = 0
        with connection.cursor() as cursor:
            for location in locations:
                project_id = location.get("project_id", "")
                cursor.execute("SELECT id FROM rh_project WHERE old_id = %s", [project_id])
                project = cursor.fetchone()

                if project:
                    project_id = project[0]
                    cursor.execute("SELECT id FROM rh_location WHERE code = 'AF'")
                    country = cursor.fetchone()
                    country_id = country[0] if country else None

                    admin1pcode = location.get("admin1pcode", "").strip()
                    cursor.execute("SELECT id FROM rh_location WHERE code = %s", [admin1pcode])
                    province = cursor.fetchone()
                    province_id = province[0] if province else None

                    admin2pcode = location.get("admin2pcode", "").strip()
                    cursor.execute("SELECT id FROM rh_location WHERE code = %s", [admin2pcode])
                    district = cursor.fetchone()
                    district_id = district[0] if district else None

                    cursor.execute("SELECT id FROM rh_activityplan WHERE project_id = %s", [project_id])
                    activity_plans = cursor.fetchall()

                    for activity_plan in activity_plans:
                        activity_plan_id = activity_plan[0]
                        cursor.execute(
                            """
                                            SELECT id FROM rh_targetlocation 
                                            WHERE project_id = %s AND state = %s AND activity_plan_id = %s 
                                            AND country_id = %s AND province_id = %s AND district_id = %s
                                        """,
                            [project_id, "in-progress", activity_plan_id, country_id, province_id, district_id],
                        )

                        target_location = cursor.fetchone()

                        if not target_location:
                            cursor.execute(
                                """
                                            INSERT INTO rh_targetlocation 
                                            (project_id, state, activity_plan_id, country_id, province_id, district_id)
                                            VALUES (%s, %s, %s, %s, %s, %s)
                                        """,
                                [project_id, "in-progress", activity_plan_id, country_id, province_id, district_id],
                            )
                            locations_created += 1

        self.stdout.write(self.style.SUCCESS(f"{locations_created} Target Locations - created successfully!!!"))

    def _load_activity_plans(self):
        # Import the actvity_domain, activity_types, activity_details
        path = os.path.join(BASE_DIR.parent, "scripts/data/updated_nov_2023/protection_plans.xlsx")
        df = pd.read_excel(path)
        df.fillna(False, inplace=True)
        plans_exits = 0
        plans_created = 0
        plans = df.to_dict(orient="records")
        for index, plan in enumerate(plans):
            project = Project.objects.filter(old_id=plan.get("project_id", "")).first()
            if not project:
                print(plan.get("project_id", ""))
                continue
            activity_domain_name = plan.get("activity_type_id", "")
            if activity_domain_name:
                activity_domain_name.strip()
            else:
                print("NONE")
            activity_domain = ActivityDomain.objects.filter(code=activity_domain_name).first()
            if not activity_domain:
                print(f"activity_domain: {activity_domain_name}")
                continue
            activity_type = ActivityType.objects.filter(code=plan.get("activity_description_id", "").strip()).first()
            if not activity_type:
                print(f"activity_description_id: {plan.get('activity_description_id', '')}")
                continue
            activity_detail = ActivityDetail.objects.filter(code=plan.get("activity_type_id", "").strip()).first()
            indicator = Indicator.objects.filter(name=plan.get("indicator_id", "").strip()).first()
            if not indicator:
                print(plan.get("indicator_id", ""))
                continue
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

            try:
                activity_plan, created = ActivityPlan.objects.get_or_create(
                    project_id=project.id,
                    state="in-progress",
                    activity_domain_id=activity_domain.id,
                    activity_type_id=activity_type.id,
                    activity_detail_id=activity_detail.id if activity_detail else None,
                    indicator_id=indicator.id,
                    beneficiary_id=beneficiary.id if beneficiary else None,
                    hrp_beneficiary_id=hrp_beneficiary.id if hrp_beneficiary else None,
                    beneficiary_category=plan.get("beneficiary_category_id", "").lower()
                    if plan.get("beneficiary_category_id", "")
                    else "",
                    # total_set_target=plan.get("total_beneficiaries", 0),
                    package_type_id=package_type.id if package_type else None,
                    unit_type_id=unit_type.id if unit_type else None,
                    grant_type_id=grant_type.id if grant_type else None,
                    transfer_category_id=transfer_category.id if transfer_category else None,
                    transfer_mechanism_type_id=transfer_mechanism_type.id if transfer_mechanism_type else None,
                    implement_modility_type_id=implement_modility_type.id if implement_modility_type else None,
                )
                if created:
                    plans_created += 1
                else:
                    plans_exits += 1
                    strd = f"""
                    Project: {activity_plan.project.old_id}
                    Activity Plan: {activity_plan}
                    Activity Domain: {activity_plan.activity_domain.code if activity_plan.activity_domain else ""}
                    Activity Type: {activity_plan.activity_type.code if activity_plan.activity_type else ""}
                    Activity Detail: {activity_plan.activity_detail.code if activity_plan.activity_detail else ""}
                    Indicator: {activity_plan.indicator.name if activity_plan.indicator else ""}
                    Beneficiary: {activity_plan.beneficiary.code if activity_plan.beneficiary else ""}
                    HRP Beneficiary: {activity_plan.hrp_beneficiary.code if activity_plan.hrp_beneficiary else ""}
                    """
                    print(f"{strd}")
                activity_plan.save()
            except Exception as e:
                print(e)
        self.stdout.write(self.style.SUCCESS(f"{plans_created} Plans - created successfully!!"))
        self.stdout.write(self.style.SUCCESS(f"{plans_exits} Plans - Already Exist!!"))

    def _load_projects(self):
        # Import the actvity_domain, activity_types, activity_details
        path = os.path.join(BASE_DIR.parent, "scripts/data/updated_nov_2023/protection_projects.xlsx")
        df = pd.read_excel(path)
        df.fillna(False, inplace=True)

        projects = df.to_dict(orient="records")
        projects_created = 0

        for index, project_vals in enumerate(projects):
            # Convert the naive datetime to an aware datetime using the timezone
            aware_start_date = timezone.make_aware(project_vals.get("project_start_date", "test"))
            aware_end_date = timezone.make_aware(project_vals.get("project_end_date", "test"))

            project_code = project_vals.get("project_code")
            hrp_code = project_vals.get("project_hrp_code", "test")
            if not project_code:
                project_code = f"{project_vals.get('_id', 'test')}-TEST-CODE"
            project_with_code_exists = Project.objects.filter(code=project_code)
            if project_with_code_exists:
                project_code = f"{project_vals.get('_id', 'test')}-{project_code}"
            project_with_hrp_exists = Project.objects.filter(hrp_code=project_vals.get("project_hrp_code", "test"))
            if project_with_hrp_exists:
                hrp_code = f"{project_vals.get('_id', 'test')}-{project_vals.get('project_hrp_code', 'test')}"

            project, created = Project.objects.get_or_create(
                title=project_vals.get("project_title", "test"),
                code=project_code,
                start_date=aware_start_date,
                end_date=aware_end_date,
                state="in-progress",
                is_hrp_project=True if project_vals.get("project_hrp_project", False) == 1 else False,
                hrp_code=hrp_code,
                budget=project_vals.get("project_budget", 0),
                description=project_vals.get("project_description", "test"),
                old_id=project_vals.get("_id", "test"),
            )

            cluster_ids = project_vals.get("cluster_id").split(",")

            # Set ManyToMany field values and related field values
            if created:
                projects_created += 1
                cluster = Cluster.objects.filter(code__in=cluster_ids)
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

                # Handle User and Profile Creation
                username = project_vals.get("username", "test")
                name = project_vals.get("name", "test")
                user_org = project_vals.get("organization", "test")
                email = project_vals.get("email", "test")

                users = User.objects.filter(Q(username=username) | Q(email=email))

                if users.exists():
                    user = users.first()
                else:
                    # If user does not exist, create a new one
                    user = User.objects.create_user(
                        username=username, email=email, first_name=name, password="asd54321"
                    )
                    country = Location.objects.filter(code="AF")

                    # Retrieve or create the organization based on the provided code
                    org_obj, created = Organization.objects.get_or_create(code=user_org)
                    if created:
                        org_obj.clusters.set(cluster)
                        org_obj.countries.set(country)

                    # Create user profile
                    profile = Profile.objects.create(user=user, organization=org_obj, country=country.first())
                    # Set many-to-many relationship for clusters
                    profile.clusters.set(cluster)

                project.user = user
                project.organization = user.profile.organization

                budget_currencies = Currency.objects.filter(
                    name=project_vals.get("project_budget_currency", "usd").upper()
                )
                if budget_currencies.exists():
                    budget_currency = budget_currencies.first()
                    project.budget_currency = budget_currency

                project.save()
        self.stdout.write(self.style.SUCCESS(f"{projects_created} Projects - created successfully"))

    def _import_data(self):
        # Import Projects
        self.stdout.write(self.style.SUCCESS("Loading Projects!"))
        self._load_projects()
        self.stdout.write(self.style.SUCCESS("Loading Plans!"))
        self._load_activity_plans()
        self.stdout.write(self.style.SUCCESS("Loading Locations!"))
        self._load_target_locations()
        self.stdout.write(self.style.SUCCESS("ALL DONE!"))

    def handle(self, *args, **options):
        self._import_data()
