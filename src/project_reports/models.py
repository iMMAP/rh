from django.db import models

from rh.models import ActivityPlan, Disaggregation, Indicator, Location, LocationType, Project

# ##############################################
# ############# Project Reporting ##############
# ##############################################


class ProjectMonthlyReport(models.Model):
    """Project Monthly Reporting"""

    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    REPORT_STATES = [
        ("todo", "Todo"),
        ("pending", "Pending"),
        ("submit", "Submitted"),
        ("reject", "Rejected"),
        ("complete", "Completed"),
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

    def __str__(self):
        name = "Monthly Report"
        if self.report_date:
            name = f"{self.report_date.strftime('%B')}, {self.report_date.year} Report"
        return name

    class Meta:
        verbose_name = "Monthly Report"
        verbose_name_plural = "Monthly Reports"


class ActivityPlanReport(models.Model):
    """Activity Plans model"""

    monthly_report = models.ForeignKey(ProjectMonthlyReport, on_delete=models.CASCADE, null=True, blank=True)
    activity_plan = models.ForeignKey(ActivityPlan, on_delete=models.CASCADE, null=True, blank=True)
    indicator = models.ForeignKey(Indicator, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Activity Plan Report"
        verbose_name_plural = "Activity Plan Reports"


class TargetLocationReport(models.Model):
    """Target Locations model"""

    activity_plan_report = models.ForeignKey(ActivityPlanReport, on_delete=models.CASCADE, null=True, blank=True)

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

    def __str__(self):
        return f"{self.activity_plan_report}, {self.province}, {self.district}"

    class Meta:
        verbose_name = "Target Location Report"
        verbose_name_plural = "Target Location Reports"


class DisaggregationLocationReport(models.Model):
    active = models.BooleanField(default=True)
    target_location_report = models.ForeignKey(TargetLocationReport, on_delete=models.CASCADE, null=True, blank=True)
    disaggregation = models.ForeignKey(Disaggregation, on_delete=models.CASCADE, null=True, blank=True)

    target = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return f"{self.disaggregation.name}"

    class Meta:
        verbose_name = "Disaggregation Location Report"
        verbose_name_plural = "Disaggregation Location Reports"
