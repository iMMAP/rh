from django.contrib.auth.models import Group


def assign_default_permissions_to_group(source_group_name: str,target_group: Group):
    source_group = Group.objects.get(name=source_group_name)
    source_group_permissions = list(source_group.permissions.all())

    target_group.permissions.add(*source_group_permissions)