from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from django.urls import reverse_lazy

from .models import (
    ActivityPlan,
    BudgetProgress,
    Currency,
    DisaggregationLocation,
    Donor,
    FacilitySiteType,
    Organization,
    Project,
    ProjectIndicatorType,
    TargetLocation,
)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"

        widgets = {
            "clusters": forms.SelectMultiple(
                attrs={
                    "class": "js_multiselect",
                }
            ),
            "donors": forms.SelectMultiple(attrs={"class": "js_multiselect"}),
            "implementing_partners": forms.SelectMultiple(attrs={"class": "js_multiselect"}),
            "programme_partners": forms.SelectMultiple(attrs={"class": "js_multiselect"}),
            "activity_domains": forms.SelectMultiple(
                attrs={
                    "class": "js_multiselect",
                    "activity-domains-queries-url": reverse_lazy("ajax-load-activity_domains"),
                    "id": "id_activity_domains",
                }
            ),
            "start_date": forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "onfocus": "(this.type='date')",
                    "onblur": "(this.type='text')",
                }
            ),
            "end_date": forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "onfocus": "(this.type='date')",
                    "onblur": "(this.type='text')",
                }
            ),
            "active": forms.widgets.HiddenInput(),
        }

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        user_profile = False
        user_clusters = []
        if self.initial.get("user", False):
            if isinstance(self.initial.get("user"), int):
                user_profile = User.objects.get(pk=self.initial.get("user")).profile
            else:
                user_profile = User.objects.get(pk=self.initial.get("user").pk).profile
        if args and args[0].get("user", False):
            user_profile = User.objects.get(pk=args[0].get("user")).profile

        if user_profile and user_profile.clusters:
            user_clusters = list(user_profile.clusters.all().values_list("pk", flat=True))

        # should not be empty when form is used in updating
        if self.instance.pk:
            # Update mode
            self.fields["activity_domains"].choices = (
                self.instance.activity_domains.all().order_by("name").values_list("pk", "name")
            )
        else:
            # Create mode
            self.fields["activity_domains"].choices = []

        self.fields["clusters"].queryset = self.fields["clusters"].queryset.filter(id__in=user_clusters)
        self.fields["donors"].queryset = Donor.objects.order_by("name")
        self.fields["budget_currency"].queryset = Currency.objects.order_by("name")

        orgs = Organization.objects.order_by("name").values_list("pk", "name")

        self.fields["implementing_partners"].choices = orgs
        self.fields["programme_partners"].choices = orgs
        self.fields["user"].queryset = User.objects.order_by("username")


