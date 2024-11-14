from django import forms
from rh.models import Location, Project

from .models import StockItemsType, StockMonthlyReport, StockReport, Warehouse


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ("province", "district", "name")
        labels = {
            "name": "Warehouse Name",
        }
        # exclude = ['id']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["province"].required = True
        self.fields["province"].queryset = self.fields["province"].queryset.filter(level=1, parent=user.profile.country)

        self.fields["district"].queryset = Location.objects.filter(level=2)
        self.fields["district"].required = True


class StockReportForm(forms.ModelForm):
    class Meta:
        model = StockReport
        fields = "__all__"
        exclude = ["monthly_report"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["project"].queryset = Project.objects.filter(user=user)
        self.fields["cluster"].required = True
        self.fields["cluster"].queryset = self.fields["cluster"].queryset.all()

        self.fields["stock_item_type"].queryset = StockItemsType.objects.all()
        self.fields["stock_item_type"].required = True


class StockMonthlyReportForm(forms.ModelForm):
    class Meta:
        model = StockMonthlyReport
        fields = ["from_date", "due_date", "note"]

        widgets = {
            "from_date": forms.widgets.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "due_date": forms.widgets.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
