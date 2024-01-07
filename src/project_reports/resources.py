# from django.contrib.auth.models import User
from import_export import fields, resources
from rh.models import ActivityDetail, ActivityDomain, ActivityType, Indicator

# from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
# from rh.models import (
#     Project,
# )
from .models import ActivityPlanReport, DisaggregationLocationReport, TargetLocationReport


class ActivityPlanReportResource(resources.ModelResource):
    class Meta:
        model = ActivityPlanReport
        use_transactions = True
        fields = (
            "id",
            "activity_plan_name",
            "indicator_name",
            "report_types",
            "target_achieved",
        )

    # Define custom fields for related models
    activity_plan_name = fields.Field(column_name="activity_plan__title", attribute="activity_plan__title")
    indicator_name = fields.Field(column_name="indicator__name", attribute="indicator__name")

    def dehydrate_activity_plan_name(self, activity_plan_report):
        return activity_plan_report.activity_plan.title if activity_plan_report.activity_plan else None

    def dehydrate_indicator_name(self, activity_plan_report):
        return activity_plan_report.indicator.name if activity_plan_report.indicator else None

    def before_import_row(self, row, **kwargs):
        # Convert the 'parent__name' column in the import file to the corresponding ParentModel instance
        activity_domain = row.get("activity_domain")
        activity_type = row.get("activity_type")
        activity_detail = row.get("activity_detail")
        indicator = row.get("indicator")

        # activity_domain_id = None
        # activity_type_id = None
        # activity_detail_id = None
        if activity_domain:
            activity_domain_ids = ActivityDomain.objects.filter(name=activity_domain)
            if activity_domain_ids:
                ...
                # activity_domain_id = activity_domain_ids[0]

        if activity_type:
            activity_type_ids = ActivityType.objects.filter(name=activity_type)
            if activity_type_ids:
                ...
                # activity_type_id = activity_type_ids[0]

        if activity_detail:
            activity_detail_ids = ActivityDetail.objects.filter(name=activity_detail)
            if activity_detail_ids:
                ...
                # activity_detail_id = activity_detail_ids[0]

        if indicator:
            indicator_id = Indicator.objects.filter(name=indicator)
            if indicator_id:
                row["indicator"] = indicator_id
        else:
            row["indicator"] = None


class TargetLocationReportResource(resources.ModelResource):
    class Meta:
        model = TargetLocationReport
        use_transactions = True
        fields = (
            "id",
            "country",
            "province",
            "district",
            "zone",
            "location_type",
        )


class DisaggregationLocationReportResource(resources.ModelResource):
    class Meta:
        model = DisaggregationLocationReport
        use_transactions = True
        fields = (
            "id",
            "disaggregation",
            "target",
        )
