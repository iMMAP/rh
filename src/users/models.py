from django.contrib.auth.models import User
from django.db import models

from rh.models import Cluster, Location, Organization


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    country = models.ForeignKey(Location, blank=False, null=True, on_delete=models.SET_NULL)
    clusters = models.ManyToManyField(Cluster)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=True, null=True)

    position = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    whatsapp = models.CharField(max_length=200, blank=True, null=True)
    skype = models.CharField(max_length=200, blank=True, null=True)
    old_id = models.CharField(max_length=200, blank=True, null=True)
    is_cluster_contact = models.BooleanField(default=False)

    @property
    def name(self):
        "Returns the person's full name."
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return f"{self.name}'s Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
