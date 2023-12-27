import django_filters
from django import forms

from .models import ActivityDomain, Cluster, Donor, Organization, Project


class ProjectsFilter(django_filters.FilterSet):
    # FIXME: Fix the options issue
    clusters = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        widget=forms.SelectMultiple(attrs={"class":"input-select"})
    )
    implementing_partners = django_filters.ModelMultipleChoiceFilter(
        queryset=Organization.objects.all(),
        widget=forms.SelectMultiple(attrs={"class":"input-select"})
    )
    donors = django_filters.ModelMultipleChoiceFilter(
        queryset=Donor.objects.all(),
        widget=forms.SelectMultiple(attrs={"class":"input-select"}),
    )
    programme_partners = django_filters.ModelMultipleChoiceFilter(
        queryset=Organization.objects.all(),
        widget=forms.SelectMultiple(attrs={"class":"input-select"})
    )
    activity_domains = django_filters.ModelMultipleChoiceFilter(
        queryset=ActivityDomain.objects.all(),
        widget=forms.SelectMultiple(attrs={"class":"input-select"})
    )

    class Meta:
        model = Project
        fields = "__all__"
