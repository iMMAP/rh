import factory
from factory.django import DjangoModelFactory
from factory.faker import faker

from .models import Disaggregation,Cluster,Location

FAKE = faker.Faker()

D_TYPES = [
    ("age", "Age"),
    ("gender", "Gender"),
]

class DisaggregationFactory(DjangoModelFactory):
    class Meta:
        model = Disaggregation

    name = factory.Faker("word")
    type = factory.Iterator(D_TYPES, getter=lambda c: c[0])

    # Run the bellow command in the shell to create fake data
    # DisaggregationFactory.create_batch(amount)


class LocationFactory(DjangoModelFactory):
    class Meta:
        model = Location

    code = factory.Faker('pystr', max_chars=200)
    name = factory.Faker('pystr', max_chars=200)
    level = factory.Faker('random_int')
    original_name = factory.Faker('pystr', max_chars=200)
    type = factory.Iterator(Location.LOCATION_TYPES, getter=lambda c: c[0])
    classification = factory.Iterator(Location.LOCATION_CLASSIFICATIONS, getter=lambda c: c[0])
    lat = factory.Faker('latitude')
    long = factory.Faker('longitude')

class ClusterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cluster

    name = factory.Faker('name')
    title = factory.Faker('sentence', nb_words=4)
    ocha_code = factory.Faker('random_number', digits=5)

    @factory.lazy_attribute
    def code(self):
        return self.name.capitalize()

    @factory.post_generation
    def countries(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for location in extracted:
                self.countries.add(location)
        else:
            locations = Location.objects.filter(type="Country")

            for location in locations:
                self.countries.add(location)