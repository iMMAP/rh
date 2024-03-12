from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
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
            raise forms.ValidationError(f"{username} is an invalid username, please pick another.")
        return username

    def clean_email(self):
        """check if email already exists"""
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email__iexact=email)
        if qs.exists():
            raise forms.ValidationError(f"{email} is an invalid email address, please pick another.")
        return email


class ProfileCreateForm(forms.ModelForm):
    """Profile Create form"""

    class Meta:
        model = Profile
        fields = ["position", "organization", "clusters", "country"]
        labels = {"clusters": "Clusters / Sectors"}

        widgets = {
            "clusters": forms.SelectMultiple(attrs={"class": "custom-select"}),
            "organization": forms.Select(attrs={"class": "custom-select"}),
            "country": forms.Select(attrs={"class": "custom-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["country"].queryset = self.fields["country"].queryset.filter(type="Country")


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
        exclude = ("old_id", "is_cluster_contact", "visits", "name", "user")
        labels = {"name": "Full Name", "clusters": "Clusters / Sectors"}

        widgets = {
            "clusters": forms.SelectMultiple(attrs={"class": "custom-select"}),
            "country": forms.Select(attrs={"class": "custom-select", "disabled": "disabled"}),
            "organization": forms.Select(attrs={"class": "custom-select", "disabled": "disabled"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["country"].queryset = self.fields["country"].queryset.filter(type="Country")


class UserPasswordChangeForm(PasswordChangeForm):
    """Subclass Password change form to remove labels and classes"""

    def __init__(self, *args, **kwargs):
        """Call super"""
        super().__init__(*args, **kwargs)

    old_password = forms.CharField(
        label="Current Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "autofocus": True,
                "class": "form-control",
                "placeholder": "Current Password",
                "type": "password",
                "name": "old_password",
            }
        ),
    )

    new_password1 = forms.CharField(
        label="New Password",
        help_text=password_validation.password_validators_help_text_html(),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "New Password",
                "type": "password",
                "name": "new_password1",
                "autocomplete": "new-password",
            }
        ),
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm New Password",
                "type": "password",
                "name": "new_password2",
                "autocomplete": "new-password",
            }
        ),
    )


class UserSetPasswordForm(SetPasswordForm):
    """Override password reset form to add styling to the input fields"""

    def __init__(self, *args, **kwargs):
        """Call super"""
        super().__init__(*args, **kwargs)

    new_password1 = forms.CharField(
        label="",
        help_text=password_validation.password_validators_help_text_html(),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "New Password",
                "type": "password",
                "name": "new_password1",
                "autocomplete": "new-password",
            }
        ),
    )
    new_password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm New Password",
                "type": "password",
                "name": "new_password2",
                "autocomplete": "new-password",
            }
        ),
    )


class UserPasswordResetForm(PasswordResetForm):
    """Override password reset form to add styling to the input fields"""

    def __init__(self, *args, **kwargs):
        """Call super"""
        super().__init__(*args, **kwargs)

    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g abc@gmail.com",
                "type": "email",
                "name": "email",
            }
        ),
    )
