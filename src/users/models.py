from django.contrib.auth.models import User
from django.db import models
from rh.models import Cluster, Location, Organization


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    country = models.ForeignKey(
        Location,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"level": 0},
    )
    clusters = models.ManyToManyField(Cluster)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, blank=True, null=True)

    position = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    whatsapp = models.CharField(max_length=200, blank=True, null=True)
    skype = models.CharField(max_length=200, blank=True, null=True)
    old_id = models.CharField(max_length=200, blank=True, null=True)
    is_cluster_contact = models.BooleanField(default=False)

    email_verified_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @property
    def name(self):
        "Returns the person's full name."
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return f"{self.name}'s Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        permissions = [
            ("view_org_users", "View users of your organization"),
            ("make_admin", "Make a user organization admin"),
        ]
