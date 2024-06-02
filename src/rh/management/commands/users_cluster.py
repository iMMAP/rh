import os
from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand

from django.contrib.auth.models import User
from users.models import Profile
from rh.models import Cluster

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Command(BaseCommand):
    help = "Load users cluster to profile"

    def _import_data(self):
        path = os.path.join(BASE_DIR.parent, "scripts/data/updated_nov_2023/user.csv")
        df = pd.read_csv(path)

        for index, row in df.iterrows():
            try:
                users = User.objects.filter(email=row["email"])
                user = users.first()

                # delete duplicates
                users.exclude(id=users.first().id).delete()

                try:
                    profile = user.profile

                    try:
                        cluster = Cluster.objects.get(code=row["cluster_id"])
                    except Cluster.DoesNotExist:
                        continue

                    profile.clusters.add(cluster)

                except Profile.DoesNotExist:
                    print(f"Profile does not exist for user - {user}")
                    user.delete()
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"No entry found with id: {row['email']}"))
            except Exception as e:
                print(f"{e} ==== email={row['email']}")

        self.stdout.write(self.style.SUCCESS("Database update complete"))

    def handle(self, *args, **options):
        self._import_data()
