from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Profile


@receiver(pre_save, sender=Profile)
def pre_save_profile(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Profile.objects.get(pk=instance.pk)
        if old_instance.organization != instance.organization:
            org_lead_group = old_instance.user.groups.filter(name=f"{old_instance.organization.code.upper()}_ORG_LEADS")
            if org_lead_group.exists():
                # Remove user from ORG_LEAD group
                instance.user.groups.remove(org_lead_group[0].id)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        Profile.objects.create(user=instance)
