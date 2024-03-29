from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

# from users.factory import UserFactory
from rh.factory import (
    ActivityDetailFactory,
    ActivityDomainFactory,
    ActivityTypeFactory,
    Admin1Factory,
    Admin2Factory,
    Admin3Factory,
    BeneficiaryTypeFactory,
    ClusterFactory,
    CountryFactory,
    DisaggregationFactory,
    DonorFactory,
    IndicatorFactory,
    OrganizationFactory,
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
        # Fake Locations
        CountryFactory.create_batch(amount)
        Admin1Factory.create_batch(amount * 2)
        Admin2Factory.create_batch(amount * 2)
        Admin3Factory.create_batch(amount * 2)

        # Fake main activities
        ClusterFactory.create_batch(amount)
        OrganizationFactory.create_batch(amount)
        DonorFactory.create_batch(amount)
        BeneficiaryTypeFactory.create_batch(amount)
        ActivityDomainFactory.create_batch(amount)
        ActivityTypeFactory.create_batch(amount)
        ActivityDetailFactory.create_batch(amount)
        IndicatorFactory.create_batch(amount)
        DisaggregationFactory.create_batch(amount)

        password = "bcrypt$$2b$12$eRuG.5HPTy3ZaFrQmFMox.3Zvf0p5pj8Z0qYDh/j1Cetr93Jm005a"  # admin
        user = User.objects.update_or_create(
            username="admin", email="admin@admin.com", password=password, is_superuser=1, is_staff=1
        )
        user[0].profile.country_id = 1
        user[0].profile.organization_id = 1
        user[0].profile.clusters.add(Cluster.objects.get(pk=1))
        user[0].profile.save()

        # Fake projects
        ProjectFactory.create_batch(amount)

    def handle(self, *args, **options):
        amount = options.get("amount") or 10
        self._generate_data(amount)
