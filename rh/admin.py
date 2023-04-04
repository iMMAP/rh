from django.utils.translation import gettext_lazy as _
# from django.utils.safestring import mark_safe    
from django.contrib.admin import SimpleListFilter

# from django.urls import reverse

from django.contrib import admin

from .models import *


def get_app_list(self, request):
    """

    ***IMPORTANT***
    Add future new models here in this ordering method and then register 
    in admin.
    ***IMPORTANT***

    *Overrides orignal method of sorting models in admin view.
    Return a sorted list of all the installed apps that have been
    registered in this site.
    """
    # Retrieve the original list
    app_dict = self._build_app_dict(request)
    app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

    # Sort the models customably within each app.
    for app in app_list:
        # if app['app_label'] == 'auth':
        #     ordering = {
        #         'Users': 1,
        #         'Groups': 2
        #     }
        if app['app_label'] == 'rh':
            ordering = {
                "Currencies": 3,
                "Countries": 4,
                "Clusters": 5,
                "Locations": 6,
                "Donors": 7,
                "Organizations": 8,
                "Activities": 9,
                "Projects": 10,
                "Activity Plans": 11,
                "Reports": 12,
                "StockType": 13,
                "StockUnit": 14,
                "WarehouseLocation": 15,
                "StockLocationReport": 16,
            }
            app['models'].sort(key=lambda x: ordering[x['name']])
    return app_list

# Override the get_app_list of AdminSite
admin.AdminSite.get_app_list = get_app_list


#############################################
########### Currency Model Admin #############
#############################################
admin.site.register(Currency)


#############################################
########### Location Types #############
#############################################
admin.site.register(LocationType)


##############################################
############ Country Model Admin #############
##############################################
# class CountryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'code')
#     search_fields = ('name', 'code')
# admin.site.register(Country, CountryAdmin)


##############################################
############ Cluster Model Admin #############
##############################################

class ClusterAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'old_code', 'old_title')
    search_fields = ('old_code', 'code', 'old_title', 'title',)
    list_filter = ('code', 'old_code',)
admin.site.register(Cluster, ClusterAdmin)


##############################################
########### Location Model Admin #############
##############################################
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'code', 'level', 'original_name', 'type')
    list_filter = ('level', 'type')
    search_fields = ('name', 'parent__name', 'level', 'type')
admin.site.register(Location, LocationAdmin)


##############################################
######### Organization Model Admin ###########
##############################################
# class CountryFilter(SimpleListFilter):
#     title = 'Country' # or use _('country') for translated title
#     parameter_name = 'Country'

#     def lookups(self, request, model_admin):
#         countries = set([c.locations.filter(type='Country') for c in model_admin.model.objects.all()])
#         return [(c.id, c.name) for c in countries] + [
#           ('AFRICA', 'AFRICA - ALL')]

#     def queryset(self, request, queryset):
#         if self.value() == 'AFRICA':
#             return queryset.filter(country__continent='Africa')
#         if self.value():
#             return queryset.filter(country__id__exact=self.value())

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'type', 'location')
    search_fields = ('name', 'location__name', 'type')
    list_filter = ('type', 'location')
    # list_filter = ('type', CountryFilter)

    def show_locations(self, obj):
        """
        Show locations as Manytomany fields can't be 
        placed directly in list view or search
        """
        return ",\n".join([a.name for a in obj.locations.all()])
    show_locations.short_description = 'Locations'

admin.site.register(Organization, OrganizationAdmin)


##############################################
######### Donor Model Admin ###########
##############################################
class DonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'cluster')
    search_fields = ('code', 'name', 'cluster__title')
    list_filter = ('cluster', 'location')
admin.site.register(Donor, DonorAdmin)


##############################################
######### BeneficiaryType Model Admin ###########
##############################################
class BeneficiaryTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'location')
    search_fields = ('code', 'name', 'location__name')
    list_filter = ('location',)
admin.site.register(BeneficiaryType, BeneficiaryTypeAdmin)


##############################################
############ Activity Model Admin ############
##############################################
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'subdomain_name', 'show_clusters', 'show_locations', 'active')
    search_fields = ('name', 'clusters__title', 'active', 'subdomain_code')
    list_filter = ('active', 'clusters', 'locations__name')

    def show_clusters(self, obj):
        return ",\n".join([a.title for a in obj.clusters.all()])
    show_clusters.short_description = 'Clusters'

    def show_locations(self, obj):
        return ",\n".join([a.name for a in obj.locations.all()])
    show_locations.short_description = 'Locations'
admin.site.register(Activity, ActivityAdmin)


##############################################
############ Project Model Admin #############
##############################################
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'user', 'show_clusters', 'budget', 'budget_currency', 'state', 'active')
    search_fields = ('title','code', 'clusters__title', 'activities__title', 'implementing_partners__code', 'programme_partners__code', 'state')
    list_filter = ('state', 'active', 'clusters')

    # To create a clickable link between to models
    # def user_link(self, obj):
    #     url = f"admin:{obj.user._meta.app_label}_{obj.user._meta.model_name}_change"
    #     reverse = reverse(url, args=(obj.user.pk,))
    #     link_tag = f'<a href="{reverse}">{obj.user.username}</a>'
    #     return mark_safe(link_tag)
    # user_link.short_description = 'user'

    def show_clusters(self, obj):
        return ",\n".join([a.title for a in obj.clusters.all()])
    show_clusters.short_description = 'Clusters'

    def show_activities(self, obj):
        return ",\n".join([a.name for a in obj.activities.all()])
    show_activities.short_description = 'Activities'
    
    # def show_locations(self, obj):
    #     return ",\n".join([a.name for a in obj.locations.all()])
    # show_locations.short_description = 'Locations'
admin.site.register(Project, ProjectAdmin)


##############################################
######### Activity Plan Model Admin ##########
##############################################
class ActivityPlanAdmin(admin.ModelAdmin):
    list_display = ('project', 'activity',  'households', 'beneficiary', 'beneficiary_category', 'state', 'active')
    search_fields = ('state', 'active', 'project__title', 'activity__name', 'households')
    list_filter = ('state', 'active', 'project__code')
admin.site.register(ActivityPlan, ActivityPlanAdmin)


##############################################
######### Target Locations Model Admin ##########
##############################################
class TargetLocationAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'project', 'country', 'province', 'district', 'state', 'active')
    search_fields = ('project__title', 'state', 'active')
    list_filter = ('state', 'active', 'project__code')
admin.site.register(TargetLocation, TargetLocationAdmin)


##############################################
######### Report Model Admin ##########
##############################################
class ReportAdmin(admin.ModelAdmin):
    list_display = ('project', 'activity_plan', 'location', 'boys', 'girls', 'men', 'women', 'elderly_men', 'elderly_women', 'households')
    search_fields = ('project__title', 'location__name', 'boys', 'girls', 'men', 'women', 'elderly_men', 'elderly_women', 'households')
    list_filter = ('project', 'activity_plan', 'location')
admin.site.register(Report, ReportAdmin)
