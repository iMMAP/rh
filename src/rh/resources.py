from import_export import resources, fields
from django.contrib.auth.models import User
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from .models import (
    Cluster,
    Currency,
    Donor,
    Organization,
    Project,
)


class ProjectResource(resources.ModelResource):
    activity_type = fields.Field()
    activity_domain = fields.Field()
    indicator = fields.Field()
    beneficiary = fields.Field()
    beneficiary_category = fields.Field()

    province = fields.Field()
    district = fields.Field()
    location_type = fields.Field()
    site_name = fields.Field()
    site_lat = fields.Field()
    site_long = fields.Field()

    class Meta:
        model = Project

        use_transactions = True
        fields = (
            "title",
            "state",
            "is_active",
            "code",
            "is_hrp_project",
            "has_hrp_code",
            "hrp_code",
            "budget",
            "budget_currency",
            "budget_received",
            "budget_gap",
            "description",
            "start_date",
            "end_date",
            "activity_domain",
            "activity_type",
            "indicator",
            "beneficiary",
            "beneficiary_category",
            "province",
            "district",
            "location_type",
            "site_name",
            "site_lat",
            "site_long",
        )
        export_order = (
            "user",
            "title",
            "state",
            "is_active",
            "code",
            "is_hrp_project",
            "has_hrp_code",
            "hrp_code",
            "budget",
            "budget_currency",
            "budget_received",
            "budget_gap",
            "description",
            "start_date",
            "end_date",
            "activity_domain",
            "activity_type",
            "indicator",
            "beneficiary",
            "beneficiary_category",
            "province",
            "district",
            "location_type",
            "site_name",
            "site_lat",
            "site_long",
        )

    user = fields.Field(column_name="user", attribute="user", widget=ForeignKeyWidget(User, field="username"))
    currency = fields.Field(
        column_name="budget_currency", attribute="budget_currency", widget=ForeignKeyWidget(Currency, field="name")
    )
    currency = fields.Field(
        column_name="budget_currency", attribute="budget_currency", widget=ForeignKeyWidget(Currency, field="name")
    )
    currency = fields.Field(
        column_name="budget_currency", attribute="budget_currency", widget=ForeignKeyWidget(Currency, field="name")
    )
    cluster = fields.Field(
        column_name="clusters", attribute="clusters", widget=ManyToManyWidget(Cluster, field="title", separator=",")
    )

    # activity planning start
    def dehydrate_activity_domain(self, project):
        activity_domain = list(project.activityplan_set.all())
        return ",".join([child.activity_domain.name for child in activity_domain])

    def dehydrate_activity_type(self, project):
        activity_types = list(project.activityplan_set.all())
        return ",".join([child.activity_type.name for child in activity_types])

    def dehydrate_beneficiary(self, project):
        activity_plan = list(project.activityplan_set.all())
        return ",".join([child.beneficiary for child in activity_plan if child.beneficiary])

    def dehydrate_beneficiary_category(self, project):
        activity_plan = project.activityplan_set.all()
        return ",".join([plan.beneficiary_category for plan in activity_plan])

    def dehydrate_hrp_beneficiary(self, project):
        activity_plan = list(project.activityplan_set.all())
        return ",".join([child.hrp_beneficiary for child in activity_plan])

    # activity planning ends
    # target loacation starts
    def dehydrate_province(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.province.name for location in target_location])

    def dehydrate_district(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.district.name for location in target_location])

    def dehydrate_location_type(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.location_type for location in target_location if location.location_type])

    def dehydrate_site_name(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.site_name for location in target_location if location.site_name])

    def dehydrate_site_lat(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.site_lat for location in target_location if location.site_lat])

    def dehydrate_site_long(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.site_long for location in target_location if location.site_long])

    # target location ends
    donor = fields.Field(
        column_name="donors", attribute="donors", widget=ManyToManyWidget(Donor, field="code", separator=",")
    )

    organ = fields.Field(
        column_name="programme_partners",
        attribute="programme_partners",
        widget=ManyToManyWidget(Organization, field="code", separator=","),
    )
    organization = fields.Field(
        column_name="implementing_partners",
        attribute="implementing_partners",
        widget=ManyToManyWidget(Organization, field="code", separator=","),
    )

    def dehydrate_start_date(self, obj):
        return obj.start_date.strftime("%d-%m-%Y %H:%M:%S")

    def dehydrate_end_date(self, obj):
        return obj.end_date.strftime("%d-%m-%Y %H:%M:%S")

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

    def dehydrate_state(self, obj):
        if obj.state:
            return "active"
        else:
            return "not active"

    def dehydrate_active(self, obj):
        if obj.is_active:
            return "yes"
        else:
            return "no"
