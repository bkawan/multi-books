from django.db import models

from apps.company.models import Company
from utils.model_utils import EncryptedJSONField


class IntegrationProvider(models.Model):
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BEARER = "bearer"
    BASIC = "basic"

    AUTH_TYPE_CHOICES = [
        (OAUTH2, "OAuth2"),
        (API_KEY, "API Key"),
        (BEARER, "Bearer Token"),
        (BASIC, "Basic Auth"),
    ]

    name = models.CharField(max_length=50, unique=True)  # e.g., quickbooks, zoho
    display_name = models.CharField(max_length=100)
    auth_type = models.CharField(
        max_length=20, choices=AUTH_TYPE_CHOICES, default=OAUTH2
    )
    config = EncryptedJSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CompanyIntegration(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    provider = models.ForeignKey(IntegrationProvider, on_delete=models.CASCADE)
    # api_key, secrets, extra info
    credentials = EncryptedJSONField(default=dict, blank=True)
    # Provider-specific identifiers (flexible)
    provider_data = EncryptedJSONField(default=dict, blank=True)  # api_key, secrets, extra info

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
