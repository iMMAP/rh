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
    # disaggregation section
    total_household = fields.Field(column_name="Total households")
    female_headed = fields.Field(column_name="Female-headed households")

    women65 = fields.Field(column_name="Elderly women (65+)")
    men65 = fields.Field(column_name="Elderly men (65+)")
    women1864 = fields.Field(column_name="Women (18-64)")
    men1864 = fields.Field(column_name="Men (18-64)")
    girls18 = fields.Field(column_name="Girls (U18)")
    boys18 = fields.Field(column_name="Boys (U18)")
    women60 = fields.Field(column_name="Elderly women (60+)")
    men60 = fields.Field(column_name="Elderly men (60+)")
    women1860 = fields.Field(column_name="Women(18-60)")
    men1860 = fields.Field(column_name="Men(18-60)")
    girls617 = fields.Field(column_name="Girls(6-17)")
    boys617 = fields.Field(column_name="Boys(6-17)")
    girls05 = fields.Field(column_name="Girls(0-5)")
    boys05 = fields.Field(column_name="Boys(0-5)")

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

    try:
        user = fields.Field(column_name="user", attribute="user", widget=ForeignKeyWidget(User, field="username"))
    except Exception:
        user = None
    try:
        budget_currency = fields.Field(
            column_name="budget_currency", attribute="budget_currency", widget=ForeignKeyWidget(Currency, field="name")
        )
    except Exception:
        budget_currency = None

    try:
        clusters = fields.Field(
            column_name="clusters", attribute="clusters", widget=ManyToManyWidget(Cluster, field="title", separator=",")
        )
    except Exception:
        clusters = None
    try:
        donors = fields.Field(
            column_name="donors", attribute="donors", widget=ManyToManyWidget(Donor, field="name", separator=",")
        )
    except Exception:
        donors = None

    try:
        implementing_partners = fields.Field(
            column_name="implementing_partners",
            attribute="implementing_partners",
            widget=ManyToManyWidget(Organization, field="code", separator=","),
        )
    except Exception:
        implementing_partners = None
    try:
        programme_partners = fields.Field(
            column_name="programme_partners",
            attribute="programme_partners",
            widget=ManyToManyWidget(Organization, field="code", separator=","),
        )
    except Exception:
        programme_partners = None

    def dehydrate_organization(self, project):
        try:
            return project.user.profile.organization.code
        except Exception:
            return None

    def dehydrate_organization_type(self, project):
        try:
            return project.user.profile.organization.type
        except Exception:
            return None

    # activity planning start
    def dehydrate_activity_domain(self, project):
        activity_pans = list(project.activityplan_set.all())
        try:
            return ",".join([ap.activity_domain.name for ap in activity_pans if ap.activity_domain.name])
        except Exception:
            return None

    def dehydrate_activity_type(self, project):
        activity_types = list(project.activityplan_set.all())
        try:
            return ",".join([ap.activity_type.name for ap in activity_types if ap.activity_type.name])
        except Exception:
            return None

    def dehydrate_indicator(self, project):
        activity_plans = list(project.activityplan_set.all())
        try:
            return ",".join([ap.indicator.name for ap in activity_plans if ap.indicator.name])
        except Exception:
            return None

    def dehydrate_beneficiary(self, project):
        activity_plans = list(project.activityplan_set.all())
        try:
            return ",".join([ap.beneficiary.name for ap in activity_plans if ap.beneficiary.name])
        except Exception:
            return None

    def dehydrate_beneficiary_category(self, project):
        activity_plans = project.activityplan_set.all()
        try:
            return ",".join([ap.beneficiary_category for ap in activity_plans if ap.beneficiary_category])
        except Exception:
            return None

    def dehydrate_hrp_beneficiary(self, project):
        activity_plans = list(project.activityplan_set.all())
        try:
            return ",".join([ap.hrp_beneficiary for ap in activity_plans if ap.hrp_beneficiary])
        except Exception:
            return None

    def dehydrate_description(self, project):
        activity_plans = list(project.activityplan_set.all())
        try:
            return ",".join([ap.description for ap in activity_plans if ap.description])
        except Exception:
            return None

    # activity planning ends

    # target loacation starts
    def dehydrate_admin1name(self, project):
        target_location = list(project.targetlocation_set.all())
        try:
            return ",".join([location.province.name for location in target_location])
        except Exception:
            return None

    def dehydrate_region(self, project):
        target_location = list(project.targetlocation_set.all())
        try:
            return ",".join(
                [location.province.region_name for location in target_location if location.province.region_name]
            )
        except Exception:
            return None

    def dehydrate_admin1pcode(self, project):
        target_location = list(project.targetlocation_set.all())
        try:
            return ",".join([location.province.code for location in target_location])
        except Exception:
            return None

    def dehydrate_admin2pcode(self, project):
        target_location = list(project.targetlocation_set.all())
        try:
            return ",".join([location.district.code for location in target_location])
        except Exception:
            return None

    def dehydrate_admin2name(self, project):
        target_location = list(project.targetlocation_set.all())
        try:
            return ",".join([location.district.name for location in target_location])
        except Exception:
            return None

    def dehydrate_location_type(self, project):
        target_location = list(project.targetlocation_set.all())
        try:
            return ",".join([location.location_type for location in target_location if location.location_type])
        except Exception:
            return None

    def dehydrate_classification(self, project):
        target_location = list(project.targetlocation_set.all())
        try:
            return ",".join(
                [location.district.classification for location in target_location if location.district.classification]
            )
        except Exception:
            return None

    def dehydrate_facility_site_type(self, project):
        target_location = list(project.targetlocation_set.all())
        try:
            return ",".join(
                [location.facility_site_type.name for location in target_location if location.facility_site_type]
            )
        except Exception:
            return None

    def dehydrate_facility_monitoring(self, project):
        target_location = list(project.targetlocation_set.all())
        try:
            return ",".join(["Yes" for location in target_location if location.facility_monitoring])
        except Exception:
            return None

    def dehydrate_facility_name(self, project):
        target_location = list(project.targetlocation_set.all())
        try:
            return ",".join([location.facility_name for location in target_location if location.facility_name])
        except Exception:
            return None

    def dehydrate_facility_id(self, project):
        target_location = list(project.targetlocation_set.all())
        try:
            return ",".join([location.facility_id for location in target_location if location.facility_id])
        except Exception:
            return None

    def dehydrate_facility_lat(self, project):
        target_location = list(project.targetlocation_set.all())
        try:
            return ",".join([location.facility_lat for location in target_location if location.facility_lat])
        except Exception:
            return None

    def dehydrate_facility_long(self, project):
        target_location = list(project.targetlocation_set.all())
        try:
            return ",".join([location.facility_long for location in target_location if location.facility_long])
        except Exception:
            return None

    # fetching disaggregain in excel file  start
    def dehydrate_female_headed(self, project):
        target_location = project.targetlocation_set.all()
        female = []
        for tr in target_location:
            for dl in tr.disaggregationlocation_set.all():
                if dl.disaggregation.name == getattr(self.fields["female_headed"], "column_name"):
                    value = str(dl.target)
                    female += (",".join([value]),)
        return ",".join([item for item in female if item])

    def dehydrate_total_household(self, project):
        target_location = project.targetlocation_set.all()
        value_list = []
        for tr in target_location:
            for dl in tr.disaggregationlocation_set.all():
                if dl.disaggregation.name == getattr(self.fields["total_household"], "column_name"):
                    value = str(dl.target)
                    value_list += (",".join([value]),)
        return ",".join([item for item in value_list if item])

    def dehydrate_women65(self, project):
        target_location = project.targetlocation_set.all()
        value_list = []
        for tr in target_location:
            for dl in tr.disaggregationlocation_set.all():
                if dl.disaggregation.name == getattr(self.fields["women65"], "column_name"):
                    value = str(dl.target)
                    value_list += (",".join([value]),)
        return ",".join([item for item in value_list if item])

    def dehydrate_men65(self, project):
        target_location = project.targetlocation_set.all()
        value_list = []
        for tr in target_location:
            for dl in tr.disaggregationlocation_set.all():
                if dl.disaggregation.name == getattr(self.fields["men65"], "column_name"):
                    value = str(dl.target)
                    value_list += (",".join([value]),)
        return ",".join([item for item in value_list if item])

    def dehydrate_women1864(self, project):
        target_location = project.targetlocation_set.all()
        value_list = []
        for tr in target_location:
            for dl in tr.disaggregationlocation_set.all():
                if dl.disaggregation.name == getattr(self.fields["women1864"], "column_name"):
                    value = str(dl.target)
                    value_list += (",".join([value]),)
        return ",".join([item for item in value_list if item])

    def dehydrate_women1860(self, project):
        target_location = project.targetlocation_set.all()
        value_list = []
        for tr in target_location:
            for dl in tr.disaggregationlocation_set.all():
                if dl.disaggregation.name == getattr(self.fields["women1860"], "column_name"):
                    value = str(dl.target)
                    value_list += (",".join([value]),)
        return ",".join([item for item in value_list if item])

    def dehydrate_men1864(self, project):
        target_location = project.targetlocation_set.all()
        value_list = []
        for tr in target_location:
            for dl in tr.disaggregationlocation_set.all():
                if dl.disaggregation.name == getattr(self.fields["men1864"], "column_name"):
                    value = str(dl.target)
                    value_list += (",".join([value]),)
        return ",".join([item for item in value_list if item])

    def dehydrate_men1860(self, project):
        target_location = project.targetlocation_set.all()
        value_list = []
        for tr in target_location:
            for dl in tr.disaggregationlocation_set.all():
                if dl.disaggregation.name == getattr(self.fields["men1860"], "column_name"):
                    value = str(dl.target)
                    value_list += (",".join([value]),)
        return ",".join([item for item in value_list if item])

    def dehydrate_girls18(self, project):
        target_location = project.targetlocation_set.all()
        value_list = []
        for tr in target_location:
            for dl in tr.disaggregationlocation_set.all():
                if dl.disaggregation.name == getattr(self.fields["girls18"], "column_name"):
                    value = str(dl.target)
                    value_list += (",".join([value]),)
        return ",".join([item for item in value_list if item])

    def dehydrate_boys18(self, project):
        target_location = project.targetlocation_set.all()
        value_list = []
        for tr in target_location:
            for dl in tr.disaggregationlocation_set.all():
                if dl.disaggregation.name == getattr(self.fields["boys18"], "column_name"):
                    value = str(dl.target)
                    value_list += (",".join([value]),)
        return ",".join([item for item in value_list if item])

    def dehydrate_women60(self, project):
        target_location = project.targetlocation_set.all()
        value_list = []
        for tr in target_location:
            for dl in tr.disaggregationlocation_set.all():
                if dl.disaggregation.name == getattr(self.fields["women60"], "column_name"):
                    value = str(dl.target)
                    value_list += (",".join([value]),)
        return ",".join([item for item in value_list if item])

    def dehydrate_men60(self, project):
        target_location = project.targetlocation_set.all()
        value_list = []
        for tr in target_location:
            for dl in tr.disaggregationlocation_set.all():
                if dl.disaggregation.name == getattr(self.fields["men60"], "column_name"):
                    value = str(dl.target)
                    value_list += (",".join([value]),)
        return ",".join([item for item in value_list if item])

    def dehydrate_girls617(self, project):
        target_location = project.targetlocation_set.all()
        value_list = []
        for tr in target_location:
            for dl in tr.disaggregationlocation_set.all():
                if dl.disaggregation.name == getattr(self.fields["girls617"], "column_name"):
                    value = str(dl.target)
                    value_list += (",".join([value]),)
        return ",".join([item for item in value_list if item])

    def dehydrate_boys617(self, project):
        target_location = project.targetlocation_set.all()
        value_list = []
        for tr in target_location:
            for dl in tr.disaggregationlocation_set.all():
                if dl.disaggregation.name == getattr(self.fields["boys617"], "column_name"):
                    value = str(dl.target)
                    value_list += (", ".join([value]),)
        return ", ".join([item for item in value_list if item])

    def dehydrate_boys05(self, project):
        target_location = project.targetlocation_set.all()
        value_list = []
        for tr in target_location:
            for dl in tr.disaggregationlocation_set.all():
                if dl.disaggregation.name == getattr(self.fields["boys05"], "column_name"):
                    value = str(dl.target)
                    value_list += (",".join([value]),)
        return ",".join([item for item in value_list if item])

    def dehydrate_girls05(self, project):
        target_location = project.targetlocation_set.all()
        value_list = []
        for tr in target_location:
            for dl in tr.disaggregationlocation_set.all():
                if dl.disaggregation.name == getattr(self.fields["girls05"], "column_name"):
                    value = str(dl.target)
                    value_list += (",".join([value]),)
        return ",".join([item for item in value_list if item])

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
