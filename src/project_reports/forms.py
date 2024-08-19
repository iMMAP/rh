from django import forms
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404
from django.forms import BaseInlineFormSet

from rh.models import FacilitySiteType, Indicator, Organization, TargetLocation, Disaggregation

from .models import (
    ActivityPlanReport,
    DisaggregationLocationReport,
    ProjectMonthlyReport,
    TargetLocationReport,
)


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
                }
            ),
        }


class TargetLocationReportForm(forms.ModelForm):
    class Meta:
        model = TargetLocationReport
        fields = "__all__"
        widgets = {
            "nhs_code": forms.widgets.TextInput(),
            "facility_site_type": forms.Select(attrs={"class": "custom-select"}),
            "target_location": forms.Select(attrs={"class": "custom-select"}),
        }

    def __init__(self, *args, **kwargs):
        plan_report = kwargs.pop("plan_report", None)
        super().__init__(*args, **kwargs)
      
        self.fields["target_location"].queryset = TargetLocation.objects.filter(
            activity_plan=plan_report.activity_plan
        )


TargetLocationReportFormSet = inlineformset_factory(
    ActivityPlanReport,
    TargetLocationReport,
    form=TargetLocationReportForm,
    extra=0,  # Number of empty forms to display
    can_delete=False,  # Allow deletion of existing forms
)


class BaseDisaggregationLocationReportFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.plan_report = kwargs.pop("plan_report", None)
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs["plan_report"] = self.plan_report
        return super()._construct_form(i, **kwargs)


class DisaggregationLocationReportForm(forms.ModelForm):
    class Meta:
        model = DisaggregationLocationReport
        fields = (
            "disaggregation",
            "reached",
        )

    def __init__(self, *args, **kwargs):
        plan_report = kwargs.pop("plan_report", None)
        super().__init__(*args, **kwargs)

        self.fields["disaggregation"].required = True
        self.fields["disaggregation"].empty_value = "hell"
        self.fields["reached"].required = True

        if plan_report:
            self.fields["disaggregation"].queryset = self.fields["disaggregation"].queryset.filter(
                indicators=plan_report.activity_plan.indicator
            )
            # keep only the initial

        if self.instance.pk:
            self.fields["disaggregation"].queryset = Disaggregation.objects.filter(
                disaggregationlocationreport__target_location_report=self.instance.target_location_report,
                disaggregationlocationreport__disaggregation=self.instance.disaggregation,
            )


class ActivityPlanReportForm(forms.ModelForm):
    class Meta:
        model = ActivityPlanReport
        fields = "__all__"

        widgets = {
            "monthly_report":forms.HiddenInput(),
            "activity_plan": forms.Select(attrs={"class":"custom-select"}),
            "response_type": forms.SelectMultiple(attrs={"class": "custom-select"}),
            "beneficiary_status": forms.Select(attrs={"class": "custom-select"}),
            "seasonal_retargeting":forms.CheckboxInput(),
            "modality_retargeting":forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        report = kwargs.pop("report", None)
        super().__init__(*args, **kwargs)

        self.fields["monthly_report"].initial = report.id

        self.fields["activity_plan"].queryset = self.fields["activity_plan"].queryset.filter(project=report.project)
        self.fields["activity_plan"].required = True 
        self.fields["beneficiary_status"].required = True 

class RejectMonthlyReportForm(forms.Form):
    rejection_reason = forms.CharField(widget=forms.Textarea)


class MonthlyReportFileUpload(forms.Form):
    """
    File upload form for monthly reports data import
    """

    file = forms.FileField()
