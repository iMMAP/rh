from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from django.shortcuts import render

from ..forms import (
    OrganizationForm,
)
from rh.models import TargetLocation
from django.http import JsonResponse


@login_required
def target_locations(request, org_pk):
    target_locations = (
        TargetLocation.objects.select_related("project", "district","province")
        .filter(project__organization_id=org_pk, project__state="in-progress")
        .order_by("province__name")
    )

    districts_grouped = {}

    for target_location in target_locations:
        district_id = target_location.district.id
        district_name = target_location.district.name

        if district_id not in districts_grouped:
            districts_grouped[district_id] = {
                "district_name": district_name,
                "district_id": district_id,
                "province_name": target_location.province.name,
                "district_code": target_location.district.code,
                "district_lat": target_location.district.lat,
                "district_long": target_location.district.long,
                "location_count": 0,
                "target_locations": [],
            }

        districts_grouped[district_id]["target_locations"].append(
            {
                "id": target_location.id,
                "project_code": target_location.project.code,
                "project_id": target_location.project.id,
                "state": target_location.state,
                "facility_name": target_location.facility_name,
            }
        )

        # Increment the location count
        districts_grouped[district_id]["location_count"] += 1

    # Convert the dictionary back to a list of dictionaries as per the desired output format
    districts_grouped_list = list(districts_grouped.values())

    return JsonResponse({"locations": districts_grouped_list})


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

    context = {"form": org_form}

    return render(request, "rh/organization_form.html", context)
