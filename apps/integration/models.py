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
    provider_identifier = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Unique ID per provider (realm_id, organization_id, tenant_id, etc.)"
    )

    provider_data = EncryptedJSONField(default=dict, blank=True)  # api_key, secrets, extra info

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


class ProviderFieldMapping(models.Model):
    ENTITY_CHOICES = [
        ('Invoice', 'Invoice'),
        ('Customer', 'Customer'),
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    provider = models.ForeignKey(IntegrationProvider, on_delete=models.CASCADE)

    entity_name = models.CharField(
        max_length=50,
        choices=ENTITY_CHOICES,
        help_text="Select the entity type, e.g., Invoice, Customer"
    )
    local_field = models.CharField(
        max_length=100,
        help_text="Your database field name"
    )
    provider_field = models.CharField(
        max_length=100,
        help_text="The field name in the provider API response"
    )

    is_required = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'provider', 'entity_name', 'local_field')
        verbose_name = "Field Mapping"
        verbose_name_plural = "Field Mappings"

    def __str__(self):
        return f"{self.company} | {self.provider} | {self.entity_name} | {self.local_field} -> {self.provider_field}"
