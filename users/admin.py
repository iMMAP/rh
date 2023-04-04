from django.contrib import admin

from .models import *

admin.site.register(Profile)

# def get_app_list(self, request):
#     """

#     ***IMPORTANT***
#     Add future new models here in this ordering method and then register 
#     in admin.
#     ***IMPORTANT***

#     *Overrides orignal method of sorting models in admin view.
#     Return a sorted list of all the installed apps that have been
#     registered in this site.
#     """
#     # Retrieve the original list
#     app_dict = self._build_app_dict(request)
#     app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

#     # Sort the models customably within each app.
#     for app in app_list:
#         if app['app_label'] == 'auth':
#             ordering = {
#                 'Users': 1,
#                 'Groups': 2
#             }
#     return app_list

# # Override the get_app_list of AdminSite
# admin.AdminSite.get_app_list = get_app_list


# ##############################################
# ########## Custom User Model Admin ###########
# ##############################################
# class AccountAdmin(UserAdmin):
#     """
#     Customize Django User model to add some custom fields 
#     and remove first_name and last_name from the views, 
#     search and filters
#     """
#     fieldsets = (
#         (None, {"fields": ("username", "password")}),
#         (
#             _("Personal info"), {
#                 "fields": (
#                     "name", 
#                     "email", 
#                     "location", 
#                     "organization", 
#                     "cluster", 
#                     "position",
#                     "phone",
#                     "skype",
#                     "visits",
#                 ),
#             },
#         ),
#         (
#             _("Permissions"),
#             {
#                 "fields": (
#                     "is_active",
#                     "is_staff",
#                     "is_superuser",
#                     "groups",
#                     "user_permissions",
#                 ),
#             },
#         ),
#         (_("Important dates"), {"fields": ("last_login", "date_joined")}),
#     )
#     add_fieldsets = (
#         (
#             None,
#             {
#                 "classes": ("wide",),
#                 "fields": ("username", "password1", "password2"),
#             },
#         ),
#     )
#     list_display = ("username", "name", "email", "is_staff", "visits", "last_login")
#     list_filter = ("is_staff", "is_superuser", "is_active", "groups", "cluster", "location")
#     search_fields = ("username", 'name', "email", "cluster__title", "organization__name")
# admin.site.register(Account, AccountAdmin)
# Move the User model to auth section
# apps.get_model('rh.User')._meta.app_label = 'auth'
