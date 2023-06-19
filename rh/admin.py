from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.urls import reverse
from nested_inline.admin import NestedStackedInline, NestedModelAdmin

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
    list_display = ('name', 'code', 'title','countries_count','donors_count')
    search_fields = ('code', 'name')
    list_filter = ('code',)

    # get the count of a many to many relationship with Donor model
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            donors_count=Count('donor'),
            countries_count=Count('countries')
        )
        return queryset

    def donors_count(self, obj):
        return obj.donors_count

    def countries_count(self, obj):
        return obj.countries_count
    
admin.site.register(Cluster, ClusterAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'code', 'level', 'original_name', 'type')
    list_filter = ('level', 'type')
    search_fields = ('name', 'parent__name', 'level', 'type')
admin.site.register(Location, LocationAdmin)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'type', 'countries_count','clusters_count')
    search_fields = ('name', 'type')
    list_filter = ('type', )

    def countries_count(self, obj):
        return obj.countries.count()
    
    def clusters_count(self, obj):
        return obj.clusters.count()
admin.site.register(Organization, OrganizationAdmin)


class DonorAdmin(admin.ModelAdmin):
    list_display = ('name','countries_count','clusters_count')
    search_fields = ('code', 'name',)
    # list_filter = ('cluster', 'country')
    
    def countries_count(self, obj):
        return obj.countries.count()
    
    def clusters_count(self, obj):
        return obj.clusters.count()
   
admin.site.register(Donor, DonorAdmin)


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
    list_display = ('name','activity_types_count','activity_details_count')
    search_fields = ('activity_types__name','activity_details__name', 'name')
    # list_filter = ('activity_type',)
    inlines = [
        DisaggregationInline,
    ]
    def activity_types_count(self, obj):
        return obj.activity_types.count()

    def activity_details_count(self, obj):
        return obj.activity_details.count()
admin.site.register(Indicator, IndicatorAdmin)


class ActivityDomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'active','activity_types_count','activity_types_link')
    search_fields = ('name', 'clusters__title', 'code', 'countries__name')
    list_filter = ('clusters', 'countries')

    def activity_types_count(self, obj):
        return obj.activitytype_set.count()
    
    def activity_types_link(self, obj):
        url = reverse('admin:rh_activitytype_changelist')
        return format_html('<a href="{}?activity_domain__id__exact={}">View Activity Types</a>',url,obj.id)

admin.site.register(ActivityDomain, ActivityDomainAdmin)


class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity_type_link', 'active','activity_details_count','activity_details_link')
    search_fields = ('name', 'activity_domain__name', 'clusters__title', 'code', 'countries__name')
    list_filter = ('activity_domain', 'clusters', 'countries')

    def activity_details_count(self, obj):
        return obj.activitydetail_set.count()
    
    def activity_type_link(self, obj):
        url = reverse('admin:rh_activitydomain_change', args=[obj.activity_domain.id])
        return format_html('<a href="{}">{}</a>', url, obj.activity_domain)
    
    def activity_details_link(self, obj):
        url = reverse('admin:rh_activitydetail_changelist')
        return format_html('<a href="{}?activity_type__id__exact={}">View Activity Details</a>',url,obj.id)
    
admin.site.register(ActivityType, ActivityTypeAdmin)


class ActivityDetailAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity_type','activity_type_link')
    search_fields = ('activity_type__name', 'name', 'code')
    list_filter = ('activity_type',)

    def activity_type_link(self, obj):
        url = reverse('admin:rh_activitytype_change', args=[obj.activity_type.id])
        return format_html('<a href="{}">{}</a>', url, 'Click')
    
admin.site.register(ActivityDetail, ActivityDetailAdmin)



#############################################
####### Project Planning Model Admins #######
#############################################

class ActivityPlanInline(admin.TabularInline):
    model = ActivityPlan
    show_change_link = True
    extra = 0

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'user', 'show_clusters', 'budget', 'budget_currency', 'state')
    search_fields = (
        'title', 'code', 'clusters__title', 'implementing_partners__code',
        'programme_partners__code',
        'state')
    list_filter = ('state', 'clusters')

    inlines = [
        ActivityPlanInline,
    ]

    def show_clusters(self, obj):
        return ",\n".join([a.title for a in obj.clusters.all()])
    show_clusters.short_description = 'Clusters'
admin.site.register(Project, ProjectAdmin)


class ActivityPlanLocationDisaggregationInline(NestedStackedInline):
    model = ActivityPlanLocationDisaggregation
    show_change_link = True
    extra = 0

class ActivityPlanLocationInline(NestedStackedInline):
    model = ActivityPlanLocation
    show_change_link = True
    extra = 0
    inlines = [ActivityPlanLocationDisaggregationInline]

   

class ActivityPlanAdmin(NestedModelAdmin):
    list_display = ( 'project', 'total_reach', 'beneficiary',)
    search_fields = ('title', 'active', 'project__title', 'households',)
    list_filter = ('project__code',)
    
    inlines = [
        ActivityPlanLocationInline,
    ]

admin.site.register(ActivityPlan, ActivityPlanAdmin)


##############################################
######### Project Financial Report ###########
##############################################

class BudgetProgressAdmin(admin.ModelAdmin):
    list_display = (
        'project', 'donor', 'title', 'activity_domain', 'grant', 'amount_recieved', 'budget_currency', 'received_date', 'country')
    search_fields = (
        'project', 'donor', 'activity_domain', 'country')
    list_filter = ('project', 'donor', 'country')
admin.site.register(BudgetProgress, BudgetProgressAdmin)

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
