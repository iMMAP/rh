import django_filters
from django import forms

from rh.models import (
    ActivityDomain,
    ActivityType,
    Cluster,
    Disaggregation,
    Indicator,
    Location,
    Project,
)

from .models import ActivityPlanReport, ProjectMonthlyReport, TargetLocationReport


class MonthlyReportsFilter(django_filters.FilterSet):
    # Define the DateFromToRangeFilter with initial value of current month
    # current_month = datetime.date.today().replace(day=1)
    # from_date = django_filters.DateFromToRangeFilter(widget=RangeWidget(attrs={"type": "date"}))
    from_date = django_filters.DateFilter(
        widget=forms.DateInput(
            attrs={
                "type": "date",
            }
        )
    )
    to_date = django_filters.DateFilter(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = ProjectMonthlyReport
        fields = ["from_date", "to_date", "state"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ActivityPlanReportFilter(django_filters.FilterSet):
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
        field_name="activity_plan__indicator",
        queryset=Indicator.objects.none(),
        widget=forms.SelectMultiple(attrs={"class": "custom-select"}),
    )

    class Meta:
        model = ActivityPlanReport
        fields = ["activity_domain", "activity_type", "indicator", "response_types"]

    def __init__(self, data=None, *args, **kwargs):
        report = kwargs.pop("monthly_report", None)
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
    target_location__province = django_filters.ModelMultipleChoiceFilter(
        queryset=Location.objects.filter(level=1), widget=forms.SelectMultiple(attrs={"class": "custom-select"})
    )
    target_location__district = django_filters.ModelMultipleChoiceFilter(
        queryset=Location.objects.filter(level=2), widget=forms.SelectMultiple(attrs={"class": "custom-select"})
    )

    class Meta:
        model = TargetLocationReport
        fields = ["activity_plan_report", "target_location__province", "target_location__district"]

    def __init__(self, data=None, *args, **kwargs):
        report = kwargs.pop("report", None)
        super().__init__(data, *args, **kwargs)
        self.form.fields["activity_plan_report"].queryset = report.activityplanreport_set.all()


class Organization5WFilter(django_filters.FilterSet):
    cluster = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        field_name="activityplanreport__activity_plan__activity_domain__clusters",
        label="Cluster",
        widget=forms.SelectMultiple(attrs={"class": "custom-select"}),
    )
    project = django_filters.ModelMultipleChoiceFilter(
        field_name="project",
        queryset=Project.objects.none(),
        widget=forms.SelectMultiple(attrs={"class": "custom-select"}),
    )
    province = django_filters.ModelMultipleChoiceFilter(
        field_name="activityplanreport__targetlocationreport__target_location__province",
        queryset=Location.objects.filter(level=1),
        label="Province",
        widget=forms.SelectMultiple(attrs={"class": "custom-select"}),
    )
    district = django_filters.ModelMultipleChoiceFilter(
        field_name="activityplanreport__targetlocationreport__target_location__district",
        queryset=Location.objects.filter(level=2),
        label="District",
        widget=forms.SelectMultiple(attrs={"class": "custom-select"}),
    )
    disaggregations = django_filters.ModelMultipleChoiceFilter(
        field_name="activityplanreport__targetlocationreport__disaggregationlocationreport__disaggregation__name",
        queryset=Disaggregation.objects.all(),
        label="disaggregations",
        widget=forms.SelectMultiple(attrs={"class": "custom-select"}),
    )
    to_date = django_filters.DateFilter(widget=forms.DateInput(attrs={"type": "date"}))
    from_date = django_filters.DateFilter(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = ProjectMonthlyReport
        fields = ["from_date", "to_date", "cluster", "project", "province", "district", "disaggregations"]

    def __init__(self, data=None, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(data, *args, **kwargs)
        self.form.fields["project"].queryset = Project.objects.filter(organization=user.profile.organization)
