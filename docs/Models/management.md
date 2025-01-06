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

#### Schedule the commands
```shell
crontab -e
```
Add the below line save, command runs daily at 2:00 AM
```shell
0 2 * * * cd /home/ubuntu/rh && poetry run python src/manage.py dbbackup --database=default --settings=core.settings.production
0 2 * * * cd /home/ubuntu/rh && poetry run python src/manage.py mediabackup --database=default --settings=core.settings.production
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

## Queue mail with django-mailer
```shell
crontab -e
```

Add the below to the cron
```shell
*       * * * * (/home/ubuntu/rh/.venv/bin/python /home/ubuntu/rh/src/manage.py send_mail --settings=core.settings.production >> ~/cron_mail.log 2>&1)
0,20,40 * * * * (/home/ubuntu/rh/.venv/bin/python /home/ubuntu/rh/src/manage.py retry_deferred --settings=core.settings.production >> ~/cron_mail_deferred.log 2>&1)
0 0 * * * (/home/ubuntu/rh/.venv/bin/python /home/ubuntu/rh/src/manage.py purge_mail_log 7 --settings=core.settings.production >> ~/cron_mail_purge.log 2>&1)
```
