from django.db import models
from django.contrib.auth.models import AbstractUser
from rh.models import Organization, Cluster, Location
from django.utils import timezone

# Create your models here.

class Account(AbstractUser):
    """Inherit AbstractUser model and include our custom fields"""
    first_name = None
    last_name = None
    
    location = models.ForeignKey(Location, blank=True, null=True, on_delete=models.SET_NULL,)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    visits = models.IntegerField(blank=True, null=True)
    cluster = models.ForeignKey(Cluster, on_delete=models.SET_NULL, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    position = models.CharField(max_length=200, blank=True, null=True)
    skype = models.CharField(max_length=200, blank=True, null=True)
    old_id = models.CharField(max_length=200, blank=True, null=True)

    pass


class LoginHistory(models.Model):
    """Login History"""
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, blank=True, null=True)
    last_logged_in = models.DateTimeField(blank=True, null=True, default=timezone.now)

    def __str__(self):
        return self.user.name
    