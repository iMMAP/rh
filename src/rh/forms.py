from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from django.urls import reverse_lazy

from .models import (
    ActivityPlan,
    BudgetProgress,
    Cluster,
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
        exclude = ["organization"]

        widgets = {
            "clusters": forms.SelectMultiple(
                attrs={
                    "class": "custom-select",
                }
            ),
            "donors": forms.SelectMultiple(attrs={"class": "custom-select"}),
            "implementing_partners": forms.SelectMultiple(attrs={"class": "custom-select"}),
            "programme_partners": forms.SelectMultiple(attrs={"class": "custom-select"}),
            "user": forms.Select(attrs={"class": "custom-select"}),
            "activity_domains": forms.SelectMultiple(
                attrs={
                    "class": "",
                    "activity-domains-queries-url": reverse_lazy("ajax-load-activity_domains"),
                    "id": "id_activity_domains",
                }
            ),
            "start_date": forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "class": "start-date",
                }
            ),
            "end_date": forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "class": "end-date",
                }
            ),
            "active": forms.widgets.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        if self.instance.pk:
            # Update mode
            self.fields["activity_domains"].choices = (
                self.instance.activity_domains.all().order_by("name").values_list("pk", "name")
            )

            if self.instance.user:
                # join the project selected clusters with the user's current clusters
                user_clusters = self.instance.user.profile.clusters.all()
                project_clusters = self.instance.clusters.all()
                self.fields["clusters"].queryset = Cluster.objects.filter(
                    pk__in=user_clusters.union(project_clusters).values("pk")
                )

            # Show only the project's organization members
            self.fields["user"].queryset = User.objects.filter(profile__organization=self.instance.organization)
        else:
            # Create mode
            self.fields["activity_domains"].choices = []
            self.fields["clusters"].queryset = user.profile.clusters.all()
            # Show only the user's organization members
            self.fields["user"].queryset = User.objects.filter(profile__organization=user.profile.organization)
            self.fields["user"].initial = user

        self.fields["donors"].queryset = Donor.objects.order_by("name")
        self.fields["budget_currency"].queryset = Currency.objects.order_by("name")

        orgs = Organization.objects.order_by("name").values_list("pk", "code")
        self.fields["implementing_partners"].choices = orgs
        self.fields["programme_partners"].choices = orgs


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
        # accessing user location
        form_prefix=kwargs.get("prefix")
        prefix_data_list=form_prefix.split(',')
        user_location=prefix_data_list[0]
        # update the prefix 
        kwargs['prefix']=prefix_data_list[1]
        
        super().__init__(*args, **kwargs)
        self.fields["save"] = forms.BooleanField(
            required=False,
            initial=False,
            widget=forms.HiddenInput(attrs={"name": self.prefix + "-save"}),
        )

        cluster_has_nhs_code = False
        activity_plan = False
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

        self.fields["province"].queryset = self.fields["province"].queryset.filter(type="Province", parent_id=user_location)
        self.fields["district"].queryset = self.fields["district"].queryset.filter(type="District")

        # Get only the relevant facility types - related to cluster
        if activity_plan:
            self.fields["facility_site_type"].queryset = FacilitySiteType.objects.filter(
                cluster__in=activity_plan.activity_domain.clusters.all()
            )
        else:
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
        if budget_currency:
            self.fields["budget_currency"].queryset = self.fields["budget_currency"].queryset.filter(
                pk=budget_currency.pk
            )


class OrganizationRegisterForm(forms.ModelForm):
    """Organization Registeration Form"""

    class Meta:
        model = Organization
        fields = "__all__"
        exclude = ("old_id",)
        labels = {"clusters": "Clusters / Sectors", "name": "Organization Name"}

        widgets = {
            "clusters": forms.SelectMultiple(attrs={"class": "custom-select"}),
            "countries": forms.SelectMultiple(attrs={"class": "custom-select"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            user_groups = user.groups.filter(name__endswith="_CLUSTER_LEADS")
            cluster_ids = [group.name.split("_")[0].lower() for group in user_groups]
            self.fields["clusters"].queryset = Cluster.objects.filter(code__in=cluster_ids)
        else:
            self.fields["clusters"].queryset = []

        if user and hasattr(user, "profile") and user.profile.country:
            self.fields["countries"].initial = user.profile.country

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
