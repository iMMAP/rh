import factory
from factory.django import DjangoModelFactory
from factory.faker import faker

from .models import Disaggregation

FAKE = faker.Faker()

D_TYPES = [
    ("public", "Public"),
    ("private", "Private"),
]

class DisaggregationFactory(DjangoModelFactory):
    class Meta:
        model = Disaggregation

    name = factory.Faker("sentence", nb_words=1)
    type = factory.Iterator(D_TYPES, getter=lambda c: c[0])

    # Run the bellow command in the shell to create fake data
    # DisaggregationFactory.create_batch(amount)
    