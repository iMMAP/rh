from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "profiles"

    filter_horizontal = ("clusters",)


class UserAdminCustom(UserAdmin):
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_active",
        "profile_link",
        "last_login",
        "is_staff",
        "date_joined",
        "is_superuser",
    )

    inlines = (ProfileInline,)

    def profile_link(self, obj):
        url = reverse("admin:users_profile_change", args=[obj.profile.id])
        return format_html("<a href='{}'>{}'s Profile</a>", url, obj.username)


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
