from django.core.management.base import BaseCommand

# from users.factory import UserFactory
from rh.factory import DisaggregationFactory,ProjectFactory


class Command(BaseCommand):
    help = "Generate fake data and seed the models with them, default are 10"

    def add_arguments(self, parser):
        # https://docs.python.org/3/library/argparse.html#the-add-argument-method
        # Optional!
        parser.add_argument("--amount", type=int, help="The amount of fake data you want")
        # parser.add_argument('amount', nargs='+', type=int)

    def _generate_data(self, amount):
        DisaggregationFactory.create_batch(amount)
        ProjectFactory.create_batch(amount)

    def handle(self, *args, **options):
        amount = options.get("amount") or 10
        self._generate_data(amount)
