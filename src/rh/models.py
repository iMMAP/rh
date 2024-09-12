from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinLengthValidator, MinValueValidator
from django.db import models

NAME_MAX_LENGTH = 200
DESCRIPTION_MAX_LENGTH = 600


# ##############################################
# ############## Reference Models ##############
# ##############################################


class Location(models.Model):
    """Locations Model"""

    class Meta:
        ordering = ["name"]

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
    code = models.SlugField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    level = models.IntegerField(default=0)
    original_name = models.CharField(max_length=200, blank=True, null=True)
    region_name = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=15, choices=LOCATION_TYPES, default="Country", null=True, blank=True)
    classification = models.CharField(max_length=15, choices=LOCATION_CLASSIFICATIONS, null=True, blank=True)
    lat = models.FloatField(blank=True, null=True)
    long = models.FloatField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Cluster(models.Model):
    """Clusters Model"""

    countries = models.ManyToManyField(Location, blank=True, limit_choices_to={"level": 0})

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    code = models.SlugField(max_length=NAME_MAX_LENGTH, unique=True)
    title = models.CharField(max_length=NAME_MAX_LENGTH)
    ocha_code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"[{self.code}] - {self.title}"

    class Meta:
        permissions = [
            ("activate_deactivate_cluster_users", "activate/deactivate cluster users"),
        ]


class BeneficiaryType(models.Model):
    """Beneficiary Types Model"""

    country = models.ForeignKey(
        Location,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"level": 0},
    )

    clusters = models.ManyToManyField(Cluster)

    name = models.CharField(max_length=NAME_MAX_LENGTH)
    code = models.SlugField(max_length=NAME_MAX_LENGTH)

    description = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)
    is_active = models.BooleanField(default=False)

    TYPE = [("hrp", "HRP"), ("non-hrp", "Non-HRP")]
    type = models.CharField(max_length=NAME_MAX_LENGTH, choices=TYPE)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"[{self.type}] {self.name}"

    class Meta:
        verbose_name = "Beneficiary Type"
        verbose_name_plural = "Beneficiary Types"


