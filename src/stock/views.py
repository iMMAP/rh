import calendar
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django_htmx.http import HttpResponseClientRedirect
from extra_settings.models import Setting

from stock.filter import StockFilter, StockMonthlyReportFilter, StockReportFilter
from stock.utils import write_csv_columns_and_rows

from .forms import StockMonthlyReportForm, StockReportForm, WarehouseForm
from .models import StockItemsType, StockMonthlyReport, StockReport, Warehouse


def get_cluster_stock_type(request):
    stock_types = StockItemsType.objects.filter(cluster=list(request.GET.values())[0]).select_related("cluster")
    return render(request, "stock/_stock_type_select_options.html", {"stock_types": stock_types})


@login_required
def stock_index_view(request):
    """stock views"""
    user_org = request.user.profile.organization
    warehouse_queryset = (
        Warehouse.objects.filter(organization=user_org)
        .prefetch_related("stockmonthlyreport_set")
        .order_by("-updated_at")
        .annotate(total_beneficiary=Sum("stockmonthlyreport__stockreport__beneficiary_coverage"))
    )
    ap_filter = StockFilter(
        request.GET,
        queryset=warehouse_queryset,
    )
    RECORDS_PER_PAGE = Setting.get("RECORDS_PER_PAGE", default=10)

    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    paginator = Paginator(ap_filter.qs, per_page=per_page)  # Show 10 activity plans per page
    page = request.GET.get("page", 1)
    w_locations = paginator.get_page(page)
    w_locations.adjusted_elided_pages = paginator.get_elided_page_range(page)

    context = {
        "organization": user_org,
        "warehouse_locations": w_locations,
        "stock_filter": ap_filter,
    }
    return render(request, "stock/stocks_index.html", context)


@login_required
def create_warehouse_location(request):
    user_org = request.user.profile.organization
    if request.method == "POST":
        form = WarehouseForm(request.POST, user=request.user)
        if form.is_valid():
            warehoues = form.save(commit=False)
            warehoues.organization = user_org
            warehoues.user = request.user
            warehoues.save()
            messages.success(
                request,
                mark_safe(
                    f"{warehoues} was added successfully.",
                ),
            )
            if "_save" in request.POST:
                return redirect("stocks")
            elif "_addanother" in request.POST:
                return redirect("warehouse-location-create")
        else:
            messages.error(request, "Something went wrong. Please fix the below error.")
    else:
        form = WarehouseForm(user=request.user)
    context = {"organization": user_org, "form": form}
    return render(request, "stock/create_warehouse_location_form.html", context)


@login_required
def update_warehouse_location(request, pk):
    warehouse_location = get_object_or_404(Warehouse, pk=pk)
    user_org = request.user.profile.organization
    if request.method == "POST":
        form = WarehouseForm(request.POST, instance=warehouse_location, user=request.user)
        if form.is_valid():
            location = form.save(commit=False)
            location.organization = user_org
            location.save()
            messages.success(
                request,
                mark_safe(
                    f"{location} was updated successfully.",
                ),
            )
            return redirect("stocks")
        else:
            messages.error(request, "Something went wrong. Please fix the below error.")
    else:
        form = WarehouseForm(instance=warehouse_location, user=request.user)
    context = {"form": form, "warhouse": warehouse_location, "organization": user_org}
    return render(request, "stock/create_warehouse_location_form.html", context)


@login_required
def copy_warehouse_location(request, pk):
    new_warehouse_location = get_object_or_404(Warehouse, pk=pk)
    new_warehouse_location.id = None
    new_warehouse_location.name = f"[Copy]-{new_warehouse_location.name}"
    new_warehouse_location.save()
    messages.success(request, "Warehouse Location copied.")
    return redirect("stocks")


