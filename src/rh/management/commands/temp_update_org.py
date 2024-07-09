import os
import csv
from pathlib import Path

import pandas as pd
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from rh.models import (  # TargetLocation,
    Location ,
    Organization,
  
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Command(BaseCommand):
    help = "Temp update orgs countries"
    def update_org(self):
        path = os.path.join(BASE_DIR.parent, "scripts/data/updated_nov_2023/organizations.csv")
        with open(path, 'r') as file:
            reader = csv.DictReader(file)
            afg = Location.objects.get(code="AF")
            so = Location.objects.get(code="SO")
            ng = Location.objects.get(code="NG")

            for row in reader:
                admin0code = row['admin0pcode']

                try:
                    organization = Organization.objects.get(code=row['organization'])  # Assuming you have a unique identifier like _id
                except Exception:
                    continue

                # Perform logic to map admin0code to country and update the organization
                if organization:
                    if admin0code == "ALL":
                        organization.countries.add(afg,so)
                    if admin0code == "AF":
                        organization.countries.add(afg)
                    elif admin0code == "SO":
                        organization.countries.add(so)
                    elif admin0code == "NG":
                        organization.countries.add(ng)


    def handle(self, *args, **options):
        self.update_org()
