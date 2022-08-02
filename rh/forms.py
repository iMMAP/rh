from django import forms

class ProjectForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={
        "class":"w-full rounded-lg focus:ring-primary-600 focus:border-primary-600"
    }), label='Project Title', max_length=100)
    
    description = forms.CharField(widget=forms.Textarea(attrs={
        "class":"w-full rounded-lg focus:ring-primary-600 focus:border-primary-600"
    }), label='Description')
    start_date = forms.DateField(widget=forms.widgets.TextInput(attrs={
        "type":"date",
        "class": "focus:ring-primary-600 rounded-lg focus:border-primary-600 w-full"
    }), label='Start date')
    end_date = forms.DateField(widget=forms.widgets.TextInput(attrs={
        "type":"date",
        "class": " focus:ring-primary-600 rounded-lg focus:border-primary-600 w-full"
    }), label='End date')
