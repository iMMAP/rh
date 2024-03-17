import django_filters
from django import forms
from django_filters.widgets import RangeWidget

from rh.models import Cluster, Organization

from .models import ProjectMonthlyReport


class ReportFilterForm(django_filters.FilterSet):
    cluster = django_filters.ModelChoiceFilter(
        # field_name='test',
        # to_field_name='project',
        queryset=Cluster.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "custom-select",
            }
        ),
    )
    organization = django_filters.ModelChoiceFilter(
        queryset=Organization.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "custom-select",
            }
        ),
    )

    Date = django_filters.DateFromToRangeFilter(widget=RangeWidget(attrs={"type": "date"}))

    class Meta:
        model = ProjectMonthlyReport
        fields = "__all__"
