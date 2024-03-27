import datetime

import django_filters
from django_filters.widgets import RangeWidget

from .models import ProjectMonthlyReport


class ReportFilterForm(django_filters.FilterSet):
    """Monthly Report Filter Form"""

    # Define the DateFromToRangeFilter with initial value of current month
    current_month = datetime.date.today().replace(day=1)
    report_date = django_filters.DateFromToRangeFilter(widget=RangeWidget(attrs={"type": "date"}))

    class Meta:
        model = ProjectMonthlyReport
        fields = {
            "project__clusters": ["exact"],  # Exact match for clusters
            "project__implementing_partners": ["exact"],  # Exact match for implementing partners
            "report_date": ["gte", "lte"],  # Date range
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.form.fields["project__clusters"].widget.attrs.update({"class": "custom-select"})
        self.form.fields["project__implementing_partners"].widget.attrs.update({"class": "custom-select"})