@login_required
def delete_warehouse_location(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    monthly_report = StockMonthlyReport.objects.filter(warehouse_location=warehouse).prefetch_related(
        Prefetch("stockreport_set", queryset=StockReport.objects.all())
    )
    if monthly_report.exists():
        # TODO: handle this better in the frontend
        messages.error(request, "Cannot delete warehouse location with existing reports.")
        return HttpResponse(status=200)
    warehouse.delete()
    messages.success(request, "Warehouse location has been delete.")
    if request.headers.get("Hx-Trigger", "") == "delete-btn":
        url = reverse_lazy("stocks", kwargs={})
        return HttpResponseClientRedirect(url)
    else:
        return HttpResponse(status=200)


@login_required
def stock_report_period_list(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)

    ap_filter = StockMonthlyReportFilter(
        request.GET,
        queryset=StockMonthlyReport.objects.filter(warehouse_location=warehouse).order_by("-updated_at"),
    )
    RECORDS_PER_PAGE = Setting.get("RECORDS_PER_PAGE", default=10)

    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    paginator = Paginator(ap_filter.qs, per_page=per_page)  # Show 10 activity plans per page
    page = request.GET.get("page", 1)
    reports = paginator.get_page(page)
    reports.adjusted_elided_pages = paginator.get_elided_page_range(page)

    context = {
        "stock_reports": reports,
        "warehouse": warehouse,
        "period_filter": ap_filter,
        "report_states": StockMonthlyReport.STOCK_State,
        # "submitted_stock_reports": submitted_stock_reports,
    }
    return render(request, "stock/all_stock_report.html", context)


# Stock monthly Report
@login_required
def stock_details_view(request, pk):
    monthly_reports = get_object_or_404(StockMonthlyReport, pk=pk)
    ap_filter = StockReportFilter(
        request.GET,
        queryset=StockReport.objects.filter(monthly_report=monthly_reports).order_by("-updated_at"),
    )
    RECORDS_PER_PAGE = Setting.get("RECORDS_PER_PAGE", default=10)

    per_page = request.GET.get("per_page", RECORDS_PER_PAGE)
    paginator = Paginator(ap_filter.qs, per_page=per_page)  # Show 10 activity plans per page
    page = request.GET.get("page", 1)
    stock_report_details = paginator.get_page(page)
    stock_report_details.adjusted_elided_pages = paginator.get_elided_page_range(page)
    context = {
        "stock_report": monthly_reports,
        "stock_report_details": stock_report_details,
        "stock_filter": ap_filter,
        "report_states": StockReport.STATUS_TYPES,
    }
    return render(request, "stock/stock_details_view.html", context)


@login_required
def create_stock_report_period(request, warehouse):
    warehouse = get_object_or_404(Warehouse, pk=warehouse)
    # Get the current date
    current_date = datetime.now()

    # Calculate the last day of the current month
    last_day = calendar.monthrange(current_date.year, current_date.month)[1]

    # Create a new date representing the end of the current month
    end_of_month = datetime(current_date.year, current_date.month, last_day)
    form = StockMonthlyReportForm(
        request.POST or None,
        initial={"due_date": end_of_month},
    )
    if request.method == "POST":
        if form.is_valid():
            monthly_report = form.save(commit=False)
            monthly_report.warehouse_location = warehouse
            monthly_report.save()
            return redirect("stock-details-view", pk=monthly_report.id)
        else:
            messages.error(request, "something went wrong. Please fix the below errors.")

    context = {"form": form, "warehouse": warehouse}
    return render(request, "stock/stock_report_period_form.html", context)


@login_required
def update_stock_report_period(request, report):
    monthly_report = get_object_or_404(StockMonthlyReport, pk=report)

    warehouse = monthly_report.warehouse_location
    # Get the current date
    current_date = datetime.now()

    # Calculate the last day of the current month
    last_day = calendar.monthrange(current_date.year, current_date.month)[1]

    # Create a new date representing the end of the current month
    end_of_month = datetime(current_date.year, current_date.month, last_day)
    form = StockMonthlyReportForm(request.POST or None, initial={"due_date": end_of_month}, instance=monthly_report)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, f"{monthly_report} report was updated.")
            return redirect("stock-report-period", pk=monthly_report.warehouse_location.id)
        else:
            messages.error(request, "Something went wrong. Please fix the below errors.")
    print(form.instance)

    context = {"form": form, "warehouse": warehouse, "monthly_report": monthly_report}
    return render(request, "stock/stock_report_period_form.html", context)


@login_required
def delete_stock_report_period(request, pk):
    monthly_report = get_object_or_404(StockMonthlyReport, pk=pk)
    if monthly_report.stockreport_set.exists():
        messages.error(request, "Unable to delete: A report has been submitted for this period")
        return HttpResponse(status=200)
    monthly_report.delete()
    messages.success(request, f"{monthly_report} Report has been deleted.")
    return HttpResponse(status=200)


