import factory
import random

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
    DisaggregationLocation,
    GrantType,
    TransferCategory,
    TransferMechanismType,
    ImplementationModalityType,
    UnitType,
    PackageType,
)
from users.factory import UserFactory

FAKE = faker.Faker()

D_TYPES = [
    ("age", "Age"),
    ("gender", "Gender"),
]

# Run the bellow command in the shell to create fake data
# DisaggregationFactory.create_batch(amount)


# unit_type
class UnitTypeFactory(DjangoModelFactory):
    class Meta:
        model = UnitType

    name = factory.Faker("word")


# grant_type
class GrantTypeFactory(DjangoModelFactory):
    class Meta:
        model = GrantType

    name = factory.Faker("word")


# transfer_category
class TransferCategoryFactory(DjangoModelFactory):
    class Meta:
        model = TransferCategory

    name = factory.Faker("word")




# implement_modility_type
class ImplementationModalityTypeFactory(DjangoModelFactory):
    class Meta:
        model = ImplementationModalityType

    name = factory.Faker("word")


# transfer_mechanism_type
class TransferMechanismTypeFactory(DjangoModelFactory):
    class Meta:
        model = TransferMechanismType

    name = factory.Faker("word")
    modality = factory.SubFactory(ImplementationModalityTypeFactory)


class PackageTypeFactory(DjangoModelFactory):
    class Meta:
        model = PackageType

    name = factory.Faker("word")


