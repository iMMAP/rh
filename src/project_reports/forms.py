from django import forms
from django.forms.models import inlineformset_factory
from rh.models import Indicator
from django.urls import reverse_lazy

from .models import ActivityPlanReport, DisaggregationLocationReport, ProjectMonthlyReport, TargetLocationReport


class ProjectMonthlyReportForm(forms.ModelForm):
    class Meta:
        model = ProjectMonthlyReport
        fields = "__all__"

        widgets = {
            "report_date": forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "onfocus": "(this.type='date')",
                    "onblur": "(this.type='text')",
                }
            ),
            "report_due_date": forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "onfocus": "(this.type='date')",
                    "onblur": "(this.type='text')",
                    "readonly": "",
                }
            ),
        }


class TargetLocationReportForm(forms.ModelForm):
    class Meta:
        model = TargetLocationReport
        fields = "__all__"
        widgets = {
            "district": forms.Select(attrs={"target-locations-queries-url": reverse_lazy("ajax-load-target-locations")}),
            "zone": forms.Select(attrs={"target-locations-queries-url": reverse_lazy("ajax-load-target-locations")}),
        }


TargetLocationReportFormSet = inlineformset_factory(
    ActivityPlanReport,
    TargetLocationReport,
    form=TargetLocationReportForm,
    extra=0,  # Number of empty forms to display
    can_delete=True,  # Allow deletion of existing forms
)

DisaggregationReportFormSet = inlineformset_factory(
    TargetLocationReport,
    DisaggregationLocationReport,
    fields="__all__",
    extra=0,  # Number of empty forms to display
)


class ActivityPlanReportForm(forms.ModelForm):
    class Meta:
        model = ActivityPlanReport
        fields = "__all__"

        widgets = {
            "activity_plan": forms.widgets.HiddenInput(),
            "report_types": forms.SelectMultiple(attrs={"class": "js_multiselect"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        (self.fields["indicator"].widget.attrs.update({"hidden": ""}),)


class RejectMonthlyReportForm(forms.Form):
    rejection_reason = forms.CharField(widget=forms.Textarea)


class IndicatorsForm(forms.ModelForm):
    class Meta:
        model = Indicator
        fields = "__all__"
