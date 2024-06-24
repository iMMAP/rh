from django.contrib.auth.models import Group,User

def has_permission(user: User,user_obj:User, permission: str = "") -> bool:
    if user.is_superuser:
        return True
    
    if permission:
        if not user.has_perm(permission):
            return False

    if not (user.profile.organization == user_obj.profile.organization):
        return False

    return True

def assign_default_permissions_to_group(source_group_name: str, target_group: Group):
    try:
        source_group = Group.objects.get(name=source_group_name)
        source_group_permissions = list(source_group.permissions.all())

        target_group.permissions.add(*source_group_permissions)
    except Group.DoesNotExist:
        pass
    except Exception:
        pass
