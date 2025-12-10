from django.urls import path
from . import views
from .api.views import QuickBooksConnectAPIView, QuickBooksCallbackAPIView, QuickBooksOnlineSyncCustomersAPIView

urlpatterns = [
    # path("qbo/connect/<int:company_id>/", views.connect_to_quickbooks, name="qbo-connect"),
    # path("qbo/callback/", views.quickbooks_callback, name="quickbooks_callback"),
    path("qbo/connect/<int:company_id>/", QuickBooksConnectAPIView.as_view(), name="qbo-connect"),
    path("qbo/callback/", QuickBooksCallbackAPIView.as_view(), name="quickbooks_callback"),
    path("qbo/<int:company_id>/customers/", QuickBooksOnlineSyncCustomersAPIView.as_view(),
         name="qbo-sync-customers"),
    path("qbo/<int:company_id>/invoices/", views.get_invoices_api, name="qbo-sync-invoices"),
    path("qbo/<int:company_id>/invoices/", views.get_invoices_api, name="qbo-sync-company"),
]
