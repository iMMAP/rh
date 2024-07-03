from django import forms
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from rh.models import FacilitySiteType, Indicator, Organization, TargetLocation

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
            "district": forms.Select(
                attrs={"target-locations-queries-url": reverse_lazy("ajax-load-target-locations")}
            ),
            "zone": forms.Select(attrs={"target-locations-queries-url": reverse_lazy("ajax-load-target-locations")}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cluster_has_nhs_code = False
        plan_report = False
        if "instance" in kwargs and kwargs["instance"]:
            plan_report = kwargs["instance"]
            if plan_report:
                cluster_has_nhs_code = any(
                    cluster.has_nhs_code for cluster in plan_report.activity_plan.activity_domain.clusters.all()
                )
        nhs_code = f"{kwargs.get('prefix')}-nhs_code"
        has_nhs_code = nhs_code in kwargs.get("data", {})

        # Get only the relevant facility types - related to cluster
        if plan_report:
            self.fields["facility_site_type"].queryset = FacilitySiteType.objects.filter(
                cluster__in=plan_report.activity_plan.activity_domain.clusters.all()
            )
        else:
            self.fields["facility_site_type"].queryset = FacilitySiteType.objects.all()

        if cluster_has_nhs_code or has_nhs_code:
            self.fields["nhs_code"] = forms.CharField(max_length=200, required=True)
        else:
            self.fields.pop("nhs_code", None)

        if plan_report:
            self.fields["target_location"].queryset = TargetLocation.objects.filter(
                activity_plan=plan_report.activity_plan
            )


TargetLocationReportFormSet = inlineformset_factory(
    ActivityPlanReport,
    TargetLocationReport,
    form=TargetLocationReportForm,
    extra=0,  # Number of empty forms to display
    can_delete=True,  # Allow deletion of existing forms
)


class DisaggregationLocationReportForm(forms.ModelForm):
    class Meta:
        model = DisaggregationLocationReport
        fields = (
            "disaggregation",
            "target",
        )


DisaggregationReportFormSet = inlineformset_factory(
    TargetLocationReport,
    DisaggregationLocationReport,
    fields=(
        "disaggregation",
        "target",
    ),
    extra=0,  # Number of empty forms to display
)


class ActivityPlanReportForm(forms.ModelForm):
    class Meta:
        model = ActivityPlanReport
        fields = "__all__"

        widgets = {
            "activity_plan": forms.widgets.HiddenInput(),
            "report_types": forms.SelectMultiple(attrs={"class": "custom-select"}),
            "implementing_partners": forms.SelectMultiple(attrs={"class": "custom-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Retrieve the monthly_report_instance from initial data or instance
        monthly_report_id = self.initial.get("monthly_report")
        monthly_report_instance = get_object_or_404(ProjectMonthlyReport, pk=monthly_report_id)

        if monthly_report_instance:
            project = monthly_report_instance.project
            if project and project.implementing_partners.exists():
                organizations = project.implementing_partners.all()
            else:
                organizations = Organization.objects.all().order_by("name")
        else:
            organizations = Organization.objects.all().order_by("name")

        self.fields["indicator"].widget.attrs.update({"hidden": ""})
        self.fields["monthly_report"].widget.attrs.update({"hidden": ""})
        self.fields["activity_plan"].widget.attrs.update({"hidden": ""})
        self.fields["implementing_partners"].queryset = organizations
        self.fields["seasonal_retargeting"].widget = forms.CheckboxInput()
        self.fields["modality_retargeting"].widget = forms.CheckboxInput()


class RejectMonthlyReportForm(forms.Form):
    rejection_reason = forms.CharField(widget=forms.Textarea)


class IndicatorsForm(forms.ModelForm):
    class Meta:
        model = Indicator
        fields = "__all__"


class MonthlyReportFileUpload(forms.Form):
    """
    File upload form for monthly reports data import
    """

    file = forms.FileField()
