from django.contrib.auth.models import User
from django.db import models
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField

NAME_MAX_LENGTH = 200
DESCRIPTION_MAX_LENGTH = 600


# ##############################################
# ############## Reference Models ##############
# ##############################################


class Location(models.Model):
    """Locations Model"""

    LOCATION_CLASSIFICATIONS = [("urban", "Urban"), ("rural", "Rural")]

    LOCATION_TYPES = [
        ("All", "ALL"),
        ("Country", "Country"),
        ("Province", "Province"),
        ("District", "District"),
        ("Zone", "Zone"),
    ]
    parent = models.ForeignKey(
        "self",
        default=0,
        on_delete=models.CASCADE,
        related_name="children",
        blank=True,
        null=True,
    )
    code = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    level = models.IntegerField(default=0)
    original_name = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=15, choices=LOCATION_TYPES, default="Country", null=True, blank=True)
    classification = models.CharField(max_length=15, choices=LOCATION_CLASSIFICATIONS, null=True, blank=True)
    lat = models.FloatField(blank=True, null=True)
    long = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"({self.code}) {self.name}"


class Cluster(models.Model):
    """Clusters Model"""

    countries = models.ManyToManyField(Location, blank=True)

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    code = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    title = models.CharField(max_length=NAME_MAX_LENGTH)
    ocha_code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return f"[{self.code}] - {self.title}"


