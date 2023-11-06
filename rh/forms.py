from django import forms
from django.forms.models import inlineformset_factory
from django.urls import reverse_lazy

from .models import *


class FieldHandler:
    form_fields = {}

    def __init__(self, fields, initial_data=None):
        for field in fields:
            options = self.get_options(field)
            if initial_data:
                name = field.get("name", False)
                initials = initial_data.get(name, None)
            else:
                initials = None
            f = getattr(self, "create_field_for_" + field["type"])(
                field, options, initials
            )
            self.form_fields[field["name"]] = f

    def get_options(self, field):
        options = {
            "help_text": field.get("help_text", None),
            "required": bool(field.get("required", 0)),
        }
        return options

    def create_field_for_text(self, field, options, initials=None):
        options["max_length"] = int(field.get("max_length", "20"))
        return forms.CharField(
            widget=forms.TextInput(
                attrs={
                    "class": "form-control",
                    "type": "text",
                }
            ),
            initial=initials,
            **options,
        )

    def create_field_for_textarea(self, field, options, initials=None):
        options["max_length"] = int(field.get("max_value", "9999"))
        return forms.CharField(
            widget=forms.Textarea(
                attrs={
                    "class": "form-control",
                    "type": "text",
                }
            ),
            initial=initials,
            **options,
        )

    def create_field_for_integer(self, field, options, initials=None):
        options["max_value"] = int(field.get("max_value", "999999999"))
        options["min_value"] = int(field.get("min_value", "-999999999"))
        return forms.IntegerField(
            widget=forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "type": "number",
                }
            ),
            initial=initials,
            **options,
        )

    def create_field_for_radio(self, field, options, initials=None):
        options["choices"] = [(c.lower(), c.capitalize()) for c in field["value"]]
        return forms.ChoiceField(widget=forms.RadioSelect, initial=initials, **options)

    def create_field_for_select(self, field, options, initials=None):
        options["choices"] = [(c.lower(), c.capitalize()) for c in field["value"]]
        return forms.ChoiceField(
            widget=forms.Select(
                attrs={
                    "class": "form-control",
                    "type": "select",
                }
            ),
            initial=initials,
            **options,
        )

    def create_field_for_multi(self, field, options, initials=None):
        options["choices"] = [(c.lower(), c.capitalize()) for c in field["value"]]
        return forms.MultipleChoiceField(
            widget=forms.SelectMultiple(
                attrs={
                    "class": "form-control",
                    "type": "select",
                }
            ),
            initial=initials,
            **options,
        )

    def create_field_for_checkbox(self, field, options, initials=None):
        return forms.BooleanField(
            widget=forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                    "type": "checkbox",
                }
            ),
            initial=initials,
            **options,
        )


