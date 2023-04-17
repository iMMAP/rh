from django.contrib import admin

from .models import *

admin.site.register(Currency)
admin.site.register(LocationType)
admin.site.register(FacilitySiteType)
admin.site.register(ImplementationModalityType)
admin.site.register(TransferMechanismType)
admin.site.register(PackageType)
admin.site.register(TransferCategory)
admin.site.register(GrantType)
admin.site.register(UnitType)
admin.site.register(ReportType)


class ClusterAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'title')
    search_fields = ('code', 'name')
    list_filter = ('code',)
admin.site.register(Cluster, ClusterAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'code', 'level', 'original_name', 'type')
    list_filter = ('level', 'type')
    search_fields = ('name', 'parent__name', 'level', 'type')
admin.site.register(Location, LocationAdmin)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'type', 'country')
    search_fields = ('name', 'country__name', 'type')
    list_filter = ('type', 'country')
admin.site.register(Organization, OrganizationAdmin)


class DonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'cluster')
    search_fields = ('code', 'name', 'cluster__title')
    list_filter = ('cluster', 'country')
admin.site.register(Donor, DonorAdmin)


class BeneficiaryTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'country')
    search_fields = ('code', 'name', 'country__name')
    list_filter = ('country',)
admin.site.register(BeneficiaryType, BeneficiaryTypeAdmin)


class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code',)
    search_fields = ('activity_types__name', 'name', 'code')
    # list_filter = ('activity_type',)
admin.site.register(Indicator, IndicatorAdmin)


class ActivityDomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'active')
    search_fields = ('name', 'clusters__title', 'code', 'countries__name')
    list_filter = ('clusters', 'countries')
admin.site.register(ActivityDomain, ActivityDomainAdmin)


class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'activity_domain', 'active')
    search_fields = ('name', 'activity_domain__name', 'clusters__title', 'code', 'countries__name')
    list_filter = ('activity_domain', 'clusters', 'countries')
admin.site.register(ActivityType, ActivityTypeAdmin)


class ActivityDetailAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity_type', 'code',)
    search_fields = ('activity_type__name', 'name', 'code')
    list_filter = ('activity_type',)
admin.site.register(ActivityDetail, ActivityDetailAdmin)


#############################################
####### Project Planning Model Admins #######
#############################################

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
    list_display = ('title', 'site_name', 'project', 'country', 'province', 'district', 'state', 'active')
    search_fields = ('title', 'project__title', 'state', 'active')
    list_filter = ('state', 'active', 'project__code')


admin.site.register(TargetLocation, TargetLocationAdmin)


##############################################
######### Reporting Model Admins ##########
##############################################

class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'project', 'activity_plan', 'location', 'boys', 'girls', 'men', 'women', 'elderly_men', 'elderly_women',
        'households')
    search_fields = (
        'project__title', 'location__name', 'boys', 'girls', 'men', 'women', 'elderly_men', 'elderly_women',
        'households')
    list_filter = ('project', 'activity_plan', 'location')
admin.site.register(Report, ReportAdmin)
