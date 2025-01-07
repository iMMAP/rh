import django_filters
from django import forms

from rh.models import Cluster, Location
from stock.models import StockItemsType, StockMonthlyReport, StockReport, StockUnit, Warehouse


class StockFilter(django_filters.FilterSet):
    province = django_filters.ModelMultipleChoiceFilter(
        queryset=Location.objects.filter(level=1),
        widget=forms.SelectMultiple(attrs={"class": "custom-select"}),
    )
    # Filter by district
    district = django_filters.ModelChoiceFilter(
        queryset=Location.objects.filter(level=2),
        label="District",
        widget=forms.SelectMultiple(attrs={"class": "custom-select"}),
    )
    name = django_filters.CharFilter(lookup_expr="icontains", label="Name")

    class Meta:
        model = Warehouse
        fields = ["province", "district", "name"]


class StockReportFilter(django_filters.FilterSet):
    cluster = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "custom-select"}),
    )
    stock_item_type = django_filters.ModelMultipleChoiceFilter(
        queryset=StockItemsType.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "custom-select"}),
    )
    stock_unit = django_filters.ModelMultipleChoiceFilter(
        queryset=StockUnit.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "custom-select"}),
    )

    class Meta:
        model = StockReport
        fields = ["cluster", "stock_item_type", "stock_unit", "stock_purpose", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StockMonthlyReportFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(
        widget=forms.DateInput(
            attrs={
                "type": "date",
            }
        )
    )
    due_date = django_filters.DateFilter(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = StockMonthlyReport
        fields = ["from_date", "due_date", "state"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class StockDashboardFilter(django_filters.FilterSet):
    from_date = django_filters.DateFilter(
        field_name="stockmonthlyreport__from_date",
        label="From Date",
        lookup_expr="exact",
        widget=forms.DateInput(
            attrs={
                "type": "date",
            }
        ),
    )
    due_date = django_filters.DateFilter(
        field_name="stockmonthlyreport__due_date",
        label="To Date",
        lookup_expr="exact",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    name = django_filters.ModelChoiceFilter(
        lookup_expr="icontains", queryset=Warehouse.objects.all(), label="Warehouse Name"
    )
    status = django_filters.ChoiceFilter(
        field_name="stockmonthlyreport__stockreport__status",
        choices=StockReport.STATUS_TYPES,
        label="Stock Status",
    )
    cluster = django_filters.ModelMultipleChoiceFilter(
        field_name="stockmonthlyreport__stockreport__cluster",
        queryset=Cluster.objects.all(),
        lookup_expr="exact",
        label="Clusters / Sectors",
        widget=forms.SelectMultiple(attrs={"class": "custom-select"}),
    )

    class Meta:
        mode = Warehouse
        fields = ["from_date", "due_date", "name", "status", "cluster"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
