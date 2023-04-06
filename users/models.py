from django.contrib.auth.models import User
from django.db import models

from rh.models import Organization, Cluster, Location


class Profile(models.Model):
    """Inherit AbstractUser model and include our custom fields"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    country = models.ForeignKey(Location, blank=True, null=True, on_delete=models.SET_NULL, )
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    visits = models.IntegerField(blank=True, null=True)
    clusters = models.ManyToManyField(Cluster)
    phone = models.CharField(max_length=200, blank=True, null=True)
    whatsapp = models.CharField(max_length=200, blank=True, null=True)
    position = models.CharField(max_length=200, blank=True, null=True)
    skype = models.CharField(max_length=200, blank=True, null=True)
    old_id = models.CharField(max_length=200, blank=True, null=True)
    is_cluster_contact = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}'s Profile"
