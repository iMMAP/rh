from django.db import models
from django.contrib.auth.models import AbstractUser
from rh.models import Organization, Cluster

# Create your models here.

class Account(AbstractUser):
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
