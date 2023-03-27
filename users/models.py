from django.db import models
from rh.models import Organization, Cluster, Location
from django.contrib.auth.models import User


class Profile(models.Model):
    """Inherit AbstractUser model and include our custom fields"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    location = models.ForeignKey(Location, blank=True, null=True, on_delete=models.SET_NULL,)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    visits = models.IntegerField(blank=True, null=True)
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    position = models.CharField(max_length=200, blank=True, null=True)
    skype = models.CharField(max_length=200, blank=True, null=True)
    old_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.name}'s Profile"

    