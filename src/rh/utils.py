import json
from datetime import datetime

from django.contrib.auth.models import User
from users.utils import is_cluster_lead

from rh.models import Project, TargetLocation


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


def update_project_plan_state(project: Project, state: str):
    """Updates the states of a project its activity plans and target locations
    state: should be from rh.models.STATES
    """
    activity_plans = project.activityplan_set.all()
    activity_plans.update(state=state)

    target_locations = TargetLocation.objects.filter(activity_plan__in=activity_plans)
    target_locations.update(state=state)

    project.state = state
    project.save()
