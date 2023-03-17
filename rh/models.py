from django.db import models

NAME_MAX_LENGTH = 300
DESCRIPTION_MAX_LENGTH = 600


class Location(models.Model):
    """Locations Model"""

    LOCATION_TYPES = [
        ('All', 'ALL'),
        ('Country', 'Country'),
        ('Province', 'Province'),
        ('District', 'District'),
    ]
    parent = models.ForeignKey("self", default=0, on_delete=models.CASCADE, blank=True, null=True)
    level = models.IntegerField(default=0)
    code = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    original_name = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(
        max_length=15,
        choices=LOCATION_TYPES,
        default='Country', null=True, blank=True
    )
    lat = models.FloatField(blank=True, null=True)
    long = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.name

# class Location(models.Model):
#     """Locations Model"""

#     LOCATION_TYPES = [
#         ('Country', 'Country'),
#         ('Province', 'Province'),
#         ('District', 'District'),
#     ]
#     admin0_pcode = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
#     admin0_na_en = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
#     admin0_translation = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

#     admin1_pcode = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
#     admin1_na_en = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
#     admin1_translation = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

#     admin2_pcode = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
#     admin2_na_en = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
#     admin2_translation = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

#     admin2_lat = models.FloatField(blank=True, null=True)
#     admin2_long = models.FloatField(blank=True, null=True)

#     admin3_pcode = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
#     admin3_na_en = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
#     admin3_translation = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

#     admin4_pcode = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
#     admin4_na_en = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
#     admin4_translation = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    
#     type = models.CharField(
#         max_length=15,
#         choices=LOCATION_TYPES,
#         default='Country', null=True, blank=True
#     )

#     def __str__(self):
#         name = self.admin0_na_en
#         if self.admin4_na_en:
#             name = self.admin4_na_en
#         elif self.admin3_na_en:
#             name = self.admin3_na_en
#         elif self.admin2_na_en:
#             name = self.admin2_na_en
#         elif self.admin1_na_en:
#             name = self.admin1_na_en

#         return name
    

class Cluster(models.Model):
    """Clusters Model"""

    old_code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    old_title = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    title = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    ocha_code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.title


class BeneficiaryType(models.Model):
    """Beneficiary Types Model"""
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    location = models.ForeignKey(Location, blank=True, null=True, on_delete=models.SET_NULL,)
    description = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    old_id =  models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Beneficiary Type'
        verbose_name_plural = "Beneficiary Types"


class Organization(models.Model):
    """Organizations Model"""
    location = models.ForeignKey(Location, blank=True, null=True, on_delete=models.SET_NULL,)
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    type = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    old_id =  models.CharField("Old ID", max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name


class Donor(models.Model):
    code =  models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name =  models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    location = models.ForeignKey(Location, blank=True, null=True, on_delete=models.SET_NULL,)
    cluster = models.ForeignKey(Cluster, blank=True, null=True, on_delete=models.SET_NULL,)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    old_id =  models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Donor'
        verbose_name_plural = "Donors"


class StrategicObjective(models.Model):
    """Objectives"""
    strategic_objective_name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    strategic_objective_description = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)
    output_objective_name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    sector_objective_name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    sector_objective_description = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)
    denominator = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Objective'
        verbose_name_plural = "Objectives"


class Indicator(models.Model):
    """Indicators"""
    code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    numerator = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    denominator = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    description = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Indicator'
        verbose_name_plural = "Indicators"


class Currency(models.Model):
    """Currencies model"""
    name = models.CharField(max_length=15, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = "Currencies"


class Activity(models.Model):
    """Activities model"""
    active = models.BooleanField(default=True)
    activity_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    hrp_code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    code_indicator = models.BooleanField(default=False, blank=True, null=True)
    code = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)
    subdomain_code = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)
    subdomain_name = models.CharField(max_length=DESCRIPTION_MAX_LENGTH, blank=True, null=True)
    locations = models.ManyToManyField(Location)
    clusters = models.ManyToManyField(Cluster)
    indicator = models.ForeignKey(Indicator, on_delete=models.SET_NULL, blank=True, null=True)
    objective_id = models.ForeignKey(StrategicObjective, on_delete=models.SET_NULL, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    end_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    fields = models.JSONField(blank=True, null=True, default=dict)
    old_id =  models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)
    ocha_code = models.CharField(max_length=NAME_MAX_LENGTH, blank=True, null=True)

    def __str__(self):
        return f"[{self.name}]- {self.subdomain_name}"
    
    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = "Activities"
    

class Project(models.Model):
    """Projects model"""
    user = models.ForeignKey('accounts.Account', on_delete=models.SET_NULL, null=True, blank=True)
    code = models.CharField(max_length=NAME_MAX_LENGTH, null=True, blank=True)
    title = models.CharField(max_length=NAME_MAX_LENGTH)
    description = models.TextField(blank=True, null=True)
    clusters = models.ManyToManyField(Cluster)
    activities = models.ManyToManyField(Activity)
    locations = models.ManyToManyField(Location)
    start_date = models.DateTimeField('start date')
    end_date = models.DateTimeField('end date')
    budget = models.IntegerField(null=True, blank=True)
    budget_currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class ActivityPlan(models.Model):
    """Activity Plans model"""
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True, blank=True)
    boys = models.IntegerField(blank=True, null=True)
    girls = models.IntegerField(blank=True, null=True)
    men = models.IntegerField(blank=True, null=True)
    women = models.IntegerField(blank=True, null=True)
    elderly_men = models.IntegerField(blank=True, null=True)
    elderly_women = models.IntegerField(blank=True, null=True)
    households = models.IntegerField(blank=True, null=True)
    activity_fields = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.project.title}, {self.activity.title}"

    class Meta:
        verbose_name = 'Activity Plan'
        verbose_name_plural = "Activity Plans"


class Report(models.Model):
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    activity_plan = models.ForeignKey(ActivityPlan, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    boys = models.IntegerField(blank=True, null=True)
    girls = models.IntegerField(blank=True, null=True)
    men = models.IntegerField(blank=True, null=True)
    women = models.IntegerField(blank=True, null=True)
    elderly_men = models.IntegerField(blank=True, null=True)
    elderly_women = models.IntegerField(blank=True, null=True)
    households = models.IntegerField(blank=True, null=True)
    notes =  models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
