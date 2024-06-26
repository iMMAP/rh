# Roles and permissions
The default groups and permissions for Django is used.

The default groups and their permissions are in the `src/users/fixtures/groups.json` fixture.

## Roles/Groups
- CLUSTER_LEAD (This group is used as permission template. Do not assign this to users)
- ORG_LEAD
- ORG_USER
- iMMAP_IMO

Each clusters have their own group with `CLUSTER_LEAD` group permission.
Ex:

- WASH_CLUSTER_LEADS
- ESNFI_CLUSTER_LEADS
- ...
- ...

### Create group for each cluster
```shell
python src/manage.py create_groups
```

### Update cluster leads groups permissions
If new permission are added to `CLUSTER_LEAD` groups, run the below command to update all cluster leads groups.
```shell
python src/manage.py update_groups_perms
```

## Permission
Default django model permission and custom ones (check models).

## Seed Default Groups
```shell
python src/manage.py loaddata groups.json
```


