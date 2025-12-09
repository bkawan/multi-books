from django.utils import timezone
from datetime import timedelta
from intuitlib.client import AuthClient
from apps.integration.models import CompanyIntegration


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
