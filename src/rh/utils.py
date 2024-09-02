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


def update_project_plan_state(project: Project, state: str):
    """Updates the states of a project its activity plans and target locations
    state: should be from rh.models.STATES
    """
    activity_plans = project.activityplan_set.all()

    # Iterate through activity plans and archive them.
    for plan in activity_plans:
        target_locations = plan.targetlocation_set.all()

        # Iterate through target locations and archive them.
        for location in target_locations:
            disaggregation_locations = location.disaggregationlocation_set.all()

            # Iterate through disaggregation locations and archive.
            for disaggregation_location in disaggregation_locations:
                disaggregation_location.save()

            location.state = state
            location.save()

        plan.state = state
        plan.save()

    project.state = state
    project.save()
