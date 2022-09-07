from django.contrib import admin
from .models import Project, User, Organization


admin.site.register(Project)
admin.site.register(User)
admin.site.register(Organization)