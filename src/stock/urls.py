from django.urls import path

from . import views as user_views

urlpatterns = [
    # Stock Warehouse Routes
    path(
        "stocks/",
        user_views.stock_index_view,
        name="stocks",
    ),
    path("ajax/load-stock-types", user_views.get_cluster_stock_type, name="get-cluster-stock-type"),
    # warehouse location create
    path(
        "warehouse/create",
        user_views.create_warehouse_location,
        name="create-warehouse-location",
    ),
    path(
        "warehouse/update/<str:pk>",
        user_views.update_warehouse_location,
        name="update-warehouse-location",
    ),
    path(
        "warehouse/copy/<str:pk>",
        user_views.copy_warehouse_location,
        name="copy-warehouse-location",
    ),
    path(
        "warehouse/delete/<str:pk>",
        user_views.delete_warehouse_location,
        name="delete-warehouse-location",
    ),
    path(
        "stock/report/period/<str:warehouse>",
        user_views.create_stock_report_period,
        name="create-report-period",
    ),
    path(
        "stock/report/delete/<str:pk>",
        user_views.delete_stock_report_period,
        name="delete-report-period",
    ),
    path(
        "stock/reports/periods/<str:pk>",
        user_views.stock_report_period_list,
        name="stock-report-period",
    ),
    path(
        "stock/report-period/update/<str:report>",
        user_views.update_stock_report_period,
        name="stock-report-period-update",
    ),
    path(
        "stock/details/<str:pk>",
        user_views.stock_details_view,
        name="stock-details-view",
    ),
    path(
        "stock/reports/<str:pk>",
        user_views.create_stock_monthly_report,
        name="stock-report-create",
    ),
    path("stock/report/submit/<str:pk>", user_views.submit_stock_monthly_report, name="submit-stock-monthly-report"),
    path(
        "stock/monthly-report/delete/<str:pk>",
        user_views.delete_stock_monthly_report,
        name="monthly-stock-report-delete",
    ),
    path(
        "stock/monthly-report/copy/<str:pk>",
        user_views.copy_stock_monthly_report,
        name="copy-stock-monthly-report",
    ),
    path(
        "stock/monthly-report/update/<str:pk>",
        user_views.update_stock_monthly_report,
        name="update-stock-monthly-report",
    ),
    path(
        "stock/single-report/delete/<str:pk>",
        user_views.delete_record_stock_report,
        name="delete-record-stock-report",
    ),
    path(
        "stock/monthly-report/export/<str:warehouse>",
        user_views.export_stock_monthly_report,
        name="stock-monthly-report-export",
    ),
]
