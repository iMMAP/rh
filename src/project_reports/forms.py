from django import forms
from django.forms.models import inlineformset_factory
from django.urls import reverse_lazy
from rh.models import FacilitySiteType, Indicator

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
            plan_report = kwargs["instance"].activity_plan_report
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


class MonthlyReportFileUpload(forms.Form):
    """
    File upload form for monthly reports data import
    """

    file = forms.FileField()
