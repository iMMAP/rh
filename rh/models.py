from django.contrib.auth.models import User
from django.db import models
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField
# from projects.models import Project

NAME_MAX_LENGTH = 200
DESCRIPTION_MAX_LENGTH = 600



class Location(models.Model):
    """Locations Model"""

    LOCATION_TYPES = [
        ('All', 'ALL'),
        ('Country', 'Country'),
        ('Province', 'Province'),
        ('District', 'District'),
        ('Zone', 'Zone'),
    ]
    parent = models.ForeignKey("self", default=0, on_delete=models.CASCADE, related_name='children', blank=True, null=True)
    code = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    level = models.IntegerField(default=0)
    original_name = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(
        max_length=15,
        choices=LOCATION_TYPES,
        default='Country', null=True, blank=True
    )
    lat = models.FloatField(blank=True, null=True)
    long = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.name

class Cluster(models.Model):
    """Clusters Model"""

    countries = models.ManyToManyField(Location, blank=True, null=True)

    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    title = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    ocha_code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return f"[{self.code}] - {self.title}"

class Organization(models.Model):
    """Organizations Model"""
    countries = models.ManyToManyField(Location, blank=True, null=True)
    clusters = models.ManyToManyField(Cluster, blank=True, null=True)

    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    type = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    old_id = models.CharField("Old ID", max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.code

class Currency(models.Model):
    """Currencies model"""
    name = models.CharField(max_length=15, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = "Currencies"

class Donor(models.Model):
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    countries = models.ManyToManyField(Location, blank=True, null=True)
    clusters = models.ManyToManyField(Cluster, blank=True, null=True)

    old_id = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Donor'
        verbose_name_plural = "Donors"

class LocationType(models.Model):
    """Locations Types model"""
    name = models.CharField(max_length=15, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Location Type'
        verbose_name_plural = "Location Types"

