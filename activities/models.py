from django.contrib.auth.models import User
from django.db import models
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField
from rh.models import Location, Cluster



NAME_MAX_LENGTH = 200
DESCRIPTION_MAX_LENGTH = 600

class BeneficiaryType(models.Model):
    """Beneficiary Types Model"""
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    country = models.ForeignKey(Location, blank=True, null=True, on_delete=models.SET_NULL, )
    clusters = models.ManyToManyField(Cluster)
    is_hrp_beneficiary = models.BooleanField(default=False)
    is_regular_beneficiary = models.BooleanField(default=False)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    description = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Beneficiary Type'
        verbose_name_plural = "Beneficiary Types"

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
        verbose_name = 'Objective'
        verbose_name_plural = "Objectives"


class FacilitySiteType(models.Model):
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.fields.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Facility Site Type'
        verbose_name_plural = "Facility Site Types"


class ImplementationModalityType(models.Model):
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.fields.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Implementation Modality Type'
        verbose_name_plural = "Implementation Modality Types"


class TransferMechanismType(models.Model):
    modality_id = models.ForeignKey(ImplementationModalityType, on_delete=models.SET_NULL, blank=True, null=True)
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.fields.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Transfer Mechanism Type'
        verbose_name_plural = "Transfer Mechanism Types"


class PackageType(models.Model):
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.fields.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Package Type'
        verbose_name_plural = "Package Types"


class TransferCategory(models.Model):
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.fields.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Transfer Category'
        verbose_name_plural = "Transfer Categories"


class GrantType(models.Model):
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.fields.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Grant Type'
        verbose_name_plural = "Grant Types"


class UnitType(models.Model):
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.fields.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Unit Type'
        verbose_name_plural = "Unit Types"


class ReportType(models.Model):
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.fields.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Report Type'
        verbose_name_plural = "Report Types"


class ActivityDomain(models.Model):
    active = models.BooleanField(default=True)
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    countries = models.ManyToManyField(Location)
    clusters = models.ManyToManyField(Cluster)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Activity Domain'
        verbose_name_plural = "Activity Domains"


class ActivityType(models.Model):
    activity_domain = models.ForeignKey(ActivityDomain, on_delete=models.SET_NULL, blank=True, null=True)
    active = models.BooleanField(default=True)
    code = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)
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
        verbose_name = 'Activity Type'
        verbose_name_plural = "Activity Types"


class ActivityDetail(models.Model):
    activity_type = models.ForeignKey(ActivityType, on_delete=models.SET_NULL, blank=True, null=True)
    code = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Activity Detail'
        verbose_name_plural = "Activity Details"


class Indicator(models.Model):
    """Indicators"""
    activity_types = models.ManyToManyField(ActivityType)
    code = models.CharField(max_length=600, blank=True, null=True)
    name = models.CharField(max_length=600, blank=True, null=True)
    numerator = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    denominator = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    description = models.CharField(max_length=1200, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Indicator'
        verbose_name_plural = "Indicators"


class Disaggregation(models.Model):
    clusters = models.ManyToManyField(Cluster)
    indicators = models.ManyToManyField(Indicator)

    name = models.CharField(max_length=NAME_MAX_LENGTH)
    type = models.CharField(max_length=NAME_MAX_LENGTH)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


