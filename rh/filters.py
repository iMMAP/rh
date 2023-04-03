import django_filters
from django import forms

from .models import *

class ProjectsFilter(django_filters.FilterSet):
    # locations = django_filters.MultipleChoiceFilter(widget=forms.SelectMultiple(attrs={'class': 'js-example-basic-multiple'}))

    class Meta:
        model = Project
        fields = '__all__'
        # form = {
        #     'locations': django_filters.FilterSet.form.SelectMultiple(attrs={'class': 'js-example-basic-multiple'}),
        #     'clusters': django_filters.FilterSet.form.SelectMultiple(attrs={'class': 'js-example-basic-multiple'}),
        #     'donors': django_filters.FilterSet.form.SelectMultiple(attrs={'class': 'js-example-basic-multiple'}),
        #     'activities': django_filters.FilterSet.form.SelectMultiple(attrs={'class': 'js-example-basic-multiple'}),
        # }    

    # def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
    #         super(ProjectsFilter, self).__init__(data=data, queryset=queryset, request=request, prefix=prefix)
    #         self.filters['locations'].field.widget.attrs.update({'class': 'js-example-basic-multiple'})