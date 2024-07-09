from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from django.shortcuts import render

from ..forms import (
    OrganizationForm,
)


# Registration Organizations
@login_required
@permission_required("rh.add_organization", raise_exception=True)
def organization_register(request):
    if request.method == "POST":
        org_form = OrganizationForm(request.POST, user=request.user)

        if org_form.is_valid():
            code = org_form.cleaned_data.get("code")
            org_code = code.upper()
            organization = org_form.save()

            if organization:
                messages.success(request, f"{org_code} is registered successfully !")
            else:
                messages.error(request, "Something went wrong ! please try again ")
    else:
        org_form = OrganizationForm(user=request.user)

    context = {"org_form": org_form}

    return render(request, "rh/organization_form.html", context)
