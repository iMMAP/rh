from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

from .models import Profile
import csv
from django.http import HttpResponse


@admin.action(description="Export selected")
def export_as_csv(self, request, queryset):
    meta = self.model._meta
    field_names = [field.name for field in meta.fields if field.name != "password"]

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename={}.csv".format(meta)
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response


@admin.action(description="Mark selected users as active")
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Mark selected users as inactive")
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "profiles"
    raw_id_fields = ["organization"]

    filter_horizontal = ("clusters",)


class UserAdminCustom(UserAdmin):
    list_display = ("email", "username", "name", "is_active", "user_groups", "last_login")
    list_select_related = ["profile"]

    inlines = (ProfileInline,)
    actions = [make_active, make_inactive, export_as_csv]
    date_hierarchy="last_login"

    def user_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])

    def name(self, obj):
        url = reverse("admin:users_profile_change", args=[obj.profile.id])
        return format_html("{} <em>(<a href='{}'>Profile</a></em>)", obj.get_full_name(), url)


admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)


# ##############################################
# ########## Profile Model Admin ###########
# ##############################################


class ProfileForm(forms.ModelForm):
    """
    Customize Default Profile form to add queryset
    """

    class Meta:
        model = Profile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)


class ProfileAdmin(admin.ModelAdmin):
    """
    Customize Default ProfileAdmin
    """

    list_display = ("user", "user_link", "organization", "position", "created_at", "Clusters")
    search_fields = ("user__first_name", "user__username")
    list_filter = ("country", "clusters")
    form = ProfileForm

    filter_horizontal = ("clusters",)

    def Clusters(self, obj):
        clusters = obj.clusters.all()
        return ", ".join([c.title for c in clusters])

    def user_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user)

    # Hides the profile from admin sidebar
    def has_module_permission(self, request):
        return False


admin.site.register(Profile, ProfileAdmin)
