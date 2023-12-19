from django.urls import path

from . import views as user_views

urlpatterns = [
    # Stock Warehouse Routes
    path("stocks/", user_views.stock_index_view, name="stocks"),
    path("stocks/all_reports/", user_views.all_stock_report, name="all_stock_report"),
    path("stocks/report/<str:pk>", user_views.stock_report_view, name="stock_report"),
    path(
        "stocks/report/submit/<str:pk>",
        user_views.submit_stock_report_form,
        name="submit_stock_report",
    ),
    path("stocks/edit_submitted_stock/<str:pk>", user_views.edit_submitted_stock, name="edit_submitted_stock"),
]
