from django import forms
from django.forms import BaseInlineFormSet
from django.forms.models import inlineformset_factory
from django.urls import reverse_lazy
from rh.models import ActivityPlan, Disaggregation, Indicator, TargetLocation

from .models import (
    ActivityPlanReport,
    DisaggregationLocationReport,
    ProjectMonthlyReport,
    ResponseType,
    TargetLocationReport,
)


class ProjectMonthlyReportForm(forms.ModelForm):
    class Meta:
        model = ProjectMonthlyReport
        fields = "__all__"
        widgets = {
            "from_date": forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "onfocus": "(this.type='date')",
                    "onblur": "(this.type='text')",
                }
            ),
            "to_date": forms.widgets.DateInput(
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
        exclude = ("activity_plan_report",)
        widgets = {
            "facility_site_type": forms.Select(attrs={"class": "custom-select"}),
        }

    def __init__(self, *args, **kwargs):
        plan_report = kwargs.pop("plan_report", None)
        super().__init__(*args, **kwargs)

        self.fields["target_location"].widget = forms.Select(
            attrs={
                "class": "custom-select",
                "hx-post": reverse_lazy("hx_get_diaggregation_tabular_form"),
                "hx-target": "#target-location-info",
                "hx-indicator": ".progress",
                "hx-trigger": "change",
            }
        )
        self.fields["target_location"].queryset = TargetLocation.objects.filter(
            activity_plan=plan_report.activity_plan, state="in-progress"
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
        self.target_location = kwargs.pop("target_location", None)

        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs["target_location"] = self.target_location

        return super()._construct_form(i, **kwargs)


class DisaggregationLocationReportForm(forms.ModelForm):
    class Meta:
        model = DisaggregationLocationReport
        fields = (
            "disaggregation",
            "reached",
        )

    def __init__(self, *args, **kwargs):
        target_location = kwargs.pop("target_location", None)

        super().__init__(*args, **kwargs)

        self.fields["disaggregation"].required = True
        self.fields["disaggregation"].empty_value = "-----"
        self.fields["reached"].required = True
        self.fields["reached"].widget.attrs["placeholder"] = "Enter target reached"

        if target_location:
            self.fields["disaggregation"].queryset = Disaggregation.objects.filter(
                disaggregationlocation__target_location=target_location
            )

        if self.instance.pk:
            # updating
            self.fields["disaggregation"].queryset = Disaggregation.objects.filter(
                disaggregationlocationreport__target_location_report=self.instance.target_location_report,
                disaggregationlocationreport__disaggregation=self.instance.disaggregation,
            )


class ActivityPlanReportForm(forms.ModelForm):
    class Meta:
        model = ActivityPlanReport
        fields = "__all__"
        exclude = ("monthly_report",)

        widgets = {
            "response_types": forms.SelectMultiple(attrs={"class": "custom-select"}),
            "beneficiary_status": forms.Select(attrs={"class": "custom-select"}),
            "package_type": forms.Select(attrs={"class": "custom-select"}),
            "unit_type": forms.Select(attrs={"class": "custom-select"}),
            "grant_type": forms.Select(attrs={"class": "custom-select"}),
            "transfer_category": forms.Select(attrs={"class": "custom-select"}),
            "currency": forms.Select(attrs={"class": "custom-select"}),
            "transfer_mechanism_type": forms.Select(attrs={"class": "custom-select"}),
            "implement_modility_type": forms.Select(attrs={"class": "custom-select"}),
            "seasonal_retargeting": forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        monthly_report = kwargs.pop("monthly_report", None)

        super().__init__(*args, **kwargs)

        self.fields["response_types"].queryset = ResponseType.objects.filter(
            clusters__in=monthly_report.project.clusters.values_list("id"),
            is_active=True,
        )

        self.fields["activity_plan"].widget = forms.Select(
            attrs={
                "class": "custom-select",
                "hx-post": reverse_lazy("hx-acitivity-plans-info"),
                "hx-target": "#activity-plan-info",
                "hx-indicator": ".progress",
                "hx-trigger": "change",
            }
        )
        self.fields["activity_plan"].queryset = ActivityPlan.objects.filter(
            project=monthly_report.project.pk, state="in-progress"
        ).select_related("activity_domain")

        self.fields["prev_targeted_by"].queryset = Indicator.objects.filter(
            activity_types__activityplan__project=monthly_report.project
        )


class RejectMonthlyReportForm(forms.Form):
    rejection_reason = forms.CharField(widget=forms.Textarea)


class MonthlyReportFileUpload(forms.Form):
    """
    File upload form for monthly reports data import
    """

    file = forms.FileField()