class BeneficiaryType(models.Model):
    """Beneficiary Types Model"""

    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    country = models.ForeignKey(
        Location,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    clusters = models.ManyToManyField(Cluster)
    is_hrp_beneficiary = models.BooleanField(default=False, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    description = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Beneficiary Type"
        verbose_name_plural = "Beneficiary Types"


class Organization(models.Model):
    """Organizations Model"""

    TYPE_CHOICES = [
        ("National NGO", "National NGO"),
        ("International NGO", "International NGO"),
        ("Government", "Government"),
        ("Business", "Business"),
    ]
    countries = models.ManyToManyField(Location, blank=True)
    clusters = models.ManyToManyField(Cluster, blank=True)

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    code = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    type = models.CharField(max_length=NAME_MAX_LENGTH, choices=TYPE_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    old_id = models.CharField("Old ID", max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.code


class Donor(models.Model):
    code = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    countries = models.ManyToManyField(Location, blank=True)
    clusters = models.ManyToManyField(Cluster, blank=True)

    old_id = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Donor"
        verbose_name_plural = "Donors"


class StrategicObjective(models.Model):
    """Objectives"""

    strategic_objective_name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    strategic_objective_description = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)
    output_objective_name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    sector_objective_name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    sector_objective_description = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)
    denominator = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.strategic_objective_name

    class Meta:
        verbose_name = "Objective"
        verbose_name_plural = "Objectives"


class Currency(models.Model):
    """Currencies model"""

    name = models.CharField(max_length=15, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"


class LocationType(models.Model):
    """Locations Types model"""

    name = models.CharField(max_length=15, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Location Type"
        verbose_name_plural = "Location Types"


class FacilitySiteType(models.Model):
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Facility Site Type"
        verbose_name_plural = "Facility Site Types"


class ImplementationModalityType(models.Model):
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Implementation Modality Type"
        verbose_name_plural = "Implementation Modality Types"


class TransferMechanismType(models.Model):
    modality = models.ForeignKey(ImplementationModalityType, on_delete=models.SET_NULL, blank=True, null=True)
    code = models.CharField(max_length=NAME_MAX_LENGTH)
    name = models.CharField(max_length=NAME_MAX_LENGTH,unique=True )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Transfer Mechanism Type"
        verbose_name_plural = "Transfer Mechanism Types"


class PackageType(models.Model):
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Package Type"
        verbose_name_plural = "Package Types"


class TransferCategory(models.Model):
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Transfer Category"
        verbose_name_plural = "Transfer Categories"


class GrantType(models.Model):
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Grant Type"
        verbose_name_plural = "Grant Types"


class UnitType(models.Model):
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Unit Type"
        verbose_name_plural = "Unit Types"


class ReportType(models.Model):
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Report Type"
        verbose_name_plural = "Report Types"


class ActivityDomain(models.Model):
    active = models.BooleanField(default=True)
    code = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    countries = models.ManyToManyField(Location)
    clusters = models.ManyToManyField(Cluster)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Activity Domain"
        verbose_name_plural = "Activity Domains"


class ActivityType(models.Model):
    activity_domain = models.ForeignKey(ActivityDomain, on_delete=models.SET_NULL, blank=True, null=True)
    active = models.BooleanField(default=True)
    code = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, unique=True)
    name = models.CharField(max_length=DESCRIPTION_MAX_LENGTH)
    countries = models.ManyToManyField(Location)
    clusters = models.ManyToManyField(Cluster)
    # indicators = models.ManyToManyField(Indicator)
    activity_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    hrp_code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    code_indicator = models.BooleanField(default=False, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    end_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    ocha_code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    objective = models.ForeignKey(StrategicObjective, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Activity Type"
        verbose_name_plural = "Activity Types"
        constraints = [
            models.UniqueConstraint(fields=["code", "activity_domain"], name="unique_activitytype_for_activity_domain")
        ]


class ActivityDetail(models.Model):
    activity_type = models.ForeignKey(ActivityType, on_delete=models.SET_NULL, blank=True, null=True)

    code = models.CharField(max_length=DESCRIPTION_MAX_LENGTH)
    name = models.CharField(max_length=DESCRIPTION_MAX_LENGTH)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Activity Detail"
        verbose_name_plural = "Activity Details"
        constraints = [
            models.UniqueConstraint(fields=["code", "activity_type"], name="unique_ActivityDetail_for_activity_type")
        ]


class Indicator(models.Model):
    activity_types = models.ManyToManyField(ActivityType)

    # code = models.CharField(max_length=600, unique=True)

    # This should be unique
    name = models.CharField(max_length=600)

    numerator = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    denominator = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    description = models.CharField(max_length=1200, blank=True, null=True)
    # Reference tables
    package_type = models.ForeignKey(PackageType, on_delete=models.SET_NULL, null=True, blank=True)
    unit_type = models.ForeignKey(UnitType, on_delete=models.SET_NULL, null=True, blank=True)
    grant_type = models.ForeignKey(GrantType, on_delete=models.SET_NULL, null=True, blank=True)
    transfer_category = models.ForeignKey(TransferCategory, on_delete=models.SET_NULL, null=True, blank=True)
    transfer_mechanism_type = models.ForeignKey(TransferMechanismType, on_delete=models.SET_NULL, null=True, blank=True)
    implement_modility_type = models.ForeignKey(
        ImplementationModalityType, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Indicator"
        verbose_name_plural = "Indicators"


# ##############################################
# ############## Project Planning ##############
# ##############################################


class Project(models.Model):
    """Projects model"""

    PROJECT_STATES = [
        ("draft", "Draft"),
        ("in-progress", "In Progress"),
        ("done", "Completed"),
        ("archive", "Archived"),
    ]
    state = models.CharField(max_length=15, choices=PROJECT_STATES, default="draft", null=True, blank=True)
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=NAME_MAX_LENGTH)
    code = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)

    is_hrp_project = models.BooleanField(default=False)
    has_hrp_code = models.BooleanField(default=False)
    hrp_code = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True, unique=True)

    clusters = models.ManyToManyField(Cluster)
    activity_domains = models.ManyToManyField(ActivityDomain, related_name="activity_domains")

    donors = models.ManyToManyField(Donor)
    implementing_partners = models.ManyToManyField(Organization, related_name="implementing_partners", blank=True)
    programme_partners = models.ManyToManyField(Organization, related_name="programme_partners", blank=True)

    # locations = models.ManyToManyField(Location)
    # country = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    # provinces = models.ManyToManyField(Location, related_name="provinces")
    # districts = models.ManyToManyField(Location, related_name="districts")

    start_date = models.DateTimeField("start date")
    end_date = models.DateTimeField("end date")
    budget = models.IntegerField(null=True, blank=True)
    budget_received = models.IntegerField(null=True, blank=True)
    budget_gap = models.IntegerField(null=True, blank=True)
    budget_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateField(auto_now=True, blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    old_id = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.title


class ActivityPlan(models.Model):
    """Activity Plans model"""

    CATEGORY_TYPES = [
        ("disabled", "Persons with Disabilities"),
        ("non-disabled", "Non-Disabled"),
    ]
    ACTIVITY_PLAN_STATES = [
        ("draft", "Draft"),
        ("in-progress", "In Progress"),
        ("done", "Completed"),
        ("archive", "Archived"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)
    state = models.CharField(
        max_length=15,
        choices=ACTIVITY_PLAN_STATES,
        null=True,
        blank=True,
        default="draft",
    )
    # title = models.CharField(max_length=800, null=True, blank=True)

    activity_domain = models.ForeignKey(ActivityDomain, on_delete=models.SET_NULL, null=True, blank=True)
    activity_type = ChainedForeignKey(
        ActivityType,
        chained_field="activity_domain",
        chained_model_field="activity_domain",
        show_all=False,
        auto_choose=True,
        null=True,
        blank=True,
        sort=True,
    )
    activity_detail = ChainedForeignKey(
        ActivityDetail,
        chained_field="activity_type",
        chained_model_field="activity_type",
        show_all=False,
        auto_choose=True,
        null=True,
        blank=True,
        sort=True,
    )
    indicator = ChainedForeignKey(
        Indicator,
        chained_field="activity_type",
        chained_model_field="activity_types",
        show_all=False,
        auto_choose=True,
        null=True,
        blank=True,
        sort=True,
    )

    beneficiary = models.ForeignKey(
        BeneficiaryType,
        related_name="beneficiary",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    hrp_beneficiary = models.ForeignKey(
        BeneficiaryType,
        related_name="hrp_beneficiary",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    beneficiary_category = models.CharField(
        max_length=15, choices=CATEGORY_TYPES, default="non-disabled", null=True, blank=True
    )

    # Facility Monitoring
    # facility_monitoring = models.BooleanField(default=False)
    # facility_name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True, )
    # facility_id = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True, )
    # facility_type = models.ForeignKey(FacilitySiteType, on_delete=models.SET_NULL, null=True, blank=True)
    # facility_lat = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)
    # facility_long = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)

    total_target = models.IntegerField(default=0, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    # old_id = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return f"Project {self.project.code} - Activity Plan"

    class Meta:
        verbose_name = "Activity Plan"
        verbose_name_plural = "Activity Plans"


class TargetLocation(models.Model):
    """Target Locations model"""

    TARGET_LOCATIONS_STATES = [
        ("draft", "Draft"),
        ("in-progress", "In Progress"),
        ("done", "Completed"),
        ("archive", "Archived"),
    ]
    LOCATIONS_GROUP = [
        ("province", "Province/State"),
        ("district", "District"),
    ]
    TARGET_CLASSIFICATION = [
        ("urban", "Urban"),
        ("rural", "Rural"),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    activity_plan = models.ForeignKey(ActivityPlan, on_delete=models.CASCADE, null=True, blank=True)

    active = models.BooleanField(default=True)
    state = models.CharField(
        max_length=15,
        choices=TARGET_LOCATIONS_STATES,
        default="draft",
        null=True,
        blank=True,
    )
    locations_group_by = models.CharField(max_length=15, choices=LOCATIONS_GROUP, null=True, blank=True)
    group_by_province = models.BooleanField(default=True)
    group_by_district = models.BooleanField(default=True)
    group_by_custom = models.BooleanField(default=True)

    country = models.ForeignKey(
        Location,
        related_name="target_country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    province = models.ForeignKey(
        Location,
        related_name="target_province",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    district = models.ForeignKey(
        Location,
        related_name="target_district",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    zone = models.ForeignKey(
        Location,
        related_name="target_zones",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    location_type = models.ForeignKey(LocationType, on_delete=models.SET_NULL, null=True, blank=True)
    classification = models.CharField(max_length=15, choices=TARGET_CLASSIFICATION, blank=True, null=True)

    implementing_partner = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)

    facility_site_type = models.ForeignKey(FacilitySiteType, on_delete=models.SET_NULL, null=True)

    site_monitoring = models.BooleanField(default=False)
    site_name = models.CharField(max_length=255, blank=True, null=True)
    site_lat = models.CharField(max_length=255, blank=True, null=True)
    site_long = models.CharField(max_length=255, blank=True, null=True)
    old_id = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    disaggregations = models.ManyToManyField("Disaggregation", through="DisaggregationLocation",
                                          related_name="disaggregations")

    def __str__(self):
        return f"{self.project}, {self.province}, {self.district}"

    class Meta:
        verbose_name = "Target Location"
        verbose_name_plural = "Target Locations"


class Disaggregation(models.Model):
    clusters = models.ManyToManyField(Cluster)
    indicators = models.ManyToManyField(Indicator)

    name = models.CharField(max_length=NAME_MAX_LENGTH)
    type = models.CharField(max_length=NAME_MAX_LENGTH)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class DisaggregationLocation(models.Model):
    active = models.BooleanField(default=True)
    target_location = models.ForeignKey(TargetLocation, on_delete=models.CASCADE, null=True, blank=True)
    disaggregation = models.ForeignKey(Disaggregation, on_delete=models.CASCADE, null=True, blank=True)

    target = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return f"{self.disaggregation.name}"


# ##############################################
# ##### Project Budget Progress Reporting ######
# ##############################################


class BudgetProgress(models.Model):
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    donor = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)
    activity_domain = models.ForeignKey(ActivityDomain, on_delete=models.SET_NULL, null=True, blank=True)
    grant = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)
    amount_recieved = models.IntegerField(default=0, blank=True, null=True)
    budget_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    received_date = models.DateField(blank=True, null=True)
    country = models.ForeignKey(
        Location,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.donor}, {self.activity_domain}"

    class Meta:
        verbose_name = "Budget Progress"
        verbose_name_plural = "Budget Progress"
