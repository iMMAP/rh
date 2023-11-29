from django.urls import path

from . import views as user_views

urlpatterns = [
    # Stock Warehouse Routes
    path("stocks/", user_views.stock_index_view, name="stocks"),
    path("stocks/report/", user_views.stock_report, name="stock_report"),
    path("stocks/report/<str:pk>", user_views.stock_report_view, name="stock_report"),
    path(
        "stocks/report/submit/<str:pk>",
        user_views.submit_stock_report_form,
        name="submit_stock_report",
    ),
]
