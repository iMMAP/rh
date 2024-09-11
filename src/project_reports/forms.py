from django import forms
from django.forms import BaseInlineFormSet
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from rh.models import ActivityPlan, Disaggregation, Organization, TargetLocation

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
            "implementing_partners": forms.SelectMultiple(attrs={"class": "custom-select"}),
            "beneficiary_status": forms.Select(attrs={"class": "custom-select"}),
            "package_type": forms.Select(attrs={"class": "custom-select"}),
            "unit_type": forms.Select(attrs={"class": "custom-select"}),
            "grant_type": forms.Select(attrs={"class": "custom-select"}),
            "transfer_category": forms.Select(attrs={"class": "custom-select"}),
            "currency": forms.Select(attrs={"class": "custom-select"}),
            "transfer_mechanism_type": forms.Select(attrs={"class": "custom-select"}),
            "implement_modility_type": forms.Select(attrs={"class": "custom-select"}),
        }

    def __init__(self, *args, **kwargs):
        monthly_report = kwargs.pop("monthly_report", None)
        report_plan = kwargs.get("instance", None)
        super().__init__(*args, **kwargs)

        # Retrieve the monthly_report_instance from initial data or instance
        monthly_report_id = monthly_report.pk if monthly_report else report_plan.monthly_report.pk

        monthly_report_instance = get_object_or_404(ProjectMonthlyReport, pk=monthly_report_id)

        if monthly_report_instance:
            project = monthly_report_instance.project
            if project and project.implementing_partners.exists():
                organizations = project.implementing_partners.all()
            else:
                organizations = Organization.objects.all().order_by("name")
        else:
            organizations = Organization.objects.all().order_by("name")

        self.fields["implementing_partners"].queryset = organizations
        self.fields["seasonal_retargeting"].widget = forms.CheckboxInput()

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
            project=monthly_report_instance.project.pk, state="in-progress"
        ).select_related("activity_domain")


class RejectMonthlyReportForm(forms.Form):
    rejection_reason = forms.CharField(widget=forms.Textarea)


class MonthlyReportFileUpload(forms.Form):
    """
    File upload form for monthly reports data import
    """

    file = forms.FileField()
