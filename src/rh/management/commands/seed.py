from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

# from users.factory import UserFactory
from rh.factory import (
    ProjectFactory,
)
from rh.models import Cluster

# from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = "Generate fake data and seed the models with them, default are 10"

    def add_arguments(self, parser):
        # https://docs.python.org/3/library/argparse.html#the-add-argument-method
        # Optional!
        parser.add_argument("--amount", type=int, help="The amount of fake data you want")
        # parser.add_argument('amount', nargs='+', type=int)

    def _generate_data(self, amount):
        password = "bcrypt$$2b$12$eRuG.5HPTy3ZaFrQmFMox.3Zvf0p5pj8Z0qYDh/j1Cetr93Jm005a"  # admin
        user = User.objects.update_or_create(
            username="admin", email="admin@admin.com", password=password, is_superuser=1, is_staff=1
        )
        user[0].profile.country_id = 2
        user[0].profile.organization_id = 1
        user[0].profile.clusters.add(Cluster.objects.get(pk=1))
        user[0].profile.save()

        # Fake projects
        ProjectFactory.create_batch(amount)

    def handle(self, *args, **options):
        amount = options.get("amount") or 10
        self._generate_data(amount)
