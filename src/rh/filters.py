import django_filters
from django import forms
from django.contrib.auth.models import User

from .models import (
    ActivityDomain,
    Cluster,
    Donor,
    Organization,
    Project,
    ActivityPlan,
    ActivityType,
    Indicator,
    TargetLocation,
    Location,
)
from django.db import models


def clusters(request):
    if request is None:
        return Cluster.objects.none()

    return request.user.profile.clusters.all()


# def organization(request):
#     if request is None:
#         return Organization.objects.none()

#     return Organization.objects.filter(clusters__in=request.user.profile.clusters.all())


class ProjectsFilter(django_filters.FilterSet):
    organization = django_filters.ModelMultipleChoiceFilter(
        queryset=Organization.objects.all(), widget=forms.SelectMultiple(attrs={"class": "input-select"})
    )
    clusters = django_filters.ModelMultipleChoiceFilter(
        queryset=clusters, widget=forms.SelectMultiple(attrs={"class": "input-select"})
    )
    activity_domains = django_filters.ModelMultipleChoiceFilter(
        queryset=ActivityDomain.objects.all(), widget=forms.SelectMultiple(attrs={"class": "input-select"})
    )
    programme_partners = django_filters.ModelMultipleChoiceFilter(
        queryset=Organization.objects.all(), widget=forms.SelectMultiple(attrs={"class": "input-select"})
    )
    implementing_partners = django_filters.ModelMultipleChoiceFilter(
        queryset=Organization.objects.all(), widget=forms.SelectMultiple(attrs={"class": "input-select"})
    )
    donors = django_filters.ModelMultipleChoiceFilter(
        queryset=Donor.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "input-select"}),
    )
    user = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "input-select"}),
    )

    class Meta:
        model = Project
        fields = {
            "title": ["contains"],
            "code": ["exact"],
            "start_date": ["exact"],
            "end_date": ["exact"],
            "is_hrp_project": ["exact"],
            "state": ["exact"],
        }
        filter_overrides = {
            models.DateTimeField: {
                "filter_class": django_filters.DateFilter,
                "extra": lambda f: {
                    "widget": forms.DateInput(
                        attrs={
                            "type": "date",
                        }
                    ),
                },
            },
        }


class ActivityPlansFilter(django_filters.FilterSet):
    activity_domain = django_filters.ModelMultipleChoiceFilter(
        queryset=ActivityDomain.objects.none(), widget=forms.SelectMultiple(attrs={"class": "custom-select"})
    )
    activity_type = django_filters.ModelMultipleChoiceFilter(
        queryset=ActivityType.objects.none(), widget=forms.SelectMultiple(attrs={"class": "custom-select"})
    )
    indicator = django_filters.ModelMultipleChoiceFilter(
        queryset=Indicator.objects.none(), widget=forms.SelectMultiple(attrs={"class": "custom-select"})
    )

    class Meta:
        model = ActivityPlan
        fields = ["activity_domain", "activity_type", "indicator"]

    def __init__(self, data=None, *args, **kwargs):
        project = kwargs.pop("project", None)
        super().__init__(data, *args, **kwargs)

        activity_domains = project.activity_domains.all()
        activity_types = ActivityType.objects.filter(activity_domain__in=activity_domains)

        self.form.fields["activity_domain"].queryset = activity_domains
        self.form.fields["activity_type"].queryset = activity_types
        self.form.fields["indicator"].queryset = Indicator.objects.filter(activity_types__in=activity_types).distinct()


class TargetLocationFilter(django_filters.FilterSet):
    activity_plan = django_filters.ModelMultipleChoiceFilter(
        queryset=ActivityPlan.objects.none(), widget=forms.SelectMultiple(attrs={"class": "custom-select"})
    )
    province = django_filters.ModelMultipleChoiceFilter(
        queryset=Location.objects.filter(level=1), widget=forms.SelectMultiple(attrs={"class": "custom-select"})
    )

    class Meta:
        model = TargetLocation
        fields = ["activity_plan", "province", "state"]

    def __init__(self, data=None, *args, **kwargs):
        project = kwargs.pop("project", None)
        super().__init__(data, *args, **kwargs)
        self.form.fields["activity_plan"].queryset = project.activityplan_set.all()
