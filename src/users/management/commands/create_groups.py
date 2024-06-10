from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from users.utils import assign_default_permissions_to_group
from rh.models import Cluster, Organization


class Command(BaseCommand):
    help = "Create groups for existing organizations and clusters."

    def _cluster_groups(self):
        clusters = Cluster.objects.all()

        for cluster in clusters:
            cluster_group_name = f"{cluster.code.upper()}_CLUSTER_LEADS"
            group, _ = Group.objects.get_or_create(name=cluster_group_name)

            assign_default_permissions_to_group(source_group_name="CLUSTER_LEAD", target_group=group)

    def _org_groups(self):
        orgs = Organization.objects.all()

        for org in orgs:
            org_group_name = f"{org.code.upper()}_ORG_LEADS"
            group, _ = Group.objects.get_or_create(name=org_group_name)

            assign_default_permissions_to_group(source_group_name="ORG_LEAD", target_group=group)

    def handle(self, *args, **options):
        self._cluster_groups()
        self._org_groups()
