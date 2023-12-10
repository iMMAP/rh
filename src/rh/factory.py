import factory
from factory.django import DjangoModelFactory
from factory.faker import faker
import pytz
from .models import (
    Project,
    Indicator,
    Disaggregation,
    Cluster,
    Location,
    BeneficiaryType,
    Organization,
    Donor,
    ActivityDomain,
    ActivityType,
    ActivityDetail,
    ActivityPlan,
    LocationType,
TargetLocation,
DisaggregationLocation
)
from users.factory import UserFactory

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

    name = factory.Faker("name")
    level = factory.Faker("random_int", min=1, max=3)
    original_name = factory.Faker("name")
    type = factory.Iterator(Location.LOCATION_TYPES, getter=lambda c: c[0])
    classification = factory.Iterator(Location.LOCATION_CLASSIFICATIONS, getter=lambda c: c[0])
    lat = factory.Faker("latitude")
    long = factory.Faker("longitude")
    parent = factory.LazyAttribute(lambda obj: None)

    @factory.lazy_attribute
    def code(self):
        return self.name.capitalize()


class ClusterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cluster

    name = factory.Faker("name")
    title = factory.Faker("sentence", nb_words=4)
    ocha_code = factory.Faker("random_number", digits=5)

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


class BeneficiaryTypeFactory(DjangoModelFactory):
    class Meta:
        model = BeneficiaryType

    name = factory.Faker("word")
    code = factory.Faker("word")
    country = factory.SubFactory(LocationFactory)
    is_hrp_beneficiary = factory.Faker("boolean")
    is_regular_beneficiary = factory.Faker("boolean")
    start_date = factory.Faker("date_time_this_decade", tzinfo=pytz.UTC)
    end_date = factory.Faker("date_time_this_decade", tzinfo=pytz.UTC)
    description = factory.Faker("sentence")

    @factory.post_generation
    def clusters(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for cluster in extracted:
                self.clusters.add(cluster)
        else:
            clusters = Location.objects.all()
            for cluster in clusters:
                self.clusters.add(cluster)


class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Faker("company")
    type = factory.Faker("word")

    @factory.lazy_attribute
    def code(self):
        return self.name.capitalize()

    @factory.post_generation
    def countries(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for country in extracted:
                self.countries.add(country)
        else:
            self.countries.add(LocationFactory())

    @factory.post_generation
    def clusters(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for cluster in extracted:
                self.clusters.add(cluster)
        else:
            self.clusters.add(ClusterFactory())


class DonorFactory(DjangoModelFactory):
    class Meta:
        model = Donor

    name = factory.Faker("company")
    countries = factory.RelatedFactory(LocationFactory)
    clusters = factory.RelatedFactory(ClusterFactory)

    @factory.lazy_attribute
    def code(self):
        return self.name.capitalize()


class ActivityDomainFactory(DjangoModelFactory):
    class Meta:
        model = ActivityDomain

    active = factory.Faker("boolean")
    code = factory.Faker("pystr", max_chars=200)
    name = factory.Faker("word")
    countries = factory.RelatedFactory(LocationFactory)
    clusters = factory.RelatedFactory(ClusterFactory)


class ActivityTypeFactory(DjangoModelFactory):
    class Meta:
        model = ActivityType

    activity_domain = factory.SubFactory(ActivityDomainFactory)
    active = factory.Faker("boolean")
    code = factory.Faker("pystr", max_chars=600)
    name = factory.Faker("word")
    countries = factory.RelatedFactory(LocationFactory)
    clusters = factory.RelatedFactory(ClusterFactory)
    activity_date = factory.Faker("date_time")
    hrp_code = factory.Faker("pystr", max_chars=200)
    code_indicator = factory.Faker("boolean")
    start_date = factory.Faker("date_time")
    end_date = factory.Faker("date_time")
    ocha_code = factory.Faker("pystr", max_chars=200)


class ActivityDetailFactory(DjangoModelFactory):
    class Meta:
        model = ActivityDetail

    activity_type = factory.SubFactory(ActivityTypeFactory)
    name = factory.Faker("word")

    @factory.lazy_attribute
    def code(self):
        return self.name.capitalize()


class IndicatorFactory(DjangoModelFactory):
    class Meta:
        model = Indicator

    activity_types = factory.RelatedFactory(ActivityTypeFactory)
    name = factory.Faker("word")
    numerator = factory.Faker("pystr", max_chars=200)
    denominator = factory.Faker("pystr", max_chars=200)
    description = factory.Faker("text", max_nb_chars=1200)

    @factory.lazy_attribute
    def code(self):
        return self.name.capitalize()


class ProjectFactory(DjangoModelFactory):
    class Meta:
        model = Project

    state = factory.Iterator(Project.PROJECT_STATES, getter=lambda c: c[0])
    active = factory.Faker("boolean")
    title = factory.Faker("sentence")
    code = factory.Faker("word")
    is_hrp_project = factory.Faker("boolean")
    has_hrp_code = factory.Faker("boolean")
    hrp_code = factory.Faker("word")
    clusters = factory.RelatedFactory(ClusterFactory)
    activity_domains = factory.RelatedFactory(ActivityDomainFactory)
    donors = factory.RelatedFactory(DonorFactory)
    implementing_partners = factory.RelatedFactory(OrganizationFactory)
    programme_partners = factory.RelatedFactory(OrganizationFactory)
    start_date = factory.Faker("date_time")
    end_date = factory.Faker("date_time")
    budget = factory.Faker("random_int")
    budget_received = factory.Faker("random_int")
    budget_gap = factory.Faker("random_int")
    # budget_currency = factory.SubFactory(CurrencyFactory)
    user = factory.SubFactory(UserFactory)
    description = factory.Faker("paragraph")
    old_id = factory.Faker("word")



class ActivityPlanFactory(DjangoModelFactory):
    class Meta:
        model = ActivityPlan

    project = factory.SubFactory(ProjectFactory)
    title = factory.Faker('sentence', nb_words=4)
    activity_domain = factory.SubFactory(ActivityDomainFactory)
    activity_type = factory.SubFactory(ActivityTypeFactory)
    activity_detail = factory.SubFactory(ActivityDetailFactory)
    beneficiary = factory.SubFactory(BeneficiaryTypeFactory)
    hrp_beneficiary = factory.SubFactory(BeneficiaryTypeFactory)
    # Add other fields if necessary
    
    
    
class LocationTypeFactory(DjangoModelFactory):
    class Meta:
        model = LocationType

    name = factory.Faker('word')
    
class TargetLocationFactory(DjangoModelFactory):
    class Meta:
        model = TargetLocation

    project = factory.SubFactory(ProjectFactory)
    activity_plan = factory.SubFactory(ActivityPlanFactory)
    title = factory.Faker('sentence', nb_words=4)
    country = factory.SubFactory(LocationFactory)
    province = factory.SubFactory(LocationFactory)
    district = factory.SubFactory(LocationFactory)
    zone = factory.SubFactory(LocationFactory)
    location_type = factory.SubFactory(LocationTypeFactory)
    implementing_partner = factory.SubFactory(OrganizationFactory)
    site_name = factory.Faker('word')
    site_lat = factory.Faker('latitude')
    site_long = factory.Faker('longitude')
    # Add other fields if necessary
    
class DisaggregationLocationFactory(DjangoModelFactory):
    class Meta:
        model = DisaggregationLocation

    active = factory.Faker('boolean')
    target_location = factory.SubFactory(TargetLocationFactory)
    disaggregation = factory.SubFactory(DisaggregationFactory)
    target = factory.Faker('random_int')