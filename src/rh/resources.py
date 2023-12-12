from import_export import resources, fields
from django.contrib.auth.models import User
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from .models import (
    ActivityDomain,
    Cluster,
    Currency,
    Donor,
    Organization,
    Project,
)


class ProjectResource(resources.ModelResource):
    class Meta:
        model = Project
        fields = (
            "title",
            "state",
            "active",
            "code",
            "is_hrp_project",
            "has_hrp_code",
            "hrp_code",
            "budget",
            "budget_recieved",
            "budget_gap",
            "budget_currency",
            "description",
            "start_date",
            "end_date",
        )

    user = fields.Field(column_name="user", attribute="user", widget=ForeignKeyWidget(User, field="username"))
    currency = fields.Field(
        column_name="budget_currency", attribute="budget_currency", widget=ForeignKeyWidget(Currency, field="name")
    )
    cluster = fields.Field(
        column_name="clusters", attribute="clusters", widget=ManyToManyWidget(Cluster, field="title", separator=",")
    )
    activitydomain = fields.Field(
        column_name="activity_domains",
        attribute="activity_domains",
        widget=ManyToManyWidget(ActivityDomain, field="name", separator=","),
    )
    donor = fields.Field(
        column_name="donors", attribute="donors", widget=ManyToManyWidget(Donor, field="code", separator=",")
    )
    organization = fields.Field(
        column_name="implementing_partners",
        attribute="implementing_partners",
        widget=ManyToManyWidget(Organization, field="code", separator=","),
    )
    organization = fields.Field(
        column_name="programme_partners",
        attribute="programme_partners",
        widget=ManyToManyWidget(Organization, field="code", separator=","),
    )

    def dehydrate_is_hrp_project(self, obj):
        if obj.is_hrp_project:
            return "yes"
        else:
            return "no"

    def dehydrate_has_hrp_code(self, obj):
        if obj.has_hrp_code:
            return "yes"
        else:
            return "no"

        # export_order = ("ORDERING THE FIELDS")

    def dehydrate_state(self, obj):
        if obj.state:
            return "active"
        else:
            return "not active"

    def dehydrate_active(self, obj):
        if obj.active:
            return "yes"
        else:
            return "no"
