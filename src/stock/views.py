import calendar
from collections import defaultdict
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django_htmx.http import HttpResponseClientRedirect
from extra_settings.models import Setting

from stock.filter import StockDashboardFilter, StockFilter, StockMonthlyReportFilter, StockReportFilter
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
                return redirect("create-warehouse-location")
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

    if not monthly_report.exists():
        # TODO: handle this better in the frontend
        warehouse.delete()
        messages.success(request, "Warehouse location has been delete.")
        if request.headers.get("Hx-Trigger", "") == "delete-btn":
            url = reverse_lazy("stocks", kwargs={})
            return HttpResponseClientRedirect(url)
        else:
            return HttpResponse(status=200)
    else:
        url = reverse_lazy("stocks", kwargs={})
        messages.error(request, "Cannot delete warehouse with existance reports.")
        return HttpResponseClientRedirect(url)


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

    context = {"form": form, "warehouse": warehouse, "monthly_report": monthly_report}
    return render(request, "stock/stock_report_period_form.html", context)


@login_required
def delete_stock_report_period(request, pk):
    monthly_report = get_object_or_404(StockMonthlyReport, pk=pk)
    if not monthly_report.stockreport_set.exists():
        monthly_report.delete()
        messages.success(request, f"{monthly_report} Report has been deleted.")
        return HttpResponse(status=200)
    else:
        url = reverse_lazy("stock-report-period", kwargs={"pk": monthly_report.warehouse_location.id})
        messages.error(request, f"Cannot delete {monthly_report} report period due to existing associated reports.")
        return HttpResponseClientRedirect(url)


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
                    " Report was added successfully.",
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
        monthly_stock_reports.delete()
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


@login_required
def report_details_view(request, report):
    stock_report = get_object_or_404(StockReport, pk=report)
    monthly_report = stock_report.monthly_report
    context = {"stock_report": stock_report, "monthly_report": monthly_report}
    return render(request, "stock/report_details_view.html", context)