def get_dynamic_form(json_fields, initial_data=None):
    if not json_fields:
        return
    fields_list = json_fields.get("fields", [])
    field_handler = FieldHandler(fields_list, initial_data)
    return type("DynamicForm", (forms.Form,), field_handler.form_fields)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"

        widgets = {
            "clusters": forms.SelectMultiple(attrs={"class": "js_multiselect"}),
            "donors": forms.SelectMultiple(attrs={"class": "js_multiselect"}),
            "implementing_partners": forms.SelectMultiple(
                attrs={"class": "js_multiselect"}
            ),
            "programme_partners": forms.SelectMultiple(
                attrs={"class": "js_multiselect"}
            ),
            "activity_domains": forms.SelectMultiple(
                attrs={
                    "class": "js_multiselect",
                    "activity-domains-queries-url": reverse_lazy(
                        "ajax-load-activity_domains"
                    ),
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
            user_clusters = list(
                user_profile.clusters.all().values_list("pk", flat=True)
            )

        self.fields["clusters"].queryset = self.fields["clusters"].queryset.filter(
            id__in=user_clusters
        )
        self.fields["donors"].queryset = Donor.objects.order_by("name")
        self.fields["budget_currency"].queryset = Currency.objects.order_by("name")
        self.fields["implementing_partners"].queryset = Organization.objects.order_by(
            "name"
        )
        self.fields["programme_partners"].queryset = Organization.objects.order_by(
            "name"
        )
        self.fields["user"].queryset = User.objects.order_by("username")


class TargetLocationForm(forms.ModelForm):
    class Meta:
        model = TargetLocation
        fields = "__all__"
        widgets = {
            "country": forms.widgets.HiddenInput(),
            "active": forms.widgets.HiddenInput(),
            "locations_group_by": forms.widgets.RadioSelect(),
            "district": forms.Select(
                attrs={"locations-queries-url": reverse_lazy("ajax-load-locations")}
            ),
            "zone": forms.Select(
                attrs={"locations-queries-url": reverse_lazy("ajax-load-locations")}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["save"] = forms.BooleanField(
            required=False,
            initial=False,
            widget=forms.HiddenInput(attrs={"name": self.prefix + "-save"}),
        )
        self.fields["province"].queryset = self.fields["province"].queryset.filter(
            type="Province"
        )
        self.fields["district"].queryset = self.fields["district"].queryset.filter(
            type="District"
        )
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
        self.fields["site_name"].widget.attrs.update(
            {
                "onchange": f"updateLocationTitle('{kwargs.get('prefix')}', 'id_{kwargs.get('prefix')}-site_name');"
            }
        )


TargetLocationFormSet = inlineformset_factory(
    ActivityPlan,
    TargetLocation,
    form=TargetLocationForm,
    extra=0,  # Number of empty forms to display
    can_delete=True,  # Allow deletion of existing forms
)

DisaggregationFormSet = inlineformset_factory(
    TargetLocation,
    DisaggregationLocation,
    fields="__all__",
    extra=0,  # Number of empty forms to display
)


class ActivityPlanForm(forms.ModelForm):
    class Meta:
        model = ActivityPlan
        fields = "__all__"
        widgets = {
            "facility_type": forms.Select(
                attrs={
                    "facility-sites-queries-url": reverse_lazy(
                        "ajax-load-facility_sites"
                    )
                }
            ),
        }

    def __init__(self, *args, project, **kwargs):
        super().__init__(*args, **kwargs)
        clusters = project.clusters.all()
        activity_domains = project.activity_domains.all()
        activity_domains = list(activity_domains.all().values_list("pk", flat=True))
        cluster_ids = list(clusters.values_list("pk", flat=True))

        self.fields["save"] = forms.BooleanField(
            required=False,
            initial=False,
            widget=forms.HiddenInput(attrs={"name": self.prefix + "-save"}),
        )
        self.fields["activity_domain"].queryset = self.fields[
            "activity_domain"
        ].queryset.filter(pk__in=activity_domains)
        self.fields["activity_domain"].widget.attrs.update(
            {
                "data-form-prefix": f"{kwargs.get('prefix')}",
                "onchange": f"updateActivityTitle('{kwargs.get('prefix')}', 'id_{kwargs.get('prefix')}-activity_domain');",
            }
        )
        self.fields["activity_type"].widget.attrs.update(
            {
                "onchange": f"updateActivityTitle('{kwargs.get('prefix')}', 'id_{kwargs.get('prefix')}-activity_type');"
            }
        )
        self.fields["activity_detail"].widget.attrs.update(
            {
                "onchange": f"updateActivityTitle('{kwargs.get('prefix')}', 'id_{kwargs.get('prefix')}-activity_detail');"
            }
        )
        self.fields["indicators"].widget.attrs.update({"style": "height: 128px;"})
        # self.fields['facility_type'].queryset = self.fields['facility_type'].queryset.filter(cluster__in=cluster_ids)


ActivityPlanFormSet = inlineformset_factory(
    Project,
    ActivityPlan,
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
        self.fields["activity_domain"].queryset = self.fields[
            "activity_domain"
        ].queryset.filter(pk__in=activity_domains)
        self.fields["donor"].queryset = self.fields["donor"].queryset.filter(
            pk__in=donor_ids
        )
        self.fields["budget_currency"].queryset = self.fields[
            "budget_currency"
        ].queryset.filter(pk=budget_currency.pk)
