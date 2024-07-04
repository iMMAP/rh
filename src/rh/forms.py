from django import forms
from django.contrib.auth.models import User
from django.forms import BaseInlineFormSet
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
    BeneficiaryType,
    Indicator,
    ActivityType,
    Location,
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
            "activity_plan",
        )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["country"].disabled = True
        self.fields["country"].initial = user.profile.country
        self.fields["country"].required = True  # Ensure the field is required

        self.fields["province"].required = True 
        self.fields["province"].queryset = self.fields["province"].queryset.filter(level=1, parent=user.profile.country)

        self.fields["district"].queryset = Location.objects.none()
        self.fields["district"].required = True

        self.fields["zone"].queryset = Location.objects.none()

        if self.data:
            # Creating
            try:
                province_id = int(self.data.get("province"))
                self.fields["district"].queryset = Location.objects.filter(level=2,parent=province_id)
                
                district_id = int(self.data.get("district"))
                self.fields["zone"].queryset = Location.objects.filter(level=3,parent=district_id)
            except Exception:
                raise forms.ValidationError("Do not mess with the form!")

        elif self.instance.pk:
            # Updating
            self.fields["district"].queryset = self.instance.province.children.all()
            self.fields["zone"].queryset = self.instance.district.children.all()

    def clean_country(self):
        # Prevent changes to the country field
        initial_country = self.fields["country"].initial
        country = self.cleaned_data.get("country")

        if country != initial_country:
            raise forms.ValidationError("Country field cannot be changed.")

        return initial_country


class DisaggregationLocationForm(forms.ModelForm):
    class Meta:
        model = DisaggregationLocation
        fields = (
            "disaggregation",
            "target",
        )

    def __init__(self, *args, **kwargs):
        activity_plan = kwargs.pop("activity_plan", None)
        super().__init__(*args, **kwargs)

        if activity_plan:
            self.fields["disaggregation"].queryset = self.fields["disaggregation"].queryset.filter(
                indicators=activity_plan.indicator
            )
            # keep only the initial
            # self.fields["disaggregation"].choices = []
        # else:
        # print("ELSE ===  NO Target Location in Form",kwargs)
        #     # Do not display already existing relationships, filter based on target_location.activity_plan.indicator
        #     existing_disaggregations = DisaggregationLocation.objects.filter(
        #         target_location=target_location
        #     ).values_list("disaggregation", flat=True)
        #     # existing_disaggregation_ids = existing_disaggregations.values_list('disaggregation', flat=True)
        #     self.fields["disaggregation"].queryset = self.fields["disaggregation"].queryset.exclude(
        #         id__in=existing_disaggregations
        #     )


class BaseDisaggregationLocationFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.activity_plan = kwargs.pop("activity_plan", None)
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs["activity_plan"] = self.activity_plan
        return super()._construct_form(i, **kwargs)


class ActivityPlanForm(forms.ModelForm):
    class Meta:
        model = ActivityPlan
        fields = "__all__"
        exclude = ["state", "active", "project"]

    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

        project = project or self.instance.project
        if project is None:
            raise forms.ValidationError("Project cannot be None.")

        self.fields["activity_domain"].required = True
        self.fields["activity_type"].required = True
        self.fields["indicator"].required = True
        self.fields["beneficiary"].required = True

        self.fields["activity_domain"].queryset = project.activity_domains.all()
        self.fields["beneficiary"].queryset = BeneficiaryType.objects.filter(clusters__in=project.clusters.all())

        # The choices, does not validate the data ,(self.fields["indicator"].widget.choices = [])
        # Updating the queryset for validation purposes
        # If the data does not matche the queryset, it throws error
        self.fields["indicator"].queryset = Indicator.objects.none()

        if self.data:
            try:
                # Creating
                activity_domain_id = int(self.data.get("activity_domain"))
                self.fields["activity_type"].queryset = ActivityType.objects.filter(activity_domain_id=activity_domain_id)

                activity_type_id = int(self.data.get("activity_type"))
                self.fields["indicator"].queryset = Indicator.objects.filter(activity_types=activity_type_id)
            except Exception:
                raise forms.ValidationError("Do not mess with the form!")
        elif self.instance.pk:
            # Updating
            self.fields["activity_type"].queryset = self.instance.activity_domain.activitytype_set.all()
            self.fields["indicator"].queryset = self.instance.activity_type.indicator_set.all()


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
