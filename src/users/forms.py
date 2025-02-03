from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class UserRegisterForm(UserCreationForm):
    """Subclass User Registration form"""

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def clean_username(self):
        """check if username already exists"""
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username__iexact=username)
        if qs.exists():
            raise forms.ValidationError(f"Username {username} already exists, please choose another.")
        return username

    def clean_email(self):
        """check if email already exists"""
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email__iexact=email)
        if qs.exists():
            raise forms.ValidationError(f"Email {email} already exists, please choose another.")
        return email


class ProfileCreateForm(forms.ModelForm):
    """Profile Create form"""

    class Meta:
        model = Profile
        fields = ["position", "phone", "organization", "clusters", "country"]
        labels = {"clusters": "Clusters / Sectors"}
        help_texts = {
            "organization": "If your organization is not listed, please contact us",
            "clusters": "Select clusters that you will be responsible for",
        }

        widgets = {
            "clusters": forms.SelectMultiple(attrs={"class": "custom-select"}),
            "organization": forms.Select(attrs={"class": "custom-select"}),
            "country": forms.Select(attrs={"class": "custom-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["position"].required = True
        self.fields["organization"].required = True
        self.fields["clusters"].required = True
        self.fields["country"].required = True
        self.fields["phone"].required = True


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

        widgets = {
            "email": forms.TextInput(attrs={"readonly": "readonly", "class": "cursor-none"}),
        }


class ProfileUpdateForm(forms.ModelForm):
    """Profile Update form"""

    class Meta:
        model = Profile
        fields = "__all__"
        exclude = ("email_verified_at", "old_id", "is_cluster_contact", "visits", "name", "user")
        labels = {"name": "Full Name", "clusters": "Clusters / Sectors"}

        widgets = {
            "clusters": forms.SelectMultiple(attrs={"class": "custom-select"}),
            "country": forms.Select(attrs={"class": "custom-select", "disabled": "disabled"}),
            "organization": forms.Select(attrs={"class": "custom-select", "disabled": "disabled"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
