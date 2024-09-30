import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from project_reports.models import ProjectMonthlyReport
from rh.models import Organization, TargetLocation
from rh.utils import is_cluster_lead

from ..forms import (
    OrganizationForm,
    UpdateOrganizationForm,
)


@login_required
def dashboard_5w(request, code):
    org = get_object_or_404(Organization, code=code)

    if not org.code == request.user.profile.organization.code and not is_cluster_lead(
        request.user, org.clusters.values_list("code", flat=True)
    ):
        raise PermissionDenied

    user_org = request.user.profile.organization

    from_date = request.GET.get("from", datetime.date(datetime.datetime.now().year, 1, 1))
    to_date = request.GET.get("to", datetime.datetime.now().date())

    counts = ProjectMonthlyReport.objects.filter(
        project__organization=user_org,
        state__in=["submited", "completed"],
        from_date__lte=to_date,
        to_date__gte=from_date,
    ).aggregate(
        report_indicators_count=Count("activityplanreport__activity_plan__indicator", distinct=True),
        report_implementing_partners_count=Count(
            "activityplanreport__targetlocationreport__target_location__implementing_partner", distinct=True
        ),
        report_target_location_province_count=Count(
            "activityplanreport__targetlocationreport__target_location__province", distinct=True
        ),
    )

    people_reached_data = (
        ProjectMonthlyReport.objects.filter(
            project__organization=user_org,
            state__in=["submited", "completed"],
            from_date__lte=to_date,
            to_date__gte=from_date,
            activityplanreport__beneficiary_status="new_beneficiary",
        )
        .order_by("from_date")
        .values("from_date")
        .annotate(
            total_people_reached=Sum("activityplanreport__targetlocationreport__disaggregationlocationreport__reached")
        )
    )

    counts["people_reached"] = sum(report["total_people_reached"] for report in people_reached_data)

    labels = [report["from_date"].strftime("%b") for report in people_reached_data]
    data = [
        report["total_people_reached"] if report["total_people_reached"] is not None else 0
        for report in people_reached_data
    ]

    # people reached by activities
    activity_domains = (
        ProjectMonthlyReport.objects.filter(
            project__organization=user_org,
            state__in=["in-progress", "completed"],
            from_date__lte=to_date,
            to_date__gte=from_date,
            activityplanreport__beneficiary_status="new_beneficiary",
        )
        .values_list("activityplanreport__activity_plan__activity_domain__name", flat=True)
        .distinct()
    )

    reach_by_activity = (
        ProjectMonthlyReport.objects.filter(
            project__organization=user_org,
            state__in=["submited", "completed"],
            from_date__lte=to_date,
            to_date__gte=from_date,
            activityplanreport__beneficiary_status="new_beneficiary",
        )
        .values(
            "activityplanreport__targetlocationreport__disaggregationlocationreport__disaggregation__name",
            "activityplanreport__activity_plan__activity_domain__name",
        )
        .annotate(
            total_people_reached=Sum("activityplanreport__targetlocationreport__disaggregationlocationreport__reached"),
        )
    )

    # Organize data into a dictionary
    data_dict = {}
    for entry in reach_by_activity:
        disaggregation_name = entry[
            "activityplanreport__targetlocationreport__disaggregationlocationreport__disaggregation__name"
        ]
        activity_domain = entry["activityplanreport__activity_plan__activity_domain__name"]
        total_reached = entry["total_people_reached"]

        if disaggregation_name not in data_dict:
            data_dict[disaggregation_name] = {}

        data_dict[disaggregation_name][activity_domain] = total_reached

    context = {
        "org": org,
        "counts": counts,
        "people_reached_labels": labels,
        "people_reached_data": data,
        "activity_domains": activity_domains,
        "reach_by_activity": data_dict,
    }

    return render(request, "rh/5w_dashboard.html", context)


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
