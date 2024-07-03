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
    Organization,
    Project,
    ProjectIndicatorType,
    TargetLocation,
    ActivityDomain,
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
        exclude = (
            "disaggregations",
            "project",
            "active",
            "state",
            "locations_group_by",
            "group_by_province",
            "group_by_district",
            "group_by_custom",
            "activity_plan",
        )
        widgets = {
            # "country": forms.widgets.HiddenInput(),
            # "nhs_code": forms.widgets.TextInput(),
            # "locations_group_by": forms.widgets.RadioSelect(),
            # "district": forms.Select(attrs={"locations-queries-url": reverse_lazy("ajax-load-locations")}),
            # "zone": forms.Select(attrs={"locations-queries-url": reverse_lazy("ajax-load-locations")}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["province"].queryset = self.fields["province"].queryset.filter(type="Province")
        self.fields["district"].queryset = self.fields["district"].queryset.filter(type="District")
        self.fields["zone"].queryset = self.fields["zone"].queryset.filter(type="Zone")


TargetLocationFormSet = inlineformset_factory(
    ActivityPlan,
    TargetLocation,
    form=TargetLocationForm,
    extra=2,  # Number of empty forms to display
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
        # TODO: limit this to the acitivity plan indicator specific disaggredations


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
        exclude = ["state", "active", "project"]

    def __init__(self, *args, **kwargs):
        # user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["activity_domain"] = forms.ModelChoiceField(
            queryset=ActivityDomain.objects.all(),
            required=True,
            empty_label="---------",
            widget=forms.Select(attrs={"class": "custom-select"}),
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