class DisaggregationFactory(DjangoModelFactory):
    class Meta:
        model = Disaggregation

    name = factory.Faker("word")
    type = factory.Iterator(D_TYPES, getter=lambda c: c[0])

    @factory.post_generation
    def indicators(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for indic in extracted:
                self.clusters.add(indic)
        else:
            indics = Indicator.objects.order_by("?")[:3]
            for indic in indics:
                self.indicators.add(indic)



    # Run the bellow command in the shell to create fake data
    # DisaggregationFactory.create_batch(amount)




class CountryFactory(DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Faker("country")
    level = 0
    type = "Country"
    classification = "urban"
    lat = factory.Faker("latitude")
    long = factory.Faker("longitude")
    parent = factory.LazyAttribute(lambda obj: None)

    @factory.lazy_attribute
    def original_name(self):
        return self.name

    @factory.lazy_attribute
    def code(self):
        return f"{self.name.capitalize()}-{self.level}-{random.randint(1, 100)}"


class Admin1Factory(DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Faker("city")
    level = 1
    type = "Province"
    classification = factory.Iterator(Location.LOCATION_CLASSIFICATIONS, getter=lambda c: c[0])
    lat = factory.Faker("latitude")
    long = factory.Faker("longitude")
    parent = factory.Iterator(Location.objects.filter(level=0))

    @factory.lazy_attribute
    def original_name(self):
        return self.name

    @factory.lazy_attribute
    def code(self):
        return f"{self.name.capitalize()}-{self.level}-{random.randint(1, 100)}"


class Admin2Factory(DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Faker("street_name")
    level = 2
    type = "District"
    classification = factory.Iterator(Location.LOCATION_CLASSIFICATIONS, getter=lambda c: c[0])
    lat = factory.Faker("latitude")
    long = factory.Faker("longitude")
    parent = factory.Iterator(Location.objects.filter(level=1))

    @factory.lazy_attribute
    def original_name(self):
        return self.name

    @factory.lazy_attribute
    def code(self):
        return f"{self.name.capitalize()}-{self.level}-{random.randint(1, 100)}"


class Admin3Factory(DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Faker("street_suffix")
    level = 3
    type = "Zone"
    classification = factory.Iterator(Location.LOCATION_CLASSIFICATIONS, getter=lambda c: c[0])
    lat = factory.Faker("latitude")
    long = factory.Faker("longitude")
    parent = factory.Iterator(Location.objects.filter(level=2))

    @factory.lazy_attribute
    def original_name(self):
        return self.name

    @factory.lazy_attribute
    def code(self):
        return f"{self.name.capitalize()}-{self.level}-{random.randint(1, 100)}"


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
            locations = Location.objects.filter(level=0)

            for location in locations:
                self.countries.add(location)


class BeneficiaryTypeFactory(DjangoModelFactory):
    class Meta:
        model = BeneficiaryType

    name = factory.Faker("word")
    code = factory.Faker("word")
    country = factory.SubFactory(CountryFactory)
    is_hrp_beneficiary = factory.Faker("boolean")
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
            clusters = Cluster.objects.order_by("?")[:2]
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
            countries = Location.objects.filter(level=0)
            for country in countries:
                self.countries.add(country)

    @factory.post_generation
    def clusters(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for cluster in extracted:
                self.clusters.add(cluster)
        else:
            clusters = Cluster.objects.order_by("?")[:2]
            for cluster in clusters:
                self.clusters.add(cluster)


class DonorFactory(DjangoModelFactory):
    class Meta:
        model = Donor

    name = factory.Faker("company")

    @factory.post_generation
    def countries(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for country in extracted:
                self.countries.add(country)
        else:
            countries = Location.objects.filter(level=0)
            for country in countries:
                self.countries.add(country)

    @factory.post_generation
    def clusters(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for cluster in extracted:
                self.clusters.add(cluster)
        else:
            clusters = Cluster.objects.order_by("?")[:2]
            for cluster in clusters:
                self.clusters.add(cluster)

    @factory.lazy_attribute
    def code(self):
        return self.name.capitalize()


class ActivityDomainFactory(DjangoModelFactory):
    class Meta:
        model = ActivityDomain

    active = factory.Faker("boolean")
    code = factory.Faker("pystr", max_chars=10)
    name = factory.Faker("word")

    @factory.post_generation
    def countries(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for country in extracted:
                self.countries.add(country)
        else:
            countries = Location.objects.filter(level=0)
            for country in countries:
                self.countries.add(country)

    @factory.post_generation
    def clusters(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for cluster in extracted:
                self.clusters.add(cluster)
        else:
            clusters = Cluster.objects.order_by("?")[:2]
            for cluster in clusters:
                self.clusters.add(cluster)


class ActivityTypeFactory(DjangoModelFactory):
    class Meta:
        model = ActivityType

    activity_domain = factory.Iterator(ActivityDomain.objects.all())

    active = factory.Faker("boolean")
    code = factory.Faker("pystr", max_chars=600)
    name = factory.Faker("word")

    activity_date = factory.Faker("date_time")
    hrp_code = factory.Faker("pystr", max_chars=200)
    code_indicator = factory.Faker("boolean")
    ocha_code = factory.Faker("pystr", max_chars=200)

    start_date = factory.Faker("date_time_this_decade", tzinfo=pytz.UTC)
    end_date = factory.Faker("date_time_this_decade", tzinfo=pytz.UTC)

    @factory.post_generation
    def countries(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for country in extracted:
                self.countries.add(country)
        else:
            countries = Location.objects.filter(level=0)
            for country in countries:
                self.countries.add(country)

    @factory.post_generation
    def clusters(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for cluster in extracted:
                self.clusters.add(cluster)
        else:
            clusters = Cluster.objects.order_by("?")[:2]
            for cluster in clusters:
                self.clusters.add(cluster)


class ActivityDetailFactory(DjangoModelFactory):
    class Meta:
        model = ActivityDetail

    name = factory.Faker("word")

    activity_type = factory.Iterator(ActivityType.objects.all())

    @factory.lazy_attribute
    def code(self):
        return self.name.capitalize()


class IndicatorFactory(DjangoModelFactory):
    class Meta:
        model = Indicator

    name = factory.Faker("word")
    numerator = factory.Faker("pystr", max_chars=200)
    denominator = factory.Faker("pystr", max_chars=200)
    description = factory.Faker("text", max_nb_chars=1200)

    package_type = factory.SubFactory(PackageTypeFactory)
    unit_type = factory.SubFactory(UnitTypeFactory)
    grant_type = factory.SubFactory(GrantTypeFactory)
    transfer_category = factory.SubFactory(TransferCategoryFactory)
    implement_modility_type = factory.SubFactory(ImplementationModalityTypeFactory)
    transfer_mechanism_type = factory.SubFactory(TransferMechanismTypeFactory)

    @factory.post_generation
    def activity_types(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for activity_type in extracted:
                self.activity_types.add(activity_type)
        else:
            activity_types = ActivityType.objects.all()
            for activity_type in activity_types:
                self.activity_types.add(activity_type)

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

    # clusters = factory.RelatedFactory(ClusterFactory)
    # activity_domains = factory.RelatedFactory(ActivityDomainFactory)
    # donors = factory.RelatedFactory(DonorFactory)
    # implementing_partners = factory.RelatedFactory(OrganizationFactory)
    # programme_partners = factory.RelatedFactory(OrganizationFactory)

    start_date = factory.Faker("date_time_this_decade", tzinfo=pytz.UTC)
    end_date = factory.Faker("date_time_this_decade", tzinfo=pytz.UTC)
    budget = factory.Faker("random_int")
    budget_received = factory.Faker("random_int")
    budget_gap = factory.Faker("random_int")
    # budget_currency = factory.SubFactory(CurrencyFactory)
    user = factory.SubFactory(UserFactory)
    description = factory.Faker("paragraph")
    old_id = factory.Faker("word")

    @factory.post_generation
    def activity_plans(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for activity_plan in extracted:
                self.activityplan_set.add(activity_plan)
        else:
            for _ in range(random.randint(1, 7)):
                self.activityplan_set.add(ActivityPlanFactory(project=self))

    @factory.post_generation
    def clusters(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for cluster in extracted:
                self.clusters.add(cluster)
        else:
            clusters = Cluster.objects.order_by("?")[: random.randint(1, 5)]
            for cluster in clusters:
                self.clusters.add(cluster)

    @factory.post_generation
    def activity_domains(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for activity_domain in extracted:
                self.activity_domains.add(activity_domain)
        else:
            activity_domains = ActivityDomain.objects.all()[: random.randint(1, 5)]
            for ad in activity_domains:
                self.activity_domains.add(ad)

    @factory.post_generation
    def donors(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for donor in extracted:
                self.donors.add(donor)
        else:
            donors = Donor.objects.all()[: random.randint(1, 5)]
            for d in donors:
                self.donors.add(d)

    @factory.post_generation
    def implementing_partners(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for partner in extracted:
                self.implementing_partners.add(partner)
        else:
            orgs = Organization.objects.all()[: random.randint(1, 5)]
            for org in orgs:
                self.implementing_partners.add(org)

    @factory.post_generation
    def programme_partners(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for partner in extracted:
                self.programme_partners.add(partner)
        else:
            orgs = Organization.objects.all()[: random.randint(1, 5)]
            for org in orgs:
                self.programme_partners.add(org)


class ActivityPlanFactory(DjangoModelFactory):
    class Meta:
        model = ActivityPlan

    project = factory.SubFactory(ProjectFactory)

    # title = factory.Faker("sentence", nb_words=4)

    activity_domain = factory.Iterator(ActivityDomain.objects.all())

    activity_type = factory.Iterator(ActivityType.objects.all())

    activity_detail = factory.Iterator(ActivityDetail.objects.all())

    beneficiary = factory.Iterator(BeneficiaryType.objects.all())

    hrp_beneficiary = factory.Iterator(BeneficiaryType.objects.filter(is_hrp_beneficiary=True))
    # Add other fields if necessary

    @factory.post_generation
    def indicator(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            return
        else:
            self.indicator = self.activity_type.indicator_set.order_by("?")[:1][0]




class LocationTypeFactory(DjangoModelFactory):
    class Meta:
        model = LocationType

    name = factory.Faker("word")


class TargetLocationFactory(DjangoModelFactory):
    class Meta:
        model = TargetLocation

    project = factory.SubFactory(ProjectFactory)

    # activity_plan = factory.SubFactory(ActivityPlanFactory)
    activity_plan = factory.SubFactory(ActivityPlanFactory, project=factory.SelfAttribute("..project"))

    title = factory.Faker("sentence", nb_words=4)

    country = factory.Iterator(Location.objects.filter(level=0))
    province = factory.Iterator(Location.objects.filter(level=1))
    district = factory.Iterator(Location.objects.filter(level=2))
    zone = factory.Iterator(Location.objects.filter(level=3))

    location_type = factory.SubFactory(LocationTypeFactory)

    implementing_partner = factory.Iterator(Organization.objects.all())

    site_name = factory.Faker("word")
    site_lat = factory.Faker("latitude")
    site_long = factory.Faker("longitude")
    # Add other fields if necessary


class DisaggregationLocationFactory(DjangoModelFactory):
    class Meta:
        model = DisaggregationLocation

    active = factory.Faker("boolean")
    target_location = factory.SubFactory(TargetLocationFactory)
    disaggregation = factory.SubFactory(DisaggregationFactory)
    target = factory.Faker("random_int")
