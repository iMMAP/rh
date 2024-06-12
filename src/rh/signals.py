from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import Cluster
from users.utils import assign_default_permissions_to_group


@receiver(post_save, sender=Cluster)
def post_create_cluster(sender, instance, created, **kwargs):
    if created:
        group, created = Group.objects.get_or_create(name=f"{instance.code.upper()}_CLUSTER_LEADS")
        if created:
            # Assign default permissions to the group
            assign_default_permissions_to_group(source_group_name="CLUSTER_LEAD", target_group=group)
