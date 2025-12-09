from django.utils import timezone
from datetime import timedelta
from intuitlib.client import AuthClient

from apps.integration.models import CompanyIntegration, ProviderFieldMapping


def refresh_qbo_token_for_integration(company_integration: CompanyIntegration):
    """
    Refresh access token using stored refresh token for CompanyIntegration.
    """
    credentials = company_integration.credentials
    refresh_token = credentials.get("refresh_token")
    expires_in = credentials.get("expires_in")
    token_created_at = credentials.get("token_created_at")

    if not refresh_token or not token_created_at:
        return None

    # Check if token is still valid
    token_created = timezone.datetime.fromisoformat(token_created_at)
    expiry_time = token_created + timedelta(seconds=expires_in)
    if expiry_time > timezone.now() + timedelta(minutes=5):
        return credentials.get("access_token")

    # Refresh token
    provider_config = company_integration.provider.config
    auth_client = AuthClient(
        client_id=provider_config.get("client_id"),
        client_secret=provider_config.get("client_secret"),
        redirect_uri=provider_config.get("redirect_uri"),
        environment=provider_config.get("environment"),
    )
    auth_client.refresh(refresh_token)

    # Update credentials
    company_integration.credentials.update({
        "access_token": auth_client.access_token,
        "refresh_token": auth_client.refresh_token,
        "expires_in": auth_client.expires_in,
        "token_created_at": timezone.now().isoformat(),
    })
    company_integration.save(update_fields=["credentials"])
    return auth_client.access_token


def create_default_invoice_field_mappings_qbo(company, integration_provider):
    """
    Create default field mappings for QuickBooks Online Invoice.
    """
    default_mappings = [
        {"local_field": "customer_id", "provider_field": "CustomerRef.value", "is_required": True},
        {"local_field": "invoice_no", "provider_field": "DocNumber", "is_required": True},
        {"local_field": "invoice_date", "provider_field": "TxnDate", "is_required": True},
        {"local_field": "invoice_type", "provider_field": "CustomField5", "is_required": False},
        {"local_field": "amount", "provider_field": "TotalAmt", "is_required": True},
        {"local_field": "invoice_balance", "provider_field": "Balance", "is_required": False},
        {"local_field": "due_date", "provider_field": "DueDate", "is_required": True},
        {"local_field": "discount", "provider_field": "Line.$Index.Amount", "is_required": False},
        {"local_field": "reference", "provider_field": "", "is_required": False},  # No mapping provided
        {"local_field": "invoice_link", "provider_field": "", "is_required": False},  # No mapping provided
    ]

    for mapping in default_mappings:
        ProviderFieldMapping.objects.update_or_create(
            company=company,
            provider=integration_provider,
            entity_name="Invoice",
            local_field=mapping["local_field"],
            defaults={
                "provider_field": mapping["provider_field"],
                "is_required": mapping["is_required"],
                "description": f"Default QBO mapping for {mapping['local_field']}"
            }
        )

    print(f"Default QBO Invoice mappings created for company '{company}' and provider '{integration_provider}'")
