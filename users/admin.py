from django.contrib import admin

from .models import *
from django import forms


# ##############################################
# ########## Profile Model Admin ###########
# ##############################################

class ProfileForm(forms.ModelForm):
    """
    Customize Default Profile form to add queryset
    """
    class Meta:
        model = Profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['country'].queryset = self.fields['country'].queryset.filter(type='Country')


class ProfileAdmin(admin.ModelAdmin):
    """
    Customize Default ProfileAdmin
    """
    list_display = ('name', 'country', 'organization', 'position')
    list_filter = ('country',)
    form = ProfileForm


admin.site.register(Profile, ProfileAdmin)
