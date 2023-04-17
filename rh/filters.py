import django_filters
from django import forms
from .models import *


class ProjectsFilter(django_filters.FilterSet):
    clusters = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'js_multiselect'}),
    )

    class Meta:
        model = Project
        fields = '__all__'
