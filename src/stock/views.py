import datetime
import re
import urllib

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_http_methods

from .forms import StockLocationDetailsForm, StockReportForm, WarehouseLocationForm
from .models import StockLocationDetails, StockReports, WarehouseLocation


@cache_control(no_store=True)
@login_required
def stock_index_view(request):
    """Stock Views"""
    WarehouseLocationFormset = modelformset_factory(WarehouseLocation, form=WarehouseLocationForm)
    if request.method == "POST":
        enurl = urllib.parse.urlencode(request.POST)  # To convert POST into a string
        delete_btn = re.search(r"delete_(.*?)_warehouse", enurl)  # To match for e.g. delete_<num>_warehouse
        if delete_btn:
            warehouse_id = delete_btn.group(1)
            try:
                warehouse_location_id = WarehouseLocation.objects.get(pk=warehouse_id)
            except Exception as _:
                warehouse_location_id = None
            if warehouse_location_id:
                warehouse_location_id.delete()

            formset = WarehouseLocationFormset(request.POST, request.FILES)
            if formset.is_valid():
                formset.save()

        formset = WarehouseLocationFormset(request.POST, queryset=WarehouseLocation.objects.all())
        if formset.is_valid():
            instances = formset.save()
            for instance in instances:
                now = datetime.datetime.now(datetime.timezone.utc)
                due_date = now + relativedelta(day=31)

                stock_report = StockReports.objects.filter(created_at__month=now.month)
                if not stock_report:
                    stock_report = StockReports(due_date=due_date, created_at=now)
                    stock_report.save()
                instance.save()

            return redirect("stocks")
    formset = WarehouseLocationFormset(queryset=WarehouseLocation.objects.all())

    # stock_reports = StockReports.objects.filter(submitted=False)
    # submitted_stock_reports = StockReports.objects.filter(submitted=True)
    context = {
        "warehouse_location_formset": formset,
        # "stock_reports": stock_reports,
        # "submitted_stock_reports": submitted_stock_reports,
    }

    return render(request, "stock/stocks_index.html", context)


@cache_control(no_store=True)
@login_required
def all_stock_report(request):
    stock_reports = StockReports.objects.filter(submitted=False)
    submitted_stock_reports = StockReports.objects.filter(submitted=True)
    context = {
        "stock_reports": stock_reports,
        "submitted_stock_reports": submitted_stock_reports,
    }
    return render(request, "stock/all_stock_report.html", context)


@cache_control(no_store=True)
@login_required
def stock_report_view(request, pk):
    stock_report = StockReports.objects.get(id=pk)
    stock_location_details = stock_report.stock_location_details.all()

    warehouse_locations = WarehouseLocation.objects.all()
    warehouse_location_stocks = {}

    if stock_report.submitted:
        for warehouse in warehouse_locations:
            warehouse_stock_details = stock_location_details.filter(warehouse_location__id=warehouse.id)
            warehouse_location_stocks.update({warehouse: warehouse_stock_details})

        context = {
            "report": stock_report,
            "warehouse_location_stocks": warehouse_location_stocks,
        }
        return render(request, "stock/stock_report_view.html", context)

    form = StockReportForm(instance=stock_report)

    # Warehouse based stock details formset
    for warehouse in warehouse_locations:
        StockLocationDetailsFormSet = modelformset_factory(
            StockLocationDetails,
            exclude=["warehouse_location"],
            form=StockLocationDetailsForm,
            extra=1,
        )
        warehouse_stock_details = stock_location_details.filter(warehouse_location__id=warehouse.id)

        formset = StockLocationDetailsFormSet(
            queryset=warehouse_stock_details, prefix=f"warehouse-{warehouse.id}-stock"
        )
        warehouse_location_stocks.update({warehouse: formset})

        if request.method == "POST":
            enurl = urllib.parse.urlencode(request.POST)  # To convert POST into a string
            delete_btn = re.search(r"delete_(.*?)_stock_detail", enurl)  # To match for e.g. delete_<num>_warehouse
            if delete_btn:
                stock_detail_id = delete_btn.group(1)
                try:
                    stock_location_id = StockLocationDetails.objects.get(pk=stock_detail_id)
                except Exception as _:
                    stock_location_id = None

                if stock_location_id:
                    stock_location_id.delete()
                    return redirect("stock_report", pk=pk)

            formset = StockLocationDetailsFormSet(
                request.POST,
                queryset=warehouse_stock_details,
                prefix=f"warehouse-{warehouse.id}-stock",
            )
            if formset.is_valid():
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.warehouse_location = warehouse
                    instance.save()
                    stock_report.stock_location_details.add(instance)
            else:
                for form in formset:
                    for error in form.errors:
                        error_message = f"Something went wrong {form.errors}"
                        if form.errors[error]:
                            error_message = f"{error}: {form.errors[error][0]}"
                        messages.error(request, error_message)

    if request.method == "POST":
        enurl = urllib.parse.urlencode(request.POST)  # To convert POST into a string
        report_save = re.search(r"report_form_save", enurl)
        if report_save:
            form = StockReportForm(request.POST, instance=stock_report)
            if form.is_valid():
                form.save()

    context = {
        "report_form": form,
        "report": stock_report,
        "warehouse_location_stocks": warehouse_location_stocks,
    }

    return render(request, "stock/stock_report_form.html", context)


@cache_control(no_store=True)
@login_required
@require_http_methods(["POST"])
def submit_stock_report_form(request, pk):
    StockReports.objects.filter(id=pk).update(submitted=True, submitted_at=datetime.datetime.now())
    return redirect("all_stock_report")


@cache_control(no_store=True)
@login_required
def update_stock_report(request, pk):
    StockReports.objects.filter(id=pk).update(submitted=False)
    return redirect("stock_report", pk=pk)
