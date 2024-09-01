from datetime import datetime
import json
from django.contrib.auth.models import User
from rh.models import Project


def is_cluster_lead(user: User, clusters: list) -> bool:
    cluster_lead_groups = [f"{cluster.upper()}_CLUSTER_LEADS" for cluster in clusters]
    if not user.groups.filter(name__in=cluster_lead_groups).exists():
        return False

    return True


def has_permission(user: User, project: Project = None, clusters: list = [], permission: str = ""):
    if user.is_superuser:
        return True

    if permission:
        if not user.has_perm(permission):
            return False

    if project:
        if not (project.user == user or user.profile.organization == project.organization):
            project_clusters = project.clusters.values_list("code", flat=True)
            if not is_cluster_lead(user=user, clusters=project_clusters):
                return False

    if clusters:
        if not is_cluster_lead(user=user, clusters=clusters):
            return False

    return True


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
