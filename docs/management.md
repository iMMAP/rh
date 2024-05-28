# Manange the platform


## Maintenance Mode
Update the below env variables to activate/deactivate the maintenace mode.

```shell
MAINTENANCE_MODE_ENABLED=False
# if True the superuser will not see the maintenance-mode page
MAINTENANCE_MODE_IGNORE_SUPERUSER=True
# if True the staff will not see the maintenance-mode page
MAINTENANCE_MODE_IGNORE_STAFF=True
# the absolute url where users will be redirected to during maintenance-mode
MAINTENANCE_MODE_REDIRECT_ROUTE=maintenance
MAINTENANCE_BYPASS_QUERY=
```


## Countinous Integration with EC2
Implemented with Github Actions.
Check `.github/workflows/CI.yml` for details.


## Periodic DB Backup to dropbox
Login to dropbox with `Sign In With Google` using RH gmail account.

### Backup
```shell
# Backup the database
poetry run python src/manage.py dbbackup

# Backup the media
poetry run python src/manage.py mediabackup
```

### Restore DB Backup

** Restore with django-dbbackup **
```shell
poetry run python src/manage.py dbrestore
```

** Restore manually **
```shell
pg_restore --clean --no-acl --no-owner -d <database> -U <user> <filename.dump>
```