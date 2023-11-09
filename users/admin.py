from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

from .models import Profile


class UserAdminCustom(UserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
        "profile_link",
    )

    def profile_link(self, obj):
        url = reverse("admin:users_profile_change", args=[obj.profile.id])
        return format_html('<a href="{}">{}</a>', url, obj.profile)


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
        self.fields["country"].queryset = self.fields["country"].queryset.filter(type="Country")


class ProfileAdmin(admin.ModelAdmin):
    """
    Customize Default ProfileAdmin
    """

    list_display = ("name", "country", "organization", "position", "user_link")
    list_filter = ("country",)
    form = ProfileForm

    def user_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user)


admin.site.register(Profile, ProfileAdmin)
