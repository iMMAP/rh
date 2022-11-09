from django.db import models


class Country(models.Model): 
    """Countries Model"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200, blank=True, null=True)
    code2 = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = "Countries"
    

class Cluster(models.Model):
    """Clusters Model"""
    code = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)

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


class Activity(models.Model):
    """Activities model"""
    active = models.BooleanField(default=True)
    ocha_code = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200)
    clusters = models.ManyToManyField(Cluster)
    indicator = models.TextField(blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    countries = models.ManyToManyField(Country)
    fields = models.JSONField(blank=True, null=True, default=dict)
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
    user = models.ForeignKey('accounts.Account', on_delete=models.SET_NULL, null=True, blank=True)
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