@login_required
def create_stock_monthly_report(request, pk):
    monthly_report = get_object_or_404(StockMonthlyReport, pk=pk)
    if request.method == "POST":
        form = StockReportForm(request.POST, user=request.user)
        if form.is_valid():
            stock_report = form.save(commit=False)
            stock_report.monthly_report = monthly_report
            stock_report.save()
            monthly_report.state = "draft"
            monthly_report.save()
            messages.success(
                request,
                mark_safe(
                    f"{stock_report} was added successfully.",
                ),
            )
            if "_save" in request.POST:
                return redirect("stock-details-view", pk=monthly_report.id)
            elif "_addanother" in request.POST:
                return redirect("stock-report-create", pk=monthly_report.id)
        else:
            messages.error(request, "something went wrong. Please fix the below errors.")
    else:
        form = StockReportForm(user=request.user)

    context = {"form": form, "monthly_report": monthly_report}
    return render(request, "stock/stock_report_form.html", context)


@login_required
def copy_stock_monthly_report(request, pk):
    new_monthly_report = get_object_or_404(StockReport, pk=pk)
    monthly_report = new_monthly_report.monthly_report
    new_monthly_report.id = None
    new_monthly_report.save()
    messages.success(request, "Monthly report copied.")
    return redirect("stock-details-view", pk=monthly_report.id)


@login_required
def update_stock_monthly_report(request, pk):
    stock_report = get_object_or_404(StockReport, pk=pk)
    monthly_report = stock_report.monthly_report
    if request.method == "POST":
        form = StockReportForm(request.POST, instance=stock_report, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Report has been updated. ")
            return redirect("stock-details-view", pk=monthly_report.id)
        else:
            messages.error(request, "Something went wrong. Please fix the below errors.")
    else:
        form = StockReportForm(instance=stock_report, user=request.user)
    context = {"form": form, "monthly_report": monthly_report}
    return render(request, "stock/stock_report_form.html", context)


@login_required
def delete_record_stock_report(request, pk):
    stock_report = get_object_or_404(StockReport, pk=pk)
    stock_report.delete()
    messages.success(request, "Report has been deleted.")
    if request.headers.get("Hx-Trigger", "") == "delete-one-btn":
        url = reverse_lazy("stock-details-view", kwargs={"pk": stock_report.monthly_report.pk})
        return HttpResponseClientRedirect(url)
    else:
        return HttpResponse(status=200)


@login_required
def delete_stock_monthly_report(request, pk):
    monthly_report = get_object_or_404(StockMonthlyReport, pk=pk)
    monthly_stock_reports = StockReport.objects.filter(monthly_report=monthly_report)
    if monthly_stock_reports:
        monthly_report.state = "todo"
        monthly_report.save()
        messages.success(request, f"{monthly_report} monthly reports has been deleted.")
        url = reverse_lazy("stock-report-period", kwargs={"pk": monthly_report.warehouse_location.pk})
    else:
        messages.error(request, "No report found for the selected period.")
        url = reverse_lazy("stock-details-view", kwargs={"pk": monthly_report.id})
    return HttpResponseClientRedirect(url)


@login_required
def submit_stock_monthly_report(request, pk):
    monthly_report = get_object_or_404(StockMonthlyReport, pk=pk)
    monthly_report.state = "submitted"
    monthly_report.save()
    messages.success(request, f"{monthly_report} report has been submitted.")
    url = reverse_lazy("stock-report-period", kwargs={"pk": monthly_report.warehouse_location.pk})
    return HttpResponseClientRedirect(url)


def export_stock_monthly_report(request, warehouse):
    today = datetime.now()
    filename = today.today().strftime("%d-%m-%Y")
    warehouse_location = get_object_or_404(Warehouse, pk=warehouse)
    try:
        all_monthly_report = StockMonthlyReport.objects.filter(
            warehouse_location=warehouse_location, state="submitted"
        ).prefetch_related(Prefetch("stockreport_set", queryset=StockReport.objects.all()))
    except Exception:
        messages.error(request, "At least one submitted report is required.")
        return HttpResponse(200)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename={warehouse_location.name}_stock_report_{filename}.csv"
    write_csv_columns_and_rows(all_monthly_report, response)
    return response
