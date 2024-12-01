from django import template
from django.contrib.auth.models import User

from rh.models import Cluster

register = template.Library()


@register.simple_tag
def user_lead_clusters(user: User) -> Cluster:
    if not isinstance(user, User) or not user.is_authenticated:
        return Cluster.objects.none()

    user_groups = user.groups.filter(name__endswith="_CLUSTER_LEADS")

    cluster_ids = [group.name.split("_")[0].lower() for group in user_groups]

    return Cluster.objects.filter(code__in=cluster_ids)
