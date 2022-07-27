from django.db import models
from django.contrib.auth.models import AbstractUser


class Organization(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

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

# Create your models here.
class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField('start date')
    end_date = models.DateTimeField('end date')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Activity(models.Model):
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField('start date', null=True)
    end_date = models.DateTimeField('end date', null=True)
    
class Indicator(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)

class Report(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    notes =  models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Beneficiary(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    boys = models.IntegerField()
    girls = models.IntegerField()
    men = models.IntegerField()
    women = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class Location(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    boys = models.IntegerField()
    girls = models.IntegerField()
    men = models.IntegerField()
    women = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
