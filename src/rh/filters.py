import django_filters
from django import forms
from django.contrib.auth.models import User

from .models import ActivityDomain, Cluster, Donor, Organization, Project
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
