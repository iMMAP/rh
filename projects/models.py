from django.db import models

from django.contrib.auth.models import User
from django.db import models
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField

from rh.models import Organization,Donor,Cluster,Location,Currency,LocationType
from activities.models import Disaggregation,ActivityDomain,ActivityDetail,ActivityType,Indicator,BeneficiaryType,FacilitySiteType

NAME_MAX_LENGTH = 200
DESCRIPTION_MAX_LENGTH = 600
# Create your models here.


class Project(models.Model):
    """Projects model"""

    PROJECT_STATES = [
        ('draft', 'Draft'),
        ('in-progress', 'In Progress'),
        ('done', 'Completed'),
        ('archive', 'Archived'),
    ]
    state = models.CharField(
        max_length=15,
        choices=PROJECT_STATES,
        default='draft', null=True, blank=True
    )
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=NAME_MAX_LENGTH)
    code = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)

    is_hrp_project = models.BooleanField(default=False)
    has_hrp_code = models.BooleanField(default=False)
    hrp_code = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)

    clusters = models.ManyToManyField(Cluster)
    activity_domains = models.ManyToManyField(ActivityDomain, related_name="activity_domains")

    donors = models.ManyToManyField(Donor)
    implementing_partners = models.ManyToManyField(Organization, related_name="implementing_partners")
    programme_partners = models.ManyToManyField(Organization, related_name="programme_partners")

    # locations = models.ManyToManyField(Location)
    # country = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    # provinces = models.ManyToManyField(Location, related_name="provinces")
    # districts = models.ManyToManyField(Location, related_name="districts")

    start_date = models.DateTimeField('start date')
    end_date = models.DateTimeField('end date')
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
        ('disabled', 'Persons with Disabilities'),
        ('non-disabled', 'Non-Disabled'),
    ]
    ACTIVITY_PLAN_STATES = [
        ('draft', 'Draft'),
        ('in-progress', 'In Progress'),
        ('done', 'Completed'),
        ('archive', 'Archived'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)
    state = models.CharField(
        max_length=15,
        choices=ACTIVITY_PLAN_STATES,
        null=True, blank=True, default='draft'
    )
    title = models.CharField(max_length=800, null=True, blank=True)

    activity_domain = models.ForeignKey(ActivityDomain, on_delete=models.SET_NULL, null=True, blank=True)
    activity_type = ChainedForeignKey(
        ActivityType,
        chained_field="activity_domain",
        chained_model_field="activity_domain",
        show_all=False,
        auto_choose=True,
        null=True, blank=True,
        sort=True)
    activity_detail = ChainedForeignKey(
        ActivityDetail,
        chained_field="activity_type",
        chained_model_field='activity_type',
        show_all=False,
        auto_choose=True,
        null=True, blank=True,
        sort=True)
    indicators = ChainedManyToManyField(
        Indicator,
        blank=True,
        chained_field="activity_type",
        chained_model_field="activity_types",
    )

    beneficiary = models.ForeignKey(BeneficiaryType, related_name="beneficiary", on_delete=models.SET_NULL, null=True, blank=True)
    hrp_beneficiary = models.ForeignKey(BeneficiaryType, related_name="hrp_beneficiary", on_delete=models.SET_NULL, null=True, blank=True)
    beneficiary_category = models.CharField(
        max_length=15,
        choices=CATEGORY_TYPES,
        default=False, null=True, blank=True
    )

    # Facility Monitoring
    facility_monitoring = models.BooleanField(default=False)
    facility_name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True, )
    facility_id = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True, )
    facility_type = models.ForeignKey(FacilitySiteType, on_delete=models.SET_NULL, null=True, blank=True)
    facility_lat = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)
    facility_long = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)

    age_desegregation = models.BooleanField(default=False)
    female_0_5 = models.IntegerField(default=0, blank=True, null=True)
    female_6_12 = models.IntegerField(default=0, blank=True, null=True)
    female_12_17 = models.IntegerField(default=0, blank=True, null=True)
    female_18 = models.IntegerField(default=0, blank=True, null=True)
    female_total = models.IntegerField(default=0, blank=True, null=True)

    male_0_5 = models.IntegerField(default=0, blank=True, null=True)
    male_6_12 = models.IntegerField(default=0, blank=True, null=True)
    male_12_17 = models.IntegerField(default=0, blank=True, null=True)
    male_18 = models.IntegerField(default=0, blank=True, null=True)
    male_total = models.IntegerField(default=0, blank=True, null=True)

    other_0_5 = models.IntegerField(default=0, blank=True, null=True)
    other_6_12 = models.IntegerField(default=0, blank=True, null=True)
    other_12_17 = models.IntegerField(default=0, blank=True, null=True)
    other_18 = models.IntegerField(default=0, blank=True, null=True)
    other_total = models.IntegerField(default=0, blank=True, null=True)

    total_0_5 = models.IntegerField(default=0, blank=True, null=True)
    total_6_12 = models.IntegerField(default=0, blank=True, null=True)
    total_12_17 = models.IntegerField(default=0, blank=True, null=True)
    total_18 = models.IntegerField(blank=True, null=True)

    total = models.IntegerField(default=0, blank=True, null=True)

    households = models.IntegerField(default=0, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    old_id = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return f"{self.project}"

    class Meta:
        verbose_name = 'Activity Plan'
        verbose_name_plural = "Activity Plans"

class TargetLocation(models.Model):
    """Target Locations model"""

    TARGET_LOCATIONS_STATES = [
        ('draft', 'Draft'),
        ('in-progress', 'In Progress'),
        ('done', 'Completed'),
        ('archive', 'Archived'),
    ]
    LOCATIONS_GROUP = [
        ('province', 'Province/State'),
        ('district', 'District'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)
    state = models.CharField(
        max_length=15,
        choices=TARGET_LOCATIONS_STATES,
        default='draft', null=True, blank=True
    )
    title = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)
    locations_group_by = models.CharField(
        max_length=15,
        choices=LOCATIONS_GROUP,
        null=True, blank=True
    )
    group_by_province = models.BooleanField(default=True)
    group_by_district = models.BooleanField(default=True)
    group_by_custom = models.BooleanField(default=True)

    country = models.ForeignKey(Location, related_name='target_country', on_delete=models.SET_NULL, null=True,
                                blank=True)
    province = models.ForeignKey(Location, related_name='target_province', on_delete=models.SET_NULL, null=True,
                                 blank=True)
    district = models.ForeignKey(Location, related_name='target_district', on_delete=models.SET_NULL, null=True,
                                 blank=True)
    zone = models.ForeignKey(Location, related_name='target_zones', on_delete=models.SET_NULL, null=True,
                                 blank=True)
    location_type = models.ForeignKey(LocationType, on_delete=models.SET_NULL, null=True, blank=True)

    implementing_partner = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)

    site_monitoring = models.BooleanField(default=False)
    site_name = models.CharField(max_length=255, blank=True, null=True)
    site_lat = models.CharField(max_length=255, blank=True, null=True)
    site_long = models.CharField(max_length=255, blank=True, null=True)
    old_id = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return f"{self.project}, {self.province}, {self.district}"

    class Meta:
        verbose_name = 'Target Location'
        verbose_name_plural = "Target Locations"

class BudgetProgress(models.Model):
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    donor = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)
    activity_domain = models.ForeignKey(ActivityDomain, on_delete=models.SET_NULL, null=True, blank=True)
    grant = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)
    amount_recieved = models.IntegerField(default=0, blank=True, null=True)
    budget_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    received_date = models.DateField(blank=True, null=True)
    country = models.ForeignKey(Location, blank=True, null=True, on_delete=models.SET_NULL, )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.donor}, {self.activity_domain}"

    class Meta:
        verbose_name = 'Budget Progress'
        verbose_name_plural = "Budget Progress"

class BudgetProgress(models.Model):
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    donor = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)
    activity_domain = models.ForeignKey(ActivityDomain, on_delete=models.SET_NULL, null=True, blank=True)
    grant = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)
    amount_recieved = models.IntegerField(default=0, blank=True, null=True)
    budget_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    received_date = models.DateField(blank=True, null=True)
    country = models.ForeignKey(Location, blank=True, null=True, on_delete=models.SET_NULL, )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.donor}, {self.activity_domain}"

    class Meta:
        verbose_name = 'Budget Progress'
        verbose_name_plural = "Budget Progress"