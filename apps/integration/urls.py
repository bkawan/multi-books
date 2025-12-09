from django.urls import path
from . import views

urlpatterns = [
    path("qbo/connect/<int:company_id>/", views.connect_to_quickbooks, name="qbo-connect"),
    path("qbo/callback/", views.quickbooks_callback, name="quickbooks_callback"),
    path("qbo/<int:company_id>/customers/", views.get_customers_api, name="quickbooks_get_customers"),
    path("qbo/<int:company_id>/invoices/", views.get_invoices_api, name="quickbooks_get_invoices"),
]
