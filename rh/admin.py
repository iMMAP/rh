from django.utils.translation import gettext_lazy as _
# from django.utils.safestring import mark_safe    

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
                "Doners": 7,
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


##############################################
############ Country Model Admin #############
##############################################
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
admin.site.register(Country, CountryAdmin)


##############################################
############ Cluster Model Admin #############
##############################################
class ClusterAdmin(admin.ModelAdmin):
    list_display = ('code', 'title',)
    search_fields = ('code', 'title',)
admin.site.register(Cluster, ClusterAdmin)


##############################################
########### Location Model Admin #############
##############################################
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'code', 'level', 'original_name', 'type')
    list_filter = ('level', 'type')
    search_fields = ('name', 'parent', 'level', 'type')
admin.site.register(Location, LocationAdmin)


##############################################
######### Organization Model Admin ###########
##############################################
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'type', 'show_countries')
    search_fields = ('name', 'countires__name', 'type')
    list_filter = ('type', 'countires')

    def show_countries(self, obj):
        """
        Show countries as Manytomany fields can't be 
        placed directly in list view or search
        """
        return ",\n".join([a.name for a in obj.countires.all()])
    show_countries.short_description = 'Countries'

admin.site.register(Organization, OrganizationAdmin)


##############################################
######### Doner Model Admin ###########
##############################################
class DonerAdmin(admin.ModelAdmin):
    list_display = ('project_donor_name', 'project_donor_id', 'country', 'cluster')
    search_fields = ('project_donor_id', 'project_donor_name', 'cluster__title', 'country__name')
    list_filter = ('cluster', 'country')
admin.site.register(Doner, DonerAdmin)


##############################################
############ Activity Model Admin ############
##############################################
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'detail', 'description', 'show_clusters', 'show_countries', 'indicator', 'active')
    search_fields = ('title', 'clusters__title', 'active')
    list_filter = ('active', 'clusters', 'countries__name')

    def show_clusters(self, obj):
        return ",\n".join([a.title for a in obj.clusters.all()])
    show_clusters.short_description = 'Clusters'

    def show_countries(self, obj):
        return ",\n".join([a.name for a in obj.countries.all()])
    show_countries.short_description = 'Countries'
admin.site.register(Activity, ActivityAdmin)


##############################################
############ Project Model Admin #############
##############################################
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'user', 'show_clusters', 'show_activities', 'show_locations', 'budget', 'budget_currency')
    search_fields = ('title','code', 'clusters__title', 'activities__title', 'locations__name')
    list_filter = ('clusters',)

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
        return ",\n".join([a.title for a in obj.activities.all()])
    show_activities.short_description = 'Activities'
    
    def show_locations(self, obj):
        return ",\n".join([a.name for a in obj.locations.all()])
    show_locations.short_description = 'Locations'
admin.site.register(Project, ProjectAdmin)


##############################################
######### Activity Plan Model Admin ##########
##############################################
class ActivityPlanAdmin(admin.ModelAdmin):
    list_display = ('project', 'activity', 'boys', 'girls', 'men', 'women', 'elderly_men', 'elderly_women', 'households')
    search_fields = ('project__title', 'activity__title', 'boys', 'girls', 'men', 'women', 'elderly_men', 'elderly_women', 'households')
    list_filter = ('project', 'activity')
admin.site.register(ActivityPlan, ActivityPlanAdmin)


##############################################
######### Report Model Admin ##########
##############################################
class ReportAdmin(admin.ModelAdmin):
    list_display = ('project', 'activity_plan', 'location', 'boys', 'girls', 'men', 'women', 'elderly_men', 'elderly_women', 'households')
    search_fields = ('project__title', 'location__name', 'boys', 'girls', 'men', 'women', 'elderly_men', 'elderly_women', 'households')
    list_filter = ('project', 'activity_plan', 'location')
admin.site.register(Report, ReportAdmin)
