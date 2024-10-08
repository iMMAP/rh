import os
from pathlib import Path

import pandas as pd
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand

from rh.models import (
    ActivityDetail,
    ActivityDomain,
    ActivityType,
    Cluster,
    Indicator,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Command(BaseCommand):
    help = "Import activities from a 'output_2024' CSV file."

    def _import_types_fixtures(self):
        self.stdout.write("Loading types fixture data...")
        try:
            call_command("loaddata", "types.json")
            self.stdout.write(self.style.SUCCESS("Successfully loaded types fixture data"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading types fixture data: {e}"))

    def _import_groups_fixtures(self):
        self.stdout.write("Loading groups fixture data...")
        try:
            call_command("loaddata", "groups.json")
            self.stdout.write(self.style.SUCCESS("Successfully loaded groups fixture data"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading groups fixture data: {e}"))

    def _import_data(self):
        self.stdout.write("Loading `output_2024.csv` file data...")

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

    def handle(self, *args, **options):
        self._import_data()

        self._import_types_fixtures()

        # Handle groups creation
        self._import_groups_fixtures()
