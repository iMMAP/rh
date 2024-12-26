from datetime import date

import django_filters
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.views.decorators.http import require_http_methods
from extra_settings.models import Setting
from openpyxl import Workbook

from rh.models import Cluster

from ..forms import (
    ProfileUpdateForm,
    UserUpdateForm,
)
from ..utils import has_permission, write_users_sheet


class UsersFilter(django_filters.FilterSet):
    clusters = django_filters.ModelMultipleChoiceFilter(
        field_name="profile__clusters",
        label="Clusters",
        queryset=Cluster.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "input-select"}),
    )
    last_login = django_filters.DateRangeFilter(field_name="last_login")
    date_joined = django_filters.DateRangeFilter(field_name="date_joined")

    class Meta:
        model = User
        # fields = "__all__"
        fields = ["username", "email", "first_name", "last_name", "clusters", "is_active"]


#############################################
############### Members ####################
#############################################


@login_required
@require_http_methods(["GET"])
@permission_required("users.view_org_users", raise_exception=True)
def org_users_list(request):
    user_org = request.user.profile.organization

    users_filter = UsersFilter(
        request.GET,
        request=request,
        queryset=User.objects.filter(profile__organization=user_org)
        .select_related("profile")
        .prefetch_related(Prefetch("profile__clusters", queryset=Cluster.objects.only("title")), "groups")
        .order_by("-last_login"),
    )

    RECORDS_PER_PAGE = Setting.get("RECORDS_PER_PAGE", default=10)
    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    paginator = Paginator(users_filter.qs, per_page=per_page)
    page_number = request.GET.get("page", 1)
    paginated_users = paginator.get_page(page_number)
    paginated_users.adjusted_elided_pages = paginator.get_elided_page_range(page_number)

    users = User.objects.filter(profile__organization=user_org).aggregate(
        users_count=Count("id"),
        active_users_count=Count("id", filter=Q(is_active=True)),
        deactive_users_count=Count("id", filter=Q(is_active=False)),
    )

    context = {
        "users": paginated_users,
        "users_filter": users_filter,
        "users_count": users["users_count"],
        "active_users_count": users["active_users_count"],
        "deactive_users_count": users["deactive_users_count"],
    }

    return render(request, "users/users_list.html", context)


@require_http_methods(["PATCH"])
@login_required
@permission_required("rh.activate_deactivate_user", raise_exception=True)
def toggle_status(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    # check if req.user is admin of the user organization
    # OR superadmin
    if not has_permission(user=request.user, user_obj=user):
        raise PermissionDenied

    if user.profile.email_verified_at is None:
        raise PermissionDenied(
            f"{user} has not verified their email. Please ask the user to verifiy their email first."
        )

    if user.is_active:
        user.is_active = False
        user.save()
        messages.success(request, f"{user.username} is deactivated.")
    else:
        user.is_active = True
        user.save()
        messages.success(request, f"{user.username} is activated.")

        # Notify the user
        subject = "Account Status Update"
        message = f"Your account status has been updated. You are now {'active' if user.is_active else 'inactive'}."
        html_message = loader.render_to_string(
            template_name="users/emails/account_status.html",
            context={
                "user": user,
                "subject": subject,
                "domain": f"{request.scheme}://{request.get_host()}",
            },
        )

        user.email_user(
            subject,
            message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            html_message=html_message,
        )

    if request.headers.get("Hx-Trigger", "") == "in-detail-page":
        return HttpResponse(200)

    return render(request, "users/partials/user_tr.html", context={"user": user})


@login_required
@require_http_methods(["POST"])
@permission_required("rh.activate_deactivate_user", raise_exception=True)
def toggle_org_admin_status(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    admin_user = request.user

    # authorize the request.user
    # only users of the same organization
    if target_user.profile.organization != admin_user.profile.organization:
        messages.error(request, "You do not have permission")
        return PermissionDenied

    org_lead_group = Group.objects.get(name="ORG_LEAD")

    if org_lead_group in target_user.groups.all():
        target_user.groups.remove(org_lead_group)
        messages.warning(request, f"`{target_user.username}` admin access has been removed.")
    else:
        target_user.groups.add(org_lead_group)
        messages.success(request, f"`{target_user.username}` is organization admin now.")

    if request.headers.get("Hx-Trigger", "") == "in-detail-page":
        return HttpResponse(200)

    return render(request, "users/partials/user_tr.html", context={"user": target_user})


#############################################
############### Profile Views #################
#############################################


@login_required
@permission_required("users.change_profile", raise_exception=True)
def profile(request):
    template = loader.get_template("users/profile.html")
    user = request.user

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(request.POST, instance=user.profile)

        country = None
        organization = None
        if user.profile:
            if user.profile.country:
                country = user.profile.country
            if user.profile.organization:
                organization = user.profile.organization

        if u_form.is_valid() and p_form.is_valid():
            user = u_form.save()
            user_profile = p_form.save(commit=False)
            user_profile.country = country
            user_profile.organization = organization

            user_profile.save()
            p_form.save_m2m()
            messages.success(request, "Profile Updated successfully")
            return redirect("profile")

        else:
            for error in list(u_form.errors.values()):
                messages.error(request, error)
            for error in list(p_form.errors.values()):
                messages.error(request, error)
    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=user.profile)

    context = {
        "user": user,
        "u_form": u_form,
        "p_form": p_form,
    }
    return HttpResponse(template.render(context, request))


@login_required
@permission_required("users.change_profile", raise_exception=True)
def profile_show(request, username):
    user = get_object_or_404(
        User.objects.select_related("profile").prefetch_related(
            Prefetch("profile__clusters", queryset=Cluster.objects.only("title")),
        ),
        username=username,
    )
    if not has_permission(user=request.user, user_obj=user):
        raise PermissionDenied

    context = {"profile_user": user}

    return render(request, "users/profile_show.html", context)


# Export Organization Users
@login_required
@require_http_methods(["GET"])
@permission_required("users.view_org_users", raise_exception=True)
def export_organization_users(request):
    # filter_list = json.loads(request.body)
    user_org = request.user.profile.organization
    try:
        # get the filtered queryset
        users_list = User.objects.filter(profile__organization=user_org).select_related("profile").order_by("-id")
        if request.GET:
            users_filter = UsersFilter(
                request.GET,
                queryset=users_list,
            )
            if users_filter.qs.exists():
                users_list = users_filter.qs

        # define the excel workbook
        workbook = Workbook()
        write_users_sheet(workbook, users_list)

        # get today date
        today = date.today()
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename="{user_org}_users_{today}.xlsx"'

        # Save the workbook to the response
        workbook.save(response)

        return response
    except Exception as e:
        response = {"error": str(e)}
        return HttpResponse(response, status=500)
