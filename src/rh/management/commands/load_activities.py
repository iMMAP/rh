from django.core.management.base import BaseCommand
from rh.models import Cluster, ActivityDomain, ActivityType, ActivityDetail, Indicator
from project_reports.models import ResponseType
import os
from pathlib import Path
import pandas as pd
# from django.contrib.auth.hashers import make_password

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Command(BaseCommand):
    help = "Import activities from a CSV file."

    def _import_data(self):
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

        ResponseType.objects.bulk_create(
            [
                ResponseType(name="Winterization", code="winterization"),
                ResponseType(name="HRP Response", code="hrp-response"),
                ResponseType(name="Flood", code="flood"),
                ResponseType(name="Drought", code="drought"),
                ResponseType(name="Earthquake Response", code="earthquake-response"),
            ]
        )

    def handle(self, *args, **options):
        self._import_data()
