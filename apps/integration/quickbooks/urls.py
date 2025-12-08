# urls.py
from django.http import HttpResponse
from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.connect_to_quickbooks, name="quickbooks_login"),
    path("callback/", views.quickbooks_callback, name="quickbooks_callback"),
]
