from random import randint

import factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory
from factory.faker import faker

from rh.models import Cluster, Location, Organization

from .models import Profile

FAKE = faker.Faker()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    is_active = 1
    is_superuser = 0
    is_staff = 0
    password = make_password("12345678")

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    @factory.post_generation
    def profile(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for profile in extracted:
                self.profile = profile
        else:
            self.profile = ProfileFactory(user=self)

    @factory.lazy_attribute
    def username(self):
        return f"{self.first_name}_{self.last_name}_{randint(1, 11)}"

    @factory.lazy_attribute
    def email(self):
        return f"{self.username}@gmail.com"


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    position = factory.Faker("job")
    phone = factory.Faker("phone_number")
    whatsapp = factory.Faker("phone_number")
    skype = factory.Faker("user_name")
    old_id = factory.Faker("uuid4")
    is_cluster_contact = factory.Faker("boolean")

    organization = factory.Iterator(Organization.objects.all())
    country = factory.Iterator(Location.objects.filter(level=0))

    @factory.post_generation
    def clusters(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for cluster in extracted:
                self.clusters.add(cluster)
        else:
            clusters = Cluster.objects.all()[:3]
            for cluster in clusters:
                self.clusters.add(cluster)
