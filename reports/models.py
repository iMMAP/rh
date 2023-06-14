from django.db import models
from django.contrib.auth.models import User
from django.db import models
from projects.models import Project,ActivityPlan,Location


# Create your models here.
class ActivityReport(models.Model):
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
    notes = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)