class TargetLocationForm(forms.ModelForm):
    class Meta:
        model = TargetLocation
        fields = "__all__"
        exclude = ("disaggregations",)
        widgets = {
            "country": forms.widgets.HiddenInput(),
            "active": forms.widgets.HiddenInput(),
            "nhs_code": forms.widgets.TextInput(),
            "locations_group_by": forms.widgets.RadioSelect(),
            "district": forms.Select(attrs={"locations-queries-url": reverse_lazy("ajax-load-locations")}),
            "zone": forms.Select(attrs={"locations-queries-url": reverse_lazy("ajax-load-locations")}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["save"] = forms.BooleanField(
            required=False,
            initial=False,
            widget=forms.HiddenInput(attrs={"name": self.prefix + "-save"}),
        )

        cluster_has_nhs_code = False
        if "instance" in kwargs and kwargs["instance"]:
            activity_plan = kwargs["instance"].activity_plan
            if activity_plan:
                cluster_has_nhs_code = any(
                    cluster.has_nhs_code for cluster in activity_plan.activity_domain.clusters.all()
                )
        nhs_code = f"{kwargs.get('prefix')}-nhs_code"
        has_nhs_code = nhs_code in kwargs.get("data", {})

        if cluster_has_nhs_code or has_nhs_code:
            self.fields["nhs_code"] = forms.CharField(max_length=200, required=True)
        else:
            self.fields.pop("nhs_code", None)

        self.fields["province"].queryset = self.fields["province"].queryset.filter(type="Province")
        self.fields["district"].queryset = self.fields["district"].queryset.filter(type="District")
        # Get only the relevant facility types -  related to cluster
        self.fields["facility_site_type"].queryset = FacilitySiteType.objects.all()
        self.fields["zone"].queryset = self.fields["zone"].queryset.filter(type="Zone")
        self.fields["province"].widget.attrs.update(
            {
                "data-form-prefix": f"{kwargs.get('prefix')}",
                "onchange": f"updateLocationTitle('{kwargs.get('prefix')}', 'id_{kwargs.get('prefix')}-province');",
            }
        )
        self.fields["district"].widget.attrs.update(
            {
                "onchange": f"updateLocationTitle('{kwargs.get('prefix')}', 'id_{kwargs.get('prefix')}-district');",
                "locations-queries-url": reverse_lazy("ajax-load-locations"),
            }
        )


TargetLocationFormSet = inlineformset_factory(
    ActivityPlan,
    TargetLocation,
    form=TargetLocationForm,
    extra=0,  # Number of empty forms to display
    can_delete=True,  # Allow deletion of existing forms
)


class DisaggregationLocationForm(forms.ModelForm):
    class Meta:
        model = DisaggregationLocation
        fields = (
            "disaggregation",
            "target",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # target_location = None # get this from somewherr
        # target_location.disaggregationlocation_set.all():

        # TODO: limit this to the acitivity plan indicator specific disaggredations
        self.fields["disaggregation"].queryset = self.fields["disaggregation"].queryset


DisaggregationFormSet = inlineformset_factory(
    parent_model=TargetLocation,
    model=DisaggregationLocation,
    form=DisaggregationLocationForm,
    extra=0,  # Number of empty forms to display
)


class ActivityPlanForm(forms.ModelForm):
    class Meta:
        model = ActivityPlan
        fields = "__all__"

    def __init__(self, *args, project, **kwargs):
        super().__init__(*args, **kwargs)
        prefix = kwargs.get("prefix")
        instance = kwargs.get("instance", "")
        instance_id = ""
        if instance:
            instance_id = instance.pk

        self.fields["save"] = forms.BooleanField(
            required=False,
            initial=False,
            widget=forms.HiddenInput(attrs={"name": self.prefix + "-save"}),
        )
        self.fields["activity_domain"].queryset = project.activity_domains.all()
        self.fields["activity_domain"].widget.attrs.update(
            {
                "data-form-prefix": f"{prefix}",
                "onchange": f"updateActivityTitle('{prefix}', 'id_{prefix}-activity_domain');",
            }
        )
        self.fields["activity_type"].widget.attrs.update(
            {"onchange": f"updateActivityTitle('{prefix}', 'id_{prefix}-activity_type');"}
        )
        self.fields["activity_detail"].widget.attrs.update(
            {"onchange": f"updateActivityTitle('{prefix}', 'id_{prefix}-activity_detail');"}
        )
        self.fields["indicator"].widget.attrs.update(
            {"style": "20px", "data-prefix": prefix, "data-activity-plan": instance_id}
        )
        self.fields["indicator"].widget.attrs.update(
            {"onchange": "updateIndicatorTypes(event)", "data-indicator-url": reverse_lazy("update_indicator_type")}
        )


ActivityPlanFormSet = inlineformset_factory(
    parent_model=Project,
    model=ActivityPlan,
    form=ActivityPlanForm,
    extra=0,
    can_delete=True,
)


class BudgetProgressForm(forms.ModelForm):
    class Meta:
        model = BudgetProgress
        fields = "__all__"
        widgets = {
            "country": forms.widgets.HiddenInput(),
            "received_date": forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "onfocus": "(this.type='date')",
                    "onblur": "(this.type='text')",
                }
            ),
        }

    def __init__(self, *args, project, **kwargs):
        super().__init__(*args, **kwargs)

        activity_domains = project.activity_domains.all()
        budget_currency = project.budget_currency

        activity_domains = list(activity_domains.all().values_list("pk", flat=True))

        donors = project.donors.all()
        donor_ids = list(donors.values_list("pk", flat=True))

        self.fields["save"] = forms.BooleanField(
            required=False,
            initial=False,
            widget=forms.HiddenInput(attrs={"name": self.prefix + "-save"}),
        )
        self.fields["activity_domain"].queryset = self.fields["activity_domain"].queryset.filter(
            pk__in=activity_domains
        )
        self.fields["donor"].queryset = self.fields["donor"].queryset.filter(pk__in=donor_ids)
        self.fields["budget_currency"].queryset = self.fields["budget_currency"].queryset.filter(pk=budget_currency.pk)


class OrganizationRegisterForm(forms.ModelForm):
    """Organization Registeration Form"""

    class Meta:
        model = Organization
        fields = "__all__"
        exclude = ("old_id",)
        labels = {"clusters": "Clusters / Sectors", "name": "Organization Name"}

        widgets = {
            "clusters": forms.SelectMultiple(attrs={"class": "js_multiselect"}),
            "countries": forms.SelectMultiple(attrs={"class": "js_multiselect"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["countries"].queryset = self.fields["countries"].queryset.filter(type="Country")

    def clean_name(self):
        """check if organization name already exits"""
        name = self.cleaned_data.get("name")
        org_name = Organization.objects.filter(name__iexact=name)
        if org_name.exists():
            raise forms.ValidationError(f"{name} already exists...!")
        return name

    def clean_code(self):
        """check if organization code exists"""
        code = self.cleaned_data.get("code")
        org_code = Organization.objects.filter(code__iexact=code)
        if org_code.exists():
            raise forms.ValidationError(f"{code} aleady exists...!")
        return code


class ProjectIndicatorTypeForm(forms.ModelForm):
    class Meta:
        model = ProjectIndicatorType
        fields = "__all__"
        exclude = (
            "project",
            "indicator",
        )
