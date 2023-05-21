import django_filters
from django import forms
from .models import *


class ProjectsFilter(django_filters.FilterSet):
    # FIXME: Fix the options issue
    clusters = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'js_multiselect'}),
    )
    implementing_partners = django_filters.ModelMultipleChoiceFilter(
        queryset=Organization.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'js_multiselect'}),
    )
    donors = django_filters.ModelMultipleChoiceFilter(
        queryset=Donor.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'js_multiselect'}),
    )
    programme_partners = django_filters.ModelMultipleChoiceFilter(
        queryset=Organization.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'js_multiselect'}),
    )
    activity_domains = django_filters.ModelMultipleChoiceFilter(
        queryset=ActivityDomain.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'js_multiselect'}),
    )

    class Meta:
        model = Project
        fields = '__all__'
