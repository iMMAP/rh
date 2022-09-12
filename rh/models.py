from django.db import models
from django.contrib.auth.models import AbstractUser


class Country(models.Model): 
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200)

class Organization(models.Model):
    countires = models.ManyToManyField(Country)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Cluster(models.Model):
    title = models.CharField(max_length=200)

class User(AbstractUser):
    first_name = None
    last_name = None

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    visits = models.IntegerField(null=True)
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE, null=True)
    position = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    pass


class Activity(models.Model):
    clusters = models.ManyToManyField(Cluster)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    countries = models.ManyToManyField(Country)
    fields = models.JSONField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Location(models.Model):
    parent = models.ForeignKey("self", default=0, on_delete=models.CASCADE)
    level = models.IntegerField(default=0)
    code = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    original_name = models.CharField(max_length=200, null=True)
    type = models.CharField(max_length=200, default='country')
    lat = models.FloatField(null=True)
    long = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activities = models.ManyToManyField(Activity)
    locations = models.ManyToManyField(Location)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField('start date')
    end_date = models.DateTimeField('end date')
    budget = models.IntegerField()
    budget_currency = models.IntegerChoices('Currency', 'EUR USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ActivityPlan(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True)
    activity_fields = models.JSONField()
    boys = models.IntegerField()
    girls = models.IntegerField()
    men = models.IntegerField()
    women = models.IntegerField()
    elderly_men = models.IntegerField()
    elderly_women = models.IntegerField()
    households = models.IntegerField()

class Report(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    activity_plan = models.ForeignKey(ActivityPlan, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    boys = models.IntegerField()
    girls = models.IntegerField()
    men = models.IntegerField()
    women = models.IntegerField()
    elderly_men = models.IntegerField()
    elderly_women = models.IntegerField()
    households = models.IntegerField()
    notes =  models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