@login_required
def stock_dashbaord(request):
    user_org = request.user.profile.organization
    # Prefetch related stock reports for submitted stock monthly reports
    stock_report_prefetch = Prefetch("stockreport_set", queryset=StockReport.objects.all())

    # Prefetch related stock monthly reports with the submitted state
    stock_monthly_report_prefetch = Prefetch(
        "stockmonthlyreport_set",
        queryset=StockMonthlyReport.objects.filter(state="submitted").prefetch_related(stock_report_prefetch),
    )

    # Annotate the total beneficiary coverage
    ware = (
        Warehouse.objects.filter(organization=user_org)
        .prefetch_related(stock_monthly_report_prefetch)
        .annotate(total_beneficiary=Coalesce(Sum("stockmonthlyreport__stockreport__beneficiary_coverage"), 0))
    )

    warehouses_filter = StockDashboardFilter(request.GET, queryset=ware, request=request)
    warehouses = warehouses_filter.qs
    # Prepare the aggregated data for the response.
    data_calculate = {
        "total_beneficiary_coverage": warehouses.aggregate(
            total_beneficiary_coverage_sum=Sum("stockmonthlyreport__stockreport__beneficiary_coverage")
        )["total_beneficiary_coverage_sum"]
        or 0,
        "total_reports": warehouses.aggregate(total_reports_sum=Count("stockmonthlyreport__stockreport__id"))[
            "total_reports_sum"
        ]
        or 0,  # Counting reports as the sum of ids
        "total_warehouse": warehouses.count(),
        "total_stock": warehouses.aggregate(total_stock_sum=Sum("stockmonthlyreport__stockreport__qty_in_stock"))[
            "total_stock_sum"
        ]
        or 0,
        "total_pipeline": warehouses.aggregate(
            total_pipeline_sum=Sum("stockmonthlyreport__stockreport__qty_in_pipeline")
        )["total_pipeline_sum"]
        or 0,
        "total_people_assisted": warehouses.aggregate(
            total_people_assisted_sum=Sum("stockmonthlyreport__stockreport__people_to_assisted")
        )["total_people_assisted_sum"]
        or 0,
        "total_unit_required": warehouses.aggregate(
            total_unit_required_sum=Sum("stockmonthlyreport__stockreport__unit_required")
        )["total_unit_required_sum"]
        or 0,
    }

    # Initialize defaultdicts to handle default values
    clusters_beneficiary_dict = defaultdict(int)
    cluster_pipeline_list = defaultdict(int)
    cluster_stock_list = defaultdict(int)
    months_beneficiary = defaultdict(int)
    total_clusters = 0
    warehouse_beneficiary = {"warehouse_name": [], "total_beneficiary": []}

    # Create a single query to fetch all necessary data
    warehouse_data = warehouses.annotate(
        total_beneficiary=Coalesce(Sum("stockmonthlyreport__stockreport__beneficiary_coverage"), 0),
        total_stock=Coalesce(Sum("stockmonthlyreport__stockreport__qty_in_stock"), 0),
        total_pipeline=Coalesce(Sum("stockmonthlyreport__stockreport__qty_in_pipeline"), 0),
        total_people_assisted=Coalesce(Sum("stockmonthlyreport__stockreport__people_to_assisted"), 0),
        total_unit_required=Coalesce(Sum("stockmonthlyreport__stockreport__unit_required"), 0),
    ).values(
        "name",
        "total_beneficiary",
        "total_stock",
        "total_pipeline",
        "total_people_assisted",
        "total_unit_required",
        "stockmonthlyreport__stockreport__cluster__code",
        "stockmonthlyreport__stockreport__beneficiary_coverage",
        "stockmonthlyreport__stockreport__qty_in_pipeline",
        "stockmonthlyreport__stockreport__qty_in_stock",
        "stockmonthlyreport__from_date",
    )

    # Process the data
    for data in warehouse_data:
        warehouse_name = data["name"] if data["name"] is not None else "Unknown"
        total_beneficiary = data["total_beneficiary"] if data["total_beneficiary"] is not None else 0

        warehouse_beneficiary["warehouse_name"].append(warehouse_name)
        warehouse_beneficiary["total_beneficiary"].append(total_beneficiary)

        report_date = data["stockmonthlyreport__from_date"]
        months_beneficiary[report_date] += data.get("stockmonthlyreport__stockreport__beneficiary_coverage", 0) or 0

        cluster_code = data["stockmonthlyreport__stockreport__cluster__code"]
        if cluster_code not in clusters_beneficiary_dict:
            total_clusters += 1

        clusters_beneficiary_dict[cluster_code] += (
            data.get("stockmonthlyreport__stockreport__beneficiary_coverage", 0) or 0
        )
        cluster_pipeline_list[cluster_code] += data.get("stockmonthlyreport__stockreport__qty_in_pipeline", 0) or 0
        cluster_stock_list[cluster_code] += data.get("stockmonthlyreport__stockreport__qty_in_stock", 0) or 0

    # Create lists using comprehensions
    clusters = list(clusters_beneficiary_dict.keys())
    number_in_stock = list(cluster_stock_list.values())
    number_in_pipeline = list(cluster_pipeline_list.values())
    beneficiary_coverage = list(clusters_beneficiary_dict.values())

    df = pd.DataFrame(warehouse_beneficiary)
    fig = px.bar(df, x="warehouse_name", y="total_beneficiary")

    fig.update_traces(marker=dict(color="#a52824"))
    fig.update_layout(
        xaxis_title="Warehouses",
        yaxis_title="Beneficiaries",
        showlegend=True,
        margin=dict(r=0, t=50, b=0, l=0),
        title={
            "text": "<b>Warehouse Beneficiary Coverage Trends</b>",
            "font": {
                "size": 14,
                "color": "#A52824",
            },
        },
    )
    # Line chart
    # Create the DataFrame for the line chart using pd.Series constructor
    df = pd.DataFrame(
        {
            "x": pd.Series(months_beneficiary.keys()).fillna("unknown"),
            "y": pd.Series(months_beneficiary.values()).fillna(0),
        }
    )
    df = df.sort_values(by="x")
    line_chart = px.line(
        df,
        x="x",
        y="y",
    )
    line_chart.update_layout(
        xaxis_title="Months",
        yaxis_title="Beneficiary Coverage",
        showlegend=True,
        margin=dict(r=0, t=50, b=0, l=0),
        title={
            "text": "<b>Stock Report Monthly Trends</b>",
            "font": {
                "size": 14,
                "color": "#A52824",
            },
        },
    )
    line_chart.update_traces(
        line=dict(shape="spline", color="#a52824"),
        mode="lines+markers",
        hovertemplate="<b>Month:</b> %{x}<br><b>Beneficiary:</b> %{y}<br><extra></extra>",
    )

    fig2 = go.Figure()
    # Plot each metric as a line
    fig2.add_trace(
        go.Scatter(
            x=clusters,
            y=number_in_stock,
            mode="lines+markers",
            name="Quantity in Stock",
            hovertemplate="<b>cluster:</b> %{x}<br><b>quantity in stock:</b> %{y}<br><extra></extra>",
            line=dict(shape="spline"),
        )
    )
    fig2.add_trace(
        go.Scatter(
            x=clusters,
            y=number_in_pipeline,
            mode="lines+markers",
            name="Quantity in Pipeline",
            hovertemplate="<b>cluster:</b> %{x}<br><b>quantity in pipeline:</b> %{y}<br><extra></extra>",
            line=dict(shape="spline"),
        )
    )
    fig2.add_trace(
        go.Scatter(
            x=clusters,
            y=beneficiary_coverage,
            mode="lines+markers",
            name="Beneficiary Coverage",
            hovertemplate="<b>cluster:</b> %{x}<br><b>beneficiary coverage:</b> %{y}<br><extra></extra>",
            line=dict(shape="spline"),
        )
    )

    # Update layout
    fig2.update_layout(
        xaxis_title="Clusters",
        yaxis_title="Stock Data Values",
        showlegend=True,
        margin=dict(r=0, t=50, b=0, l=0),
        height=400,
        title={
            "text": "<b>Cluster-wise In Stock, In Pipeline, and Beneficiary Coverage Trends</b>",
            "font": {
                "size": 14,
                "color": "#A52824",
            },
        },
    )
    data_calculate["total_cluster"] = total_clusters
    context = {
        "bar_chart": fig.to_html(),
        "pie_chart": fig2.to_html(),
        "line_chart": line_chart.to_html(),
        "data": data_calculate,
        "warehouse_filter": warehouses_filter,
    }
    return render(request, "stock/stock_dashboard.html", context)


def export_org_stock_beneficiary(request):
    user_org = request.user.profile.organization
    ware = Warehouse.objects.filter(organization=user_org).annotate(
        total_beneficiary=Sum("stockmonthlyreport__stockreport__beneficiary_coverage")
    )
    warehouses_filter = StockDashboardFilter(request.GET, queryset=ware, request=request)
    warehouses = warehouses_filter.qs

    today = datetime.now()
    filename = today.today().strftime("%d-%m-%Y")

    try:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={user_org}_stock_reports_exported_on_{filename}.csv"
        write_csv_columns_and_rows(warehouses, response)
        return response
    except Exception as e:
        print(f"Error: {e}")
        return HttpResponse(status=500)
