from django.urls import path, include

urlpatterns = [
    path('zoho/', include('apps.integration.zoho.urls')),
    path('quickbooks/', include('apps.integration.quickbooks.urls')),
]
