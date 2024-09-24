from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from rh.models import (
    ActivityPlan,
    Cluster,
    Currency,
    Disaggregation,
    GrantType,
    ImplementationModalityType,
    Indicator,
    LocationType,
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
    clusters = models.ManyToManyField(Cluster)

    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


class ProjectMonthlyReport(models.Model):
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    REPORT_STATES = [
        ("todo", "Todo"),
        ("pending", "Pending"),
        ("submited", "Submitted"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
        ("archived", "Archived"),
    ]
    state = models.CharField(max_length=15, choices=REPORT_STATES, default="todo", null=True, blank=True)

    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    submitted_on = models.DateTimeField(blank=True, null=True)
    approved_on = models.DateTimeField(blank=True, null=True)
    rejected_on = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        name = "Monthly Report"
        if self.from_date:
            name = f"{self.from_date.strftime('%B')}, {self.to_date.year} Report"
        return name

    class Meta:
        verbose_name = "Monthly Report"
        verbose_name_plural = "Monthly Reports"
        permissions = [
            ("view_5w_dashboard", "View 5W dashboard"),
        ]


class ActivityPlanReport(models.Model):
    monthly_report = models.ForeignKey(ProjectMonthlyReport, on_delete=models.CASCADE)
    activity_plan = models.ForeignKey(ActivityPlan, on_delete=models.CASCADE)

    response_types = models.ManyToManyField(ResponseType, blank=True, limit_choices_to={"is_active": True})
    prev_targeted_by = models.ForeignKey(Indicator, null=True, blank=True, on_delete=models.SET_NULL)

    package_type = models.ForeignKey(PackageType, on_delete=models.SET_NULL, null=True, blank=True)
    unit_type = models.ForeignKey(UnitType, on_delete=models.SET_NULL, null=True, blank=True)
    units = models.IntegerField(default=0, null=True, blank=True)
    no_of_transfers = models.IntegerField(
        default=0, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(30)]
    )
    grant_type = models.ForeignKey(GrantType, on_delete=models.SET_NULL, null=True, blank=True)
    transfer_category = models.ForeignKey(TransferCategory, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    transfer_mechanism_type = models.ForeignKey(TransferMechanismType, on_delete=models.SET_NULL, null=True, blank=True)
    implement_modility_type = models.ForeignKey(
        ImplementationModalityType, on_delete=models.SET_NULL, null=True, blank=True
    )

    seasonal_retargeting = models.BooleanField(blank=True, null=True)

    beneficiary_status = models.CharField(
        max_length=25,
        choices=[
            ("new_beneficiary", "New Beneficiary"),
            ("existing_beneficiaries", "Existing Beneficiaries"),
        ],
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"Activity Plan: {self.activity_plan.activity_domain} - {self.activity_plan.indicator}"

    class Meta:
        verbose_name = "Activity Plan Report"
        verbose_name_plural = "Activity Plan Reports"


class TargetLocationReport(models.Model):
    activity_plan_report = models.ForeignKey(ActivityPlanReport, on_delete=models.CASCADE)
    target_location = models.ForeignKey(TargetLocation, on_delete=models.CASCADE)
    location_type = models.ForeignKey(LocationType, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"Location Report: {self.id}"

    class Meta:
        verbose_name = "Target Location Report"
        verbose_name_plural = "Target Location Reports"


class DisaggregationLocationReport(models.Model):
    target_location_report = models.ForeignKey(TargetLocationReport, on_delete=models.CASCADE, null=True, blank=True)
    disaggregation = models.ForeignKey(Disaggregation, on_delete=models.CASCADE, null=True, blank=True)

    reached = models.IntegerField(default=0, null=True, blank=True, verbose_name="Target Reached")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.disaggregation.name}"

    class Meta:
        verbose_name = "Disaggregation Location Report"
        verbose_name_plural = "Disaggregation Location Reports"
