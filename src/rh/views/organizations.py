from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from rh.models import Organization, TargetLocation
from rh.utils import is_cluster_lead

from ..forms import (
    OrganizationForm,
    UpdateOrganizationForm,
)


@login_required
def search(request):
    """
    Search org for 5w filter. org is filtered by user's country.
    Route: /organizations/search?organization=[str]
    """
    organization = request.GET.get("organization")

    if organization:
        organizations = Organization.objects.filter(
            code__icontains=organization,
            countries__in=[
                request.user.profile.country,
            ],
        ).order_by("name")
    else:
        organizations = Organization.objects.none()

    return render(request, "rh/_org_select_options.html", {"options": organizations})


@login_required
def show(request, code):
    org = get_object_or_404(Organization, code=code)

    if not org.code == request.user.profile.organization.code and not is_cluster_lead(
        request.user, org.clusters.values_list("code", flat=True)
    ):
        raise PermissionDenied

    org_form = UpdateOrganizationForm(request.POST or None, instance=org)

    if request.method == "POST":
        if org_form.is_valid():
            org_form.save()
            messages.success(request, "Organization updated successfully!")
        else:
            messages.error(request, "Somthing went wrong please check the below errors !")

    context = {"org": org, "form": org_form}

    return render(request, "rh/org_show.html", context)


@login_required
def target_locations(request, org_pk):
    target_locations = cache.get(f"{org_pk}-target_locations")

    if not target_locations:
        target_locations = (
            TargetLocation.objects.select_related("project", "district", "province")
            .filter(project__organization_id=org_pk, project__state="in-progress")
            .order_by("province__name")
        )
        cache.set(f"{org_pk}-target_locations", target_locations, timeout=86400)  # Set timeout to 1 day (86400 seconds)

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
