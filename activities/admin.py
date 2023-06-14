from django.contrib import admin
from django.db.models import Count

from .models import *

admin.site.register(FacilitySiteType)
admin.site.register(ImplementationModalityType)
admin.site.register(TransferMechanismType)
admin.site.register(PackageType)
admin.site.register(TransferCategory)
admin.site.register(GrantType)
admin.site.register(UnitType)
admin.site.register(ReportType)


class BeneficiaryTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'country')
    search_fields = ('code', 'name', 'country__name')
    list_filter = ('country',)
admin.site.register(BeneficiaryType, BeneficiaryTypeAdmin)

class DisaggregationAdmin(admin.ModelAdmin):
    list_display = ('name','indicators_count','clusters_count')
    search_fields = ('code', 'name',)
    # list_filter = ('cluster', 'country')
    
    def indicators_count(self, obj):
        return obj.indicators.count()
    
    def clusters_count(self, obj):
        return obj.clusters.count()
admin.site.register(Disaggregation, DisaggregationAdmin)


class DisaggregationInline(admin.TabularInline):
    model = Disaggregation.indicators.through
    extra = 1

class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code',)
    search_fields = ('activity_types__name', 'name', 'code')
    # list_filter = ('activity_type',)
    inlines = [
        DisaggregationInline,
    ]
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


