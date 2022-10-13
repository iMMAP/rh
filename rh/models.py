from django.db import models
from django.contrib.auth.models import AbstractUser


class Country(models.Model): 
    """Countries Model"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = "Countries"
    

class Cluster(models.Model):
    """Clusters Model"""
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Location(models.Model):
    """Locations Model"""

    LOCATION_TYPES = [
        ('Country', 'Country'),
        ('Province', 'Province'),
        ('District', 'District'),
    ]
    parent = models.ForeignKey("self", default=0, on_delete=models.CASCADE, blank=True, null=True)
    level = models.IntegerField(default=0)
    code = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
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


class Organization(models.Model):
    """Organizations Model"""
    countires = models.ManyToManyField(Country)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Inherit AbstractUser model and include our custom fields"""
    first_name = None
    last_name = None

    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    visits = models.IntegerField(blank=True, null=True)
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, blank=True, null=True)
    position = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    pass


class Activity(models.Model):
    """Activities model"""
    clusters = models.ManyToManyField(Cluster)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200, blank=True, null=True)
    countries = models.ManyToManyField(Country)
    fields = models.JSONField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = "Activities"

class Currency(models.Model):
    """Currencies model"""
    name = models.CharField(max_length=15, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = "Currencies"


class Project(models.Model):
    """Projects model"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    clusters = models.ManyToManyField(Cluster)
    activities = models.ManyToManyField(Activity)
    locations = models.ManyToManyField(Location)
    start_date = models.DateField('start date')
    end_date = models.DateField('end date')
    budget = models.IntegerField()
    budget_currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.title


class ActivityPlan(models.Model):
    """Activity Plans model"""
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True, blank=True)
    boys = models.IntegerField(blank=True, null=True)
    girls = models.IntegerField(blank=True, null=True)
    men = models.IntegerField(blank=True, null=True)
    women = models.IntegerField(blank=True, null=True)
    elderly_men = models.IntegerField(blank=True, null=True)
    elderly_women = models.IntegerField(blank=True, null=True)
    households = models.IntegerField(blank=True, null=True)
    activity_fields = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.project.title}, {self.activity.title}"

    class Meta:
        verbose_name = 'Activity Plan'
        verbose_name_plural = "Activity Plans"


class Report(models.Model):
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    activity_plan = models.ForeignKey(ActivityPlan, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    boys = models.IntegerField(blank=True, null=True)
    girls = models.IntegerField(blank=True, null=True)
    men = models.IntegerField(blank=True, null=True)
    women = models.IntegerField(blank=True, null=True)
    elderly_men = models.IntegerField(blank=True, null=True)
    elderly_women = models.IntegerField(blank=True, null=True)
    households = models.IntegerField(blank=True, null=True)
    notes =  models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class WarehouseLocation(models.Model):
    
    province = models.ForeignKey(Location, related_name='province', on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(Location, related_name='district', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Warehouse Location Plan'
        verbose_name_plural = "Warehouse Locations"


class StockType(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Stock Type'
        verbose_name_plural = "Stock Types"


class StockUnit(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Stock Unit'
        verbose_name_plural = "Stock Units"
    

class StockLocationReport(models.Model):
    PURPOSE_TYPES = [
        ('Prepositioned', 'Prepositioned'),
        ('Operational', 'Operational'),
    ]
    TARGET_GROUP_TYPES = [
        ('All Population', 'All Population'),
        ('Conflict Affected', 'Conflict Affected'),
        ('Natural Disaster', 'Natural Disaster'),
        ('Returnees', 'Returnees'),
    ]
    STATUS_TYPES = [
        ('Available', 'Available'),
        ('Reserved', 'Reserved'),
    ]
    warhouse_location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE)
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, null=True, blank=True)
    stock_purpose = models.CharField(
        max_length=255,
        choices=PURPOSE_TYPES,
        default='', null=True, blank=True
    )
    targeted_groups = models.CharField(
        max_length=255,
        choices=TARGET_GROUP_TYPES,
        default='', null=True, blank=True
    )
    stock_type = models.ForeignKey(StockType, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=255,
        choices=STATUS_TYPES,
        default='', null=True, blank=True
    )
    stock_unit = models.ForeignKey(StockUnit, verbose_name="Units", on_delete=models.SET_NULL, null=True, blank=True)
    qty_in_stock = models.IntegerField(default=0, verbose_name="Qty in Stock", null=True, blank=True)
    qty_in_pipeline = models.IntegerField(default=0, verbose_name="Qty in Pipeline", null=True, blank=True)
    beneficiary_coverage = models.IntegerField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    due_date = models.DateField(auto_now=True, blank=True, null=True)
    submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.warhouse_location.province.name + ", " + self.warhouse_location.district.name + ", " + self.warhouse_location.name
    
    class Meta:
        verbose_name = 'Stock Report'
        verbose_name_plural = "Stock Reports"