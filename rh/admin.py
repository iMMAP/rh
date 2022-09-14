from django.utils.translation import gettext_lazy as _
# from django.utils.safestring import mark_safe    

# from django.urls import reverse

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# from django.apps import apps 


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
        if app['app_label'] == 'auth':
            ordering = {
                'Users': 1,
                'Groups': 2
            }
            app['models'].sort(key=lambda x: ordering[x['name']])
        if app['app_label'] == 'rh':
            ordering = {
                "Countries": 3,
                "Clusters": 4,
                "Locations": 5,
                "Organizations": 6,
                "Activities": 7,
                "Projects": 8,
                "Activity Plans": 9,
                "Reports": 10,
            }
    return app_list

# Override the get_app_list of AdminSite
admin.AdminSite.get_app_list = get_app_list


##############################################
########## Custom User Model Admin ###########
##############################################
class CustomUserAdmin(UserAdmin):
    """
    Customize Django User model to add some custom fields 
    and remove first_name and last_name from the views, 
    search and filters
    """
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"), {
                "fields": (
                    "name", 
                    "email", 
                    "organization", 
                    "cluster", 
                    "position",
                    "phone",
                    "visits",
                ),
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
    list_display = ("username", "name", "email", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", 'name', "email")
admin.site.register(User, CustomUserAdmin)
# Move the User model to auth section
# apps.get_model('rh.User')._meta.app_label = 'auth'


##############################################
############ Country Model Admin #############
##############################################
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
admin.site.register(Country, CountryAdmin)


##############################################
############ Currency Model Admin #############
##############################################
# class CurrencyAdmin(admin.ModelAdmin):
#     list_display = ('name', 'code', 'symbol')
#     search_fields = ('name', 'code', 'symbol')
# admin.site.register(Currency, CurrencyAdmin)


##############################################
############ Cluster Model Admin #############
##############################################
admin.site.register(Cluster)


##############################################
########### Location Model Admin #############
##############################################
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'code', 'level', 'original_name', 'type')
    list_filter = ('parent', 'level', 'type')
    search_fields = ('name', 'parent', 'level', 'type')
admin.site.register(Location, LocationAdmin)


##############################################
######### Organization Model Admin ###########
##############################################
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'type', 'show_countries')
    search_fields = ('name', 'countires__name', 'type')
    list_filter = ('code', 'type', 'countires')

    def show_countries(self, obj):
        """
        Show countries as Manytomany fields can't be 
        placed directly in list view or search
        """
        return ",\n".join([a.name for a in obj.countires.all()])
    show_countries.short_description = 'Countries'

admin.site.register(Organization, OrganizationAdmin)


##############################################
############ Activity Model Admin ############
##############################################
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'show_clusters', 'show_countries', 'active')
    search_fields = ('title', 'countires__name', 'clusters__title', 'active')
    list_filter = ('active', 'countries', 'clusters')

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
    list_display = ('title', 'user', 'show_activities', 'show_locations', 'budget', 'budget_currency')
    search_fields = ('title', 'activities__title', 'locations__name')
    list_filter = ('user', 'activities', 'locations')

    # To create a clickable link between to models
    # def user_link(self, obj):
    #     url = f"admin:{obj.user._meta.app_label}_{obj.user._meta.model_name}_change"
    #     reverse = reverse(url, args=(obj.user.pk,))
    #     link_tag = f'<a href="{reverse}">{obj.user.username}</a>'
    #     return mark_safe(link_tag)
    # user_link.short_description = 'user'

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
