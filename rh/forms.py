from django import forms

class ProjectForm(forms.Form):
    title = forms.CharField(label='Project Title', max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    start_date = forms.DateField(widget=forms.widgets.SelectDateWidget)
    end_date = forms.DateField(widget=forms.widgets.SelectDateWidget)
