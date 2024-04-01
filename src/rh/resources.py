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
    organization = fields.Field()
    organization_type = fields.Field()
    admin1pcode = fields.Field()
    admin1name = fields.Field()
    admin2pcode = fields.Field()
    admin2name = fields.Field()
    location_type = fields.Field()
    classification = fields.Field()
    facility_site_type = fields.Field()
    facility_monitoring = fields.Field()
    facility_id = fields.Field()
    region = fields.Field()
    facility_name = fields.Field()
    facility_lat = fields.Field()
    facility_long = fields.Field()
    description = fields.Field()

    class Meta:
        model = Project

        use_transactions = True
        fields = (
            "title",
            "state",
            "active",
            "code",
            "is_hrp_project",
            "has_hrp_code",
            "hrp_code",
            "organization",
            "organization_type",
            "budget",
            "budget_currency",
            "budget_received",
            "budget_gap",
            "start_date",
            "end_date",
            "clusters",
            "donors",
            "implementing_partners",
            "programme_partners",
            "activity_domain",
            "activity_type",
            "indicator",
            "beneficiary",
            "beneficiary_category",
            "admin1pcode",
            "admin1name",
            "region",
            "admin2pcode",
            "admin2name",
            "location_type",
            "classification",
            "facility_site_type",
            "facility_monitoring",
            "facility_id",
            "facility_name",
            "facility_lat",
            "facility_long",
            "description",
        )
        export_order = (
            "user",
            "title",
            "state",
            "active",
            "code",
            "is_hrp_project",
            "has_hrp_code",
            "hrp_code",
            "organization",
            "organization_type",
            "budget",
            "budget_currency",
            "budget_received",
            "budget_gap",
            "start_date",
            "end_date",
            "clusters",
            "donors",
            "implementing_partners",
            "programme_partners",
            "activity_domain",
            "activity_type",
            "indicator",
            "beneficiary",
            "beneficiary_category",
            "admin1pcode",
            "admin1name",
            "region",
            "admin2pcode",
            "admin2name",
            "location_type",
            "classification",
            "facility_site_type",
            "facility_monitoring",
            "facility_id",
            "facility_name",
            "facility_lat",
            "facility_long",
            "description",
        )

    user = fields.Field(column_name="user", attribute="user", widget=ForeignKeyWidget(User, field="username"))
    budget_currency = fields.Field(
        column_name="budget_currency", attribute="budget_currency", widget=ForeignKeyWidget(Currency, field="name")
    )

    clusters = fields.Field(
        column_name="clusters", attribute="clusters", widget=ManyToManyWidget(Cluster, field="title", separator=",")
    )
    donors = fields.Field(
        column_name="donors", attribute="donors", widget=ManyToManyWidget(Donor, field="name", separator=",")
    )
    implementing_partners = fields.Field(
        column_name="implementing_partners",
        attribute="implementing_partners",
        widget=ManyToManyWidget(Organization, field="code", separator=","),
    )
    programme_partners = fields.Field(
        column_name="programme_partners",
        attribute="programme_partners",
        widget=ManyToManyWidget(Organization, field="code", separator=","),
    )

    def dehydrate_organization(self, project):
        return project.user.profile.organization.code

    def dehydrate_organization_type(self, project):
        return project.user.profile.organization.type

    # def dehydrate_implementing_partners_type(self, project):
    #     programme_partner_type = list(project.implementing_partners.all())
    #     return ",".join([t.type for t in programme_partner_type])

    # def dehydrate_programme_partners_type(self, project):
    #     programme_partner_type = list(project.programme_partners.all())
    #     return ",".join([t.type for t in programme_partner_type])

    # activity planning start
    def dehydrate_activity_domain(self, project):
        activity_domain = list(project.activityplan_set.all())
        return ",".join([child.activity_domain.name for child in activity_domain])

    def dehydrate_activity_type(self, project):
        activity_types = list(project.activityplan_set.all())
        return ",".join([child.activity_type.name for child in activity_types])

    def dehydrate_indicator(self, project):
        indicators = list(project.activityplan_set.all())
        return ",".join([child.indicator.name for child in indicators])

    def dehydrate_beneficiary(self, project):
        activity_plan = list(project.activityplan_set.all())
        return ",".join([child.beneficiary.name for child in activity_plan if child.beneficiary.name])

    def dehydrate_beneficiary_category(self, project):
        activity_plan = project.activityplan_set.all()
        return ",".join([plan.beneficiary_category for plan in activity_plan])

    def dehydrate_hrp_beneficiary(self, project):
        activity_plan = list(project.activityplan_set.all())
        return ",".join([child.hrp_beneficiary for child in activity_plan])

    def dehydrate_description(self, project):
        descriptions = list(project.activityplan_set.all())
        return ",".join([desc.description for desc in descriptions if desc])

    # activity planning ends
    # target loacation starts
    def dehydrate_admin1name(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.province.name for location in target_location])

    def dehydrate_region(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.province.region_name for location in target_location])

    def dehydrate_admin1pcode(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.province.code for location in target_location])

    def dehydrate_admin2pcode(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.district.code for location in target_location])

    def dehydrate_admin2name(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.district.name for location in target_location])

    def dehydrate_location_type(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.location_type for location in target_location if location.location_type])

    def dehydrate_classification(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.classification for location in target_location if location.classification])

    def dehydrate_facility_site_type(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join(
            [location.facility_site_type.name for location in target_location if location.facility_site_type]
        )

    def dehydrate_facility_monitoring(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join(["Yes" for location in target_location if location.facility_monitoring])

    def dehydrate_facility_name(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.facility_name for location in target_location if location.facility_name])

    def dehydrate_facility_id(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.facility_id for location in target_location if location.facility_id])

    def dehydrate_facility_lat(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.facility_lat for location in target_location if location.facility_lat])

    def dehydrate_facility_long(self, project):
        target_location = list(project.targetlocation_set.all())
        return ",".join([location.facility_long for location in target_location if location.facility_long])

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
        if obj.active:
            return "yes"
        else:
            return "no"
