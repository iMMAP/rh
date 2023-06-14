from django.contrib import admin
from django.db.models import Count

from .models import *
# Register your models here.
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'user', 'show_clusters', 'budget', 'budget_currency', 'state', 'active')
    search_fields = (
        'title', 'code', 'clusters__title', 'implementing_partners__code',
        'programme_partners__code',
        'state')
    list_filter = ('state', 'active', 'clusters')

    def show_clusters(self, obj):
        return ",\n".join([a.title for a in obj.clusters.all()])
    show_clusters.short_description = 'Clusters'
admin.site.register(Project, ProjectAdmin)


class ActivityPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'households', 'beneficiary', 'beneficiary_category', 'state', 'active')
    search_fields = ('title', 'state', 'active', 'project__title', 'households')
    list_filter = ('state', 'active', 'project__code')
admin.site.register(ActivityPlan, ActivityPlanAdmin)


class TargetLocationAdmin(admin.ModelAdmin):
    list_display = ('title', 'site_name', 'project', 'country', 'province', 'district', 'zone', 'state', 'active')
    search_fields = ('title', 'project__title', 'state', 'active')
    list_filter = ('state', 'active', 'project__code')


admin.site.register(TargetLocation, TargetLocationAdmin)


class BudgetProgressAdmin(admin.ModelAdmin):
    list_display = (
        'project', 'donor', 'title', 'activity_domain', 'grant', 'amount_recieved', 'budget_currency', 'received_date', 'country')
    search_fields = (
        'project', 'donor', 'activity_domain', 'country')
    list_filter = ('project', 'donor', 'country')
admin.site.register(BudgetProgress, BudgetProgressAdmin)