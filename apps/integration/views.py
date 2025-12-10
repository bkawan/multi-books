import uuid

from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes

from apps.company.models import Company
from .services import create_or_update_qbo_customers
from apps.integration.models import IntegrationProvider, CompanyIntegration
from apps.integration.selectors import get_qbo_customers, get_qbo_invoices
from .services import create_or_update_qbo_invoices


# @login_required
def connect_to_quickbooks(request, company_id):
    """
    Redirect user to QuickBooks OAuth authorization page using provider config from DB.
    """
    company = get_object_or_404(Company, id=company_id, is_active=True)
    # Get QuickBooks IntegrationProvider from DB
    provider = get_object_or_404(IntegrationProvider, name="quickbooks_online")
    # Load OAuth config from provider.config
    config = provider.config
    client_id = config.get("client_id")
    client_secret = config.get("client_secret")
    redirect_uri = config.get("redirect_uri")
    environment = config.get("environment")
    scope_list = config.get("scope", [])
    # Convert strings to Scopes enum if needed
    scopes_enum = []
    for s in scope_list:
        try:
            scopes_enum.append(Scopes(s))
        except ValueError:
            scopes_enum.append(s)

    # Generate state for CSRF protection
    state = str(uuid.uuid4())
    request.session['qb_oauth_state'] = state
    request.session['qb_company_id'] = company_id

    # Initialize AuthClient dynamically from DB
    auth_client = AuthClient(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        environment=environment,
    )

    # Get authorization URL dynamically with scopes from DB
    authorization_url = auth_client.get_authorization_url(
        scopes_enum,
        state_token=state
    )
    return redirect(authorization_url)


# @login_required
def quickbooks_callback(request):
    """
    Handle QuickBooks OAuth callback:
    - Exchange code for access/refresh tokens
    - Store tokens, expiry, and granted scopes in CompanyIntegration
    """
    code = request.GET.get("code")
    state = request.GET.get("state")
    realm_id = request.GET.get("realmId")

    saved_state = request.session.get("qb_oauth_state")
    company_id = request.session.get("qb_company_id")

    if not state or state != saved_state:
        return HttpResponseBadRequest("Invalid state parameter")
    if not company_id:
        return HttpResponseBadRequest("Company ID not found in session")

    # Get the company and provider
    company = get_object_or_404(Company, id=company_id, is_active=True)
    provider = get_object_or_404(IntegrationProvider, name="quickbooks_online")

    # Load OAuth config from provider.config
    config = provider.config
    client_id = config.get("client_id")
    client_secret = config.get("client_secret")
    redirect_uri = config.get("redirect_uri")
    environment = config.get("environment")

    # Initialize AuthClient
    auth_client = AuthClient(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        environment=environment,
    )

    # Exchange code for tokens
    try:
        auth_client.get_bearer_token(code, realm_id=realm_id)
    except Exception as e:
        return HttpResponse(f"Error obtaining token: {e}", status=500)

    # Save or update the integration for this company
    CompanyIntegration.objects.update_or_create(
        company=company,
        provider=provider,
        provider_identifier=realm_id,
        defaults={
            "credentials": {
                "access_token": auth_client.access_token,
                "refresh_token": auth_client.refresh_token,
                "expires_in": auth_client.expires_in,
                "token_created_at": timezone.now().isoformat(),
            },
            "provider_data": {
                "realm_id": realm_id,
            },
            "is_active": True,
        }
    )

    # Cleanup session
    request.session.pop("qb_oauth_state", None)
    request.session.pop("qb_company_id", None)

    return HttpResponse("QuickBooks connected successfully!")


# @login_required
def get_customers_api(request, company_id):
    company_integration = CompanyIntegration.objects.filter(
        company_id=company_id,
        provider__name="quickbooks_online"
    ).first()

    if not company_integration:
        return JsonResponse({"error": "QuickBooks not connected for this company"}, status=400)

    try:
        customers = get_qbo_customers(company_integration)
        create_or_update_qbo_customers(company_integration, customers)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"customers": customers})


# @login_required
def get_invoices_api(request, company_id):
    company_integration = CompanyIntegration.objects.filter(
        company_id=company_id,
        provider__name="quickbooks_online"
    ).first()

    if not company_integration:
        return JsonResponse({"error": "QuickBooks not connected for this company"}, status=400)
    try:
        invoices = get_qbo_invoices(company_integration)
        create_or_update_qbo_invoices(company_integration, invoices)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"invoices": invoices})