class Organization(models.Model):
    """Organizations Model"""

    class Meta:
        ordering = ["code"]
        permissions = [
            ("activate_deactivate_user", "Activate/Deactivate users of organization"),
        ]

    TYPE_CHOICES = [
        ("National NGO", "National NGO"),
        ("International NGO", "International NGO"),
        ("Government", "Government"),
        ("Business", "Business"),
    ]
    countries = models.ManyToManyField(Location, blank=True, limit_choices_to={"level": 0})
    clusters = models.ManyToManyField(Cluster, blank=True)

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    code = models.SlugField(max_length=NAME_MAX_LENGTH, unique=True)
    type = models.CharField(max_length=NAME_MAX_LENGTH, choices=TYPE_CHOICES, blank=True, null=True)

    old_id = models.CharField("Old ID", max_length=NAME_MAX_LENGTH, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.code


class Donor(models.Model):
    code = models.SlugField(max_length=NAME_MAX_LENGTH, unique=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    countries = models.ManyToManyField(Location, limit_choices_to={"level": 0})

    clusters = models.ManyToManyField(Cluster, blank=True)

    old_id = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Donor"
        verbose_name_plural = "Donors"


class Currency(models.Model):
    """Currencies model"""

    name = models.CharField(max_length=15, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"


class LocationType(models.Model):
    """Locations Types model"""

    name = models.CharField(max_length=15, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Location Type"
        verbose_name_plural = "Location Types"


class FacilitySiteType(models.Model):
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Facility Site Type"
        verbose_name_plural = "Facility Site Types"


class ImplementationModalityType(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Implementation Modality Type"
        verbose_name_plural = "Implementation Modality Types"


class TransferMechanismType(models.Model):
    modality = models.ForeignKey(ImplementationModalityType, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Transfer Mechanism Type"
        verbose_name_plural = "Transfer Mechanism Types"


class PackageType(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Package Type"
        verbose_name_plural = "Package Types"


class TransferCategory(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Transfer Category"
        verbose_name_plural = "Transfer Categories"


class GrantType(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Grant Type"
        verbose_name_plural = "Grant Types"


class UnitType(models.Model):
    code = models.SlugField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Unit Type"
        verbose_name_plural = "Unit Types"


class ActivityDomain(models.Model):
    countries = models.ManyToManyField(Location, limit_choices_to={"level": 0})
    clusters = models.ManyToManyField(Cluster)

    name = models.CharField(max_length=NAME_MAX_LENGTH)
    code = models.SlugField(max_length=NAME_MAX_LENGTH, unique=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Activity Domain"
        verbose_name_plural = "Activity Domains"


class ActivityType(models.Model):
    activity_domain = models.ForeignKey(ActivityDomain, on_delete=models.SET_NULL, blank=True, null=True)

    name = models.CharField(max_length=DESCRIPTION_MAX_LENGTH)
    code = models.SlugField(max_length=DESCRIPTION_MAX_LENGTH, unique=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

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

    code = models.SlugField(max_length=DESCRIPTION_MAX_LENGTH)
    name = models.CharField(max_length=DESCRIPTION_MAX_LENGTH)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

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

    enable_retargeting = models.BooleanField(blank=True, null=True)

    # RELATIONSHIPS
    package_type = models.ForeignKey(PackageType, on_delete=models.SET_NULL, null=True, blank=True)
    unit_type = models.ForeignKey(UnitType, on_delete=models.SET_NULL, null=True, blank=True)
    units = models.IntegerField(default=0, null=True, blank=True)
    no_of_transfers = models.IntegerField(
        default=0, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(30)]
    )
    grant_type = models.ForeignKey(GrantType, on_delete=models.SET_NULL, null=True, blank=True)
    transfer_category = models.ForeignKey(TransferCategory, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    transfer_mechanism_type = models.ForeignKey(TransferMechanismType, on_delete=models.SET_NULL, null=True, blank=True)
    implement_modility_type = models.ForeignKey(
        ImplementationModalityType, on_delete=models.SET_NULL, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Indicator"
        verbose_name_plural = "Indicators"


# ##############################################
# ############## Project Planning ##############
# ##############################################

STATES = [
    ("draft", "Draft"),
    ("in-progress", "In-progress"),
    ("completed", "Completed"),
    ("archived", "Archived"),
]


class Project(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)

    clusters = models.ManyToManyField(Cluster)
    activity_domains = models.ManyToManyField(ActivityDomain, related_name="activity_domains")

    donors = models.ManyToManyField(Donor, blank=True)
    implementing_partners = models.ManyToManyField(Organization, related_name="implementing_partners", blank=True)
    programme_partners = models.ManyToManyField(Organization, related_name="programme_partners", blank=True)

    state = models.CharField(max_length=15, choices=STATES, default="draft", null=True, blank=True)

    title = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, validators=[MinLengthValidator(6)])
    code = models.SlugField(max_length=NAME_MAX_LENGTH, unique=True)

    is_hrp_project = models.BooleanField(default=False)
    hrp_code = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True, unique=True)

    budget_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    budget = models.IntegerField(null=True, blank=True)
    budget_received = models.IntegerField(null=True, blank=True)
    budget_gap = models.IntegerField(null=True, blank=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True)
    old_id = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    start_date = models.DateTimeField("start date")
    end_date = models.DateTimeField("end date")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("archive_unarchive_project", "Archive/UnArchive project"),
            ("view_org_projects", "View your organization's projects"),
            ("export_org_projects", "View your organization's projects"),
            ("view_cluster_projects", "View your clusters projects"),
            ("export_cluster_projects", "Export your clusters projects"),
            ("copy_project", "Can copy project"),
            ("review_project_activity_plan_review", "Can view a project's activity plan review"),
            ("submit_project", "Can submit a project"),
        ]


class ActivityPlan(models.Model):
    """Activity Plans model"""

    CATEGORY_TYPES = [
        ("disabled", "Persons with Disabilities"),
        ("non-disabled", "Non-Disabled"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    state = models.CharField(max_length=15, choices=STATES, null=True, default="draft")

    activity_domain = models.ForeignKey(ActivityDomain, on_delete=models.DO_NOTHING)
    activity_type = models.ForeignKey(ActivityType, on_delete=models.DO_NOTHING)
    activity_detail = models.ForeignKey(ActivityDetail, on_delete=models.DO_NOTHING, null=True, blank=True)
    indicator = models.ForeignKey(Indicator, on_delete=models.DO_NOTHING)

    beneficiary = models.ForeignKey(
        BeneficiaryType,
        related_name="beneficiary",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"type": "non-hrp"},
    )
    hrp_beneficiary = models.ForeignKey(
        BeneficiaryType,
        related_name="hrp_beneficiary",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"type": "hrp"},
    )
    beneficiary_category = models.CharField(
        max_length=15, choices=CATEGORY_TYPES, default="non-disabled", null=True, blank=True
    )

    description = models.TextField(blank=True, null=True)
    # old_id = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    package_type = models.ForeignKey(PackageType, on_delete=models.SET_NULL, null=True, blank=True)
    unit_type = models.ForeignKey(UnitType, on_delete=models.SET_NULL, null=True, blank=True)
    units = models.IntegerField(default=0, null=True, blank=True)
    no_of_transfers = models.IntegerField(
        default=0, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(30)]
    )
    grant_type = models.ForeignKey(GrantType, on_delete=models.SET_NULL, null=True, blank=True)
    transfer_category = models.ForeignKey(TransferCategory, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    transfer_mechanism_type = models.ForeignKey(TransferMechanismType, on_delete=models.SET_NULL, null=True, blank=True)
    implement_modility_type = models.ForeignKey(
        ImplementationModalityType, on_delete=models.SET_NULL, null=True, blank=True
    )

    def get_available_states(self):
        return [state[0] for state in STATES]

    def __str__(self):
        return f"Activity Plan: {self.activity_domain} - {self.indicator}"

    class Meta:
        verbose_name = "Activity Plan"
        verbose_name_plural = "Activity Plans"


class TargetLocation(models.Model):
    """Target Locations model"""

    LOCATIONS_GROUP = [
        ("province", "Province/State"),
        ("district", "District"),
    ]
    TARGET_CLASSIFICATION = [
        ("urban", "Urban"),
        ("rural", "Rural"),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    activity_plan = models.ForeignKey(ActivityPlan, on_delete=models.CASCADE)

    state = models.CharField(max_length=15, choices=STATES, default="draft", null=True)

    country = models.ForeignKey(
        Location, related_name="target_country", on_delete=models.SET_NULL, null=True, limit_choices_to={"level": 0}
    )
    province = models.ForeignKey(
        Location, related_name="target_province", on_delete=models.SET_NULL, null=True, limit_choices_to={"level": 1}
    )
    district = models.ForeignKey(
        Location,
        related_name="target_district",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"level": 2},
    )
    zone = models.ForeignKey(
        Location,
        related_name="target_zones",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"level": 3},
    )
    location_type = models.ForeignKey(LocationType, on_delete=models.SET_NULL, null=True, blank=True)

    implementing_partner = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)

    # Facility Monitoring
    facility_site_type = models.ForeignKey(FacilitySiteType, on_delete=models.SET_NULL, null=True, blank=True)
    facility_monitoring = models.BooleanField(default=False, null=True, blank=True)
    facility_name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    facility_id = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    facility_lat = models.FloatField(null=True, blank=True)
    facility_long = models.FloatField(null=True, blank=True)

    disaggregations = models.ManyToManyField(
        "Disaggregation", through="DisaggregationLocation", related_name="disaggregations"
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    nhs_code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def get_available_states(self):
        return [state[0] for state in STATES]

    def __str__(self):
        return f"Target Location: {self.province}, {self.district}"

    class Meta:
        verbose_name = "Target Location"
        verbose_name_plural = "Target Locations"


class Disaggregation(models.Model):
    clusters = models.ManyToManyField(Cluster)
    indicators = models.ManyToManyField(Indicator)

    name = models.CharField(max_length=NAME_MAX_LENGTH)
    Gender = [("Male", "male"), ("Female", "female"), ("Other", "other")]
    gender = models.CharField(max_length=NAME_MAX_LENGTH, choices=Gender, null=True)

    lower_limit = models.IntegerField(default=0, blank=True, null=True)
    upper_limit = models.IntegerField(default=0, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


class DisaggregationLocation(models.Model):
    target_location = models.ForeignKey(TargetLocation, on_delete=models.CASCADE)
    disaggregation = models.ForeignKey(Disaggregation, on_delete=models.CASCADE)

    target = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        unique_together = ("target_location", "disaggregation")

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

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.donor}, {self.activity_domain}"

    class Meta:
        verbose_name = "Budget Progress"
        verbose_name_plural = "Budget Progress"


class ProjectIndicatorType(models.Model):
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    indicator = models.ForeignKey(Indicator, on_delete=models.SET_NULL, null=True, blank=True)

    package_type = models.ForeignKey(PackageType, on_delete=models.SET_NULL, null=True, blank=True)
    unit_type = models.ForeignKey(UnitType, on_delete=models.SET_NULL, null=True, blank=True)
    grant_type = models.ForeignKey(GrantType, on_delete=models.SET_NULL, null=True, blank=True)
    transfer_category = models.ForeignKey(TransferCategory, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    transfer_mechanism_type = models.ForeignKey(TransferMechanismType, on_delete=models.SET_NULL, null=True, blank=True)
    implement_modility_type = models.ForeignKey(
        ImplementationModalityType, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.project
