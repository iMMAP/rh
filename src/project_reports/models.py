from django.db import models

from rh.models import (
    ActivityPlan,
    Currency,
    Disaggregation,
    FacilitySiteType,
    GrantType,
    ImplementationModalityType,
    Indicator,
    Location,
    LocationType,
    Organization,
    PackageType,
    Project,
    TargetLocation,
    TransferCategory,
    TransferMechanismType,
    UnitType,
)

# ##############################################
# ############# Project Reporting ##############
# ##############################################


class ResponseType(models.Model):
    name = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


class ProjectMonthlyReport(models.Model):
    """Project Monthly Reporting"""

    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    REPORT_STATES = [
        ("todo", "Todo"),
        ("pending", "Pending"),
        ("submit", "Submitted"),
        ("reject", "Rejected"),
        ("complete", "Completed"),
        ("archive", "Archived"),
    ]
    state = models.CharField(max_length=15, choices=REPORT_STATES, default="todo", null=True, blank=True)
    active = models.BooleanField(default=True)
    report_period = models.DateField(blank=True, null=True)
    report_date = models.DateField(blank=True, null=True)
    report_due_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    submitted_on = models.DateTimeField(blank=True, null=True)
    approved_on = models.DateTimeField(blank=True, null=True)
    rejected_on = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        name = "Monthly Report"
        if self.report_date:
            name = f"{self.report_date.strftime('%B')}, {self.report_date.year} Report"
        return name

    class Meta:
        verbose_name = "Monthly Report"
        verbose_name_plural = "Monthly Reports"
        permissions = [
            ("view_5w_dashboard", "View 5W dashboard"),
        ]


class ActivityPlanReport(models.Model):
    """Activity Plans model"""

    monthly_report = models.ForeignKey(ProjectMonthlyReport, on_delete=models.CASCADE, null=True, blank=True)
    activity_plan = models.ForeignKey(ActivityPlan, on_delete=models.CASCADE, null=True, blank=True)
    indicator = models.ForeignKey(Indicator, on_delete=models.SET_NULL, null=True)
    implementing_partners = models.ManyToManyField(
        Organization, related_name="reporting_implementing_partners", blank=True
    )

    report_types = models.ManyToManyField(ResponseType, blank=True)
    target_achieved = models.IntegerField(default=0, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    package_type = models.ForeignKey(PackageType, on_delete=models.SET_NULL, null=True, blank=True)
    unit_type = models.ForeignKey(UnitType, on_delete=models.SET_NULL, null=True, blank=True)
    grant_type = models.ForeignKey(GrantType, on_delete=models.SET_NULL, null=True, blank=True)
    transfer_category = models.ForeignKey(TransferCategory, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    transfer_mechanism_type = models.ForeignKey(TransferMechanismType, on_delete=models.SET_NULL, null=True, blank=True)
    implement_modility_type = models.ForeignKey(
        ImplementationModalityType, on_delete=models.SET_NULL, null=True, blank=True
    )

    seasonal_retargeting = models.BooleanField(blank=True, null=True)
    modality_retargeting = models.BooleanField(blank=True, null=True)

    beneficiary_status = models.CharField(
        max_length=15,
        choices=[
            ("new_beneficiary", "New Beneficiary"),
            ("old_beneficiary", "Old Beneficiary"),
        ],
        null=True,
        blank=True,
    )

    @property
    def activity_domain(self):
        return self.activity_plan.activity_domain if self.activity_plan else None

    @property
    def activity_type(self):
        return self.activity_plan.activity_type if self.activity_plan else None

    @property
    def activity_detail(self):
        return self.activity_plan.activity_detail if self.activity_plan else None

    def __str__(self):
        return f"Activity Plan: {self.activity_plan.activity_domain} - {self.indicator}"

    class Meta:
        verbose_name = "Activity Plan Report"
        verbose_name_plural = "Activity Plan Reports"


class TargetLocationReport(models.Model):
    """Target Locations model"""

    activity_plan_report = models.ForeignKey(ActivityPlanReport, on_delete=models.CASCADE, null=True, blank=True)

    target_location = models.ForeignKey(TargetLocation, on_delete=models.CASCADE, null=True, blank=True)

    country = models.ForeignKey(
        Location,
        related_name="target_report_country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    province = models.ForeignKey(
        Location,
        related_name="target_report_province",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    district = models.ForeignKey(
        Location,
        related_name="target_report_district",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    zone = models.ForeignKey(
        Location,
        related_name="target_report_zones",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    location_type = models.ForeignKey(LocationType, on_delete=models.SET_NULL, null=True, blank=True)
    facility_site_type = models.ForeignKey(FacilitySiteType, on_delete=models.SET_NULL, null=True, blank=True)

    # Facility Monitoring
    facility_monitoring = models.BooleanField(default=False)
    facility_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )
    facility_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )
    facility_lat = models.FloatField(null=True, blank=True)
    facility_long = models.FloatField(null=True, blank=True)
    nhs_code = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"Location Report: {self.province}, {self.district}"

    class Meta:
        verbose_name = "Target Location Report"
        verbose_name_plural = "Target Location Reports"


class DisaggregationLocationReport(models.Model):
    active = models.BooleanField(default=True)
    target_location_report = models.ForeignKey(TargetLocationReport, on_delete=models.CASCADE, null=True, blank=True)
    disaggregation = models.ForeignKey(Disaggregation, on_delete=models.CASCADE, null=True, blank=True)

    target_required = models.IntegerField(default=0, null=True, blank=True)
    target = models.IntegerField(default=0, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.disaggregation.name}"

    class Meta:
        verbose_name = "Disaggregation Location Report"
        verbose_name_plural = "Disaggregation Location Reports"
