from django import forms
from django.forms.models import inlineformset_factory
from django.urls import reverse_lazy

from .models import *


class ProjectMonthlyReportForm(forms.ModelForm):
    class Meta:
        model = ProjectMonthlyReport
        fields = "__all__"

        widgets = {
            'report_date': forms.widgets.DateInput(
                attrs={'type': 'date', 'onfocus': "(this.type='date')", 'onblur': "(this.type='text')"}),
            'state': forms.widgets.HiddenInput(),
            'project': forms.widgets.HiddenInput(),
            'active': forms.widgets.HiddenInput(),
        }


class TargetLocationReportForm(forms.ModelForm):
    class Meta:
        model = TargetLocationReport
        fields = "__all__"
        # widgets = {
        #     'country': forms.widgets.HiddenInput(),
        #     'active': forms.widgets.HiddenInput(),
        #     'locations_group_by': forms.widgets.RadioSelect(),
        #     'district': forms.Select(
        #         attrs={'locations-queries-url': reverse_lazy('ajax-load-locations')}),
        #     'zone': forms.Select(
        #         attrs={'locations-queries-url': reverse_lazy('ajax-load-locations')}),
        # }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['save'] = forms.BooleanField(required=False, initial=False,
    #                                              widget=forms.HiddenInput(attrs={'name': self.prefix + '-save'}))
    #     self.fields['province'].queryset = self.fields['province'].queryset.filter(type='Province')
    #     self.fields['district'].queryset = self.fields['district'].queryset.filter(type='District')
    #     self.fields['zone'].queryset = self.fields['zone'].queryset.filter(type='Zone')
    #     self.fields['province'].widget.attrs.update({'data-form-prefix': f"{kwargs.get('prefix')}",
    #                                                  'onchange': f"updateLocationTitle('{kwargs.get('prefix')}', 'id_{kwargs.get('prefix')}-province');",
    #                                                  })
    #     self.fields['district'].widget.attrs.update(
    #         {'onchange': f"updateLocationTitle('{kwargs.get('prefix')}', 'id_{kwargs.get('prefix')}-district');",
    #          'locations-queries-url': reverse_lazy('ajax-load-locations')})
    #     self.fields['site_name'].widget.attrs.update(
    #         {'onchange': f"updateLocationTitle('{kwargs.get('prefix')}', 'id_{kwargs.get('prefix')}-site_name');"})


TargetLocationReportFormSet = inlineformset_factory(
        ActivityPlanReport,
        TargetLocationReport,
        form=TargetLocationReportForm,
        extra=1,  # Number of empty forms to display
        can_delete=True  # Allow deletion of existing forms
    )

DisaggregationReportFormSet = inlineformset_factory(
        TargetLocationReport,
        DisaggregationLocationReport,
        fields="__all__",
        extra=2,  # Number of empty forms to display
    )


class ActivityPlanReportForm(forms.ModelForm):
    class Meta:
        model = ActivityPlanReport
        fields = "__all__"

        widgets = {
            'activity_plan': forms.widgets.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['indicator'].widget.attrs.update({'class': 'report_indicator'})