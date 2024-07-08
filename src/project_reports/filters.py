import datetime
from django import forms

import django_filters
from django_filters.widgets import RangeWidget

from .models import ProjectMonthlyReport, ActivityPlanReport, TargetLocationReport
from rh.models import (
    Location,
    ActivityDomain,
    ActivityType,
    Indicator,
)


class ReportFilterForm(django_filters.FilterSet):
    """Monthly Report Filter Form"""

    # Define the DateFromToRangeFilter with initial value of current month
    current_month = datetime.date.today().replace(day=1)
    report_date = django_filters.DateFromToRangeFilter(widget=RangeWidget(attrs={"type": "date"}))

    class Meta:
        model = ProjectMonthlyReport
        fields = {
            "project__clusters": ["exact"],  # Exact match for clusters
            "project__implementing_partners": ["exact"],  # Exact match for implementing partners
            "report_date": ["gte", "lte"],  # Date range
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.form.fields["project__clusters"].widget.attrs.update({"class": "custom-select"})
        self.form.fields["project__implementing_partners"].widget.attrs.update({"class": "custom-select"})


class PlansReportFilter(django_filters.FilterSet):
    activity_domain = django_filters.ModelMultipleChoiceFilter(
        field_name="activity_plan__activity_domain",
        queryset=ActivityDomain.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "custom-select"}),
    )
    activity_type = django_filters.ModelMultipleChoiceFilter(
        field_name="activity_plan__activity_type",
        queryset=ActivityType.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "custom-select"}),
    )
    indicator = django_filters.ModelMultipleChoiceFilter(
        queryset=Indicator.objects.none(), widget=forms.SelectMultiple(attrs={"class": "custom-select"})
    )

    class Meta:
        model = ActivityPlanReport
        fields = ["activity_domain", "activity_type", "indicator"]

    def __init__(self, data=None, *args, **kwargs):
        report = kwargs.pop("report", None)
        super().__init__(data, *args, **kwargs)

        activity_domains = report.project.activity_domains.all()
        activity_types = ActivityType.objects.filter(activity_domain__in=activity_domains)

        self.form.fields["activity_domain"].queryset = activity_domains
        self.form.fields["activity_type"].queryset = activity_types
        self.form.fields["indicator"].queryset = Indicator.objects.filter(activity_types__in=activity_types).distinct()


class TargetLocationReportFilter(django_filters.FilterSet):
    activity_plan_report = django_filters.ModelMultipleChoiceFilter(
        queryset=ActivityPlanReport.objects.none(), widget=forms.SelectMultiple(attrs={"class": "custom-select"})
    )
    province = django_filters.ModelMultipleChoiceFilter(
        queryset=Location.objects.filter(level=1), widget=forms.SelectMultiple(attrs={"class": "custom-select"})
    )
    district = django_filters.ModelMultipleChoiceFilter(
        queryset=Location.objects.filter(level=2), widget=forms.SelectMultiple(attrs={"class": "custom-select"})
    )

    class Meta:
        model = TargetLocationReport
        fields = ["activity_plan_report", "province", "district"]

    def __init__(self, data=None, *args, **kwargs):
        report = kwargs.pop("report", None)
        super().__init__(data, *args, **kwargs)
        self.form.fields["activity_plan_report"].queryset = report.activityplanreport_set.all()
