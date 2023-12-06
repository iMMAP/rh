import factory
from factory.django import DjangoModelFactory
from factory.faker import faker

from .models import Disaggregation

FAKE = faker.Faker()

class DisaggregationFactory(DjangoModelFactory):
    class Meta:
        model = Disaggregation

    name = factory.Faker("sentence", nb_words=1)
    type = factory.Faker("slug")
    