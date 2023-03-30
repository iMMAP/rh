from .models import *

from django import forms
from django.urls import reverse_lazy


class FieldHandler:
    form_fields = {}

    def __init__(self, fields, initial_data=None):
        for field in fields:
            options = self.get_options(field)
            if initial_data:
                name = field.get('name', False)
                initials = initial_data.get(name, None)
            else:
                initials = None
            f = getattr(self, "create_field_for_"+field['type'] )(field, options, initials)
            self.form_fields[field['name']] = f

    def get_options(self, field):
        options = {'help_text': field.get("help_text", None), 'required': bool(field.get("required", 0))}
        return options

    def create_field_for_text(self, field, options, initials=None):
        options['max_length'] = int(field.get("max_length", "20") )
        return forms.CharField(widget=forms.TextInput(attrs={
                                     'class': 'form-control',
                                     'type': 'text',
                                 }), initial=initials, **options)

    def create_field_for_textarea(self, field, options, initials=None):
        options['max_length'] = int(field.get("max_value", "9999") )
        return forms.CharField(widget=forms.Textarea(attrs={
                                     'class': 'form-control',
                                     'type': 'text',
                                 }), initial=initials, **options)

    def create_field_for_integer(self, field, options, initials=None):
        options['max_value'] = int(field.get("max_value", "999999999") )
        options['min_value'] = int(field.get("min_value", "-999999999") )
        return forms.IntegerField(widget=forms.NumberInput(attrs={
                                     'class': 'form-control',
                                     'type': 'number',
                                 }), initial=initials, **options)

    def create_field_for_radio(self, field, options, initials=None):
        options['choices'] = [ (c.lower(), c.capitalize() ) for c in field['value'] ]
        return forms.ChoiceField(widget=forms.RadioSelect, initial=initials, **options)

    def create_field_for_select(self, field, options, initials=None):
        options['choices']  = [ (c.lower(), c.capitalize() ) for c in field['value'] ]
        return forms.ChoiceField(widget=forms.Select(attrs={
                                     'class': 'form-control',
                                     'type': 'select',
                                 }), initial=initials, **options)
    
    def create_field_for_multi(self, field, options, initials=None):
        options['choices']  = [ (c.lower(), c.capitalize() ) for c in field['value'] ]
        return forms.MultipleChoiceField(widget=forms.SelectMultiple(attrs={
                                     'class': 'form-control',
                                     'type': 'select',
                                 }), initial=initials, **options)

    def create_field_for_checkbox(self, field, options, initials=None):
        return forms.BooleanField(widget=forms.CheckboxInput(attrs={
                                     'class': 'form-check-input',
                                     'type': 'checkbox',
                                 }), initial=initials, **options)


def get_dynamic_form(json_fields, initial_data=None):
    if not json_fields:
        return
    fields_list = json_fields.get('fields', [])
    field_handler = FieldHandler(fields_list, initial_data)
    return type('DynamicForm', (forms.Form,), field_handler.form_fields)


class ActivityPlanForm(forms.ModelForm):
    # activity_plan = forms.CharField(widget=forms.HiddenInput(), required=False)
    activity_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = ActivityPlan
        fields = "__all__"
        widgets = {
            # 'activity_fields': forms.Textarea(attrs={'class': 'ajax-activity-fields-class', 'readonly':True, 'activityfields-queries-url': reverse_lazy('ajax-load-activityfields')}),
            'activity': forms.Select(attrs={'disabled': ''}),
        }

    def clean_activity_fields(self):
        if self.instance: 
            return self.instance.activity_fields
        else: 
            return self.fields['activity_fields']
        

class TargetLocationForm(forms.ModelForm):
    country_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    province_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    district_id = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = TargetLocation
        fields = "__all__"
        widgets = {
            'country': forms.Select(attrs={'disabled': ''}),
            'province': forms.Select(attrs={'disabled': ''}),
            'district': forms.Select(attrs={'disabled': ''}),
        }

    def __init__(self, *args, **kwargs):
        super(TargetLocationForm, self).__init__(*args, **kwargs)
        self.fields['country'].queryset = self.fields['country'].queryset.filter(type='Country')
        self.fields['province'].queryset = self.fields['province'].queryset.filter(type='Province')
        self.fields['district'].queryset = self.fields['district'].queryset.filter(type='District')



class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
    
        widgets = {
            'locations': forms.SelectMultiple(attrs={'class': 'js-example-basic-multiple', 'locations-queries-url': reverse_lazy('ajax-load-locations')}),
            'clusters': forms.SelectMultiple(attrs={'class': 'js-example-basic-multiple'}),
            'donors': forms.SelectMultiple(attrs={'class': 'js-example-basic-multiple'}),
            'activities': forms.SelectMultiple(attrs={'activities-queries-url': reverse_lazy('ajax-load-activities'),
                                            'class': 'js-example-basic-multiple'
                                            }),
            'start_date': forms.widgets.DateInput(attrs={'type': 'date', 'onfocus': "(this.type='date')", 'onblur':"(this.type='text')"}),
            'end_date': forms.widgets.DateInput(attrs={'type': 'date', 'onfocus': "(this.type='date')", 'onblur':"(this.type='text')"}),
            'active': forms.widgets.HiddenInput(),
        }    

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.fields['locations'].queryset = Location.objects.order_by('name')
        self.fields['clusters'].queryset = Cluster.objects.order_by('title')
        self.fields['donors'].queryset = Donor.objects.order_by('name')
        self.fields['activities'].queryset = Activity.objects.order_by('name')
        self.fields['budget_currency'].queryset = Currency.objects.order_by('name')
        self.fields['implementing_partner'].queryset = Organization.objects.order_by('name')
        self.fields['programme_partner'].queryset = Organization.objects.order_by('name')
        self.fields['user'].queryset = User.objects.order_by('username')