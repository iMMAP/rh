from curses.ascii import US
from statistics import mode
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(UserCreationForm):
    """Registration form"""

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        """check if username already exists"""
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username__iexact=username)
        if qs.exists():
            raise forms.ValidationError(
                f"{username} is invalid, please pick another."
            )
        return username

    def clean_email(self):
        """check if email already exists"""
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email__iexact=email)
        if qs.exists():
            raise forms.ValidationError(
                f"{email} is invalid, please pick another."
            )
        return email

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
