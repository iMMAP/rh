import django_filters
from django import forms

from rh.models import Cluster, Organization
from .models import ProjectMonthlyReport


class ReportFilterForm(django_filters.FilterSet):
    clusters = django_filters.ModelMultipleChoiceFilter(
        # field_name='test',
        # to_field_name='project',
        queryset=Cluster.objects.all(),
        widget=forms.SelectMultiple(),
    )
    organization = django_filters.ModelMultipleChoiceFilter(
        queryset=Organization.objects.all(),
        widget=forms.SelectMultiple(),
    )

    class Meta:
        model = ProjectMonthlyReport
        fields = "__all__"
