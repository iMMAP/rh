import django_filters
from django import forms

from rh.models import ActivityDomain, Cluster, Location, Organization
from .models import ProjectMonthlyReport

class ReportFilterForm(django_filters.FilterSet):
    clusters = django_filters.ModelMultipleChoiceFilter(
        # field_name='test',
        # to_field_name='project',
        queryset = Cluster.objects.all(),
        widget=forms.SelectMultiple()
    )
    organization = django_filters.ModelMultipleChoiceFilter(
        queryset = Organization.objects.all(),
        widget=forms.SelectMultiple(),
    )
    activity_domains = django_filters.ModelChoiceFilter(
        queryset = ActivityDomain.objects.all(),
        widget=forms.SelectMultiple(),
    )
    country = django_filters.ModelChoiceFilter(
        queryset = Location.objects.filter(type="Country"),
        widget=forms.Select(),
    )
    province = django_filters.ModelChoiceFilter(
        queryset = Location.objects.filter(type="Province"),
        widget=forms.Select()
    ),
    district = django_filters.ModelChoiceFilter(
        queryset = Location.objects.filter(type="District"),
        widget=forms.Select(),
    )
    class Meta:
        model = ProjectMonthlyReport
        fields = "__all__"