import os
from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand

from rh.models import (
    Location,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Command(BaseCommand):
    help = "Load locations region name"

    def _import_data(self):
        path = os.path.join(BASE_DIR.parent, "scripts/data/updated_nov_2023/af_loc.csv")
        df = pd.read_csv(path)

        for index, row in df.iterrows():
            try:
                obj = Location.objects.get(code=row["adm2_pcode"])
                
                obj.region_name = row["region_name"]
                obj.save()

                self.stdout.write(self.style.SUCCESS(f"Updated entry: {obj}"))

            except Location.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"No entry found with id: {row['id']}"))
         
        self.stdout.write(self.style.SUCCESS("Database update complete"))

    def handle(self, *args, **options):
        self._import_data()