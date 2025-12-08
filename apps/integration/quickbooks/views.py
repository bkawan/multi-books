import json
import uuid
import requests
from datetime import timedelta
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes

from apps.integration.quickbooks.models import QuickBooksCompany, QuickBooksOAuthToken


def connect_to_quickbooks(request):
    """
    Redirect user to QuickBooks OAuth authorization page.
    """
    state = str(uuid.uuid4())
    request.session['qb_oauth_state'] = state

    auth_client = AuthClient(
        client_id=settings.QBO_CLIENT_ID,
        client_secret=settings.QBO_CLIENT_SECRET,
        redirect_uri=settings.QBO_REDIRECT_URI,
        environment=settings.QBO_ENVIRONMENT,
    )

    # Use Accounting scope
    authorization_url = auth_client.get_authorization_url([Scopes.ACCOUNTING, Scopes.OPENID], state_token=state)
    return redirect(authorization_url)


def quickbooks_callback(request):
    """
    Handle OAuth callback, exchange code for access/refresh tokens,
    and store them in session.
    """
    code = request.GET.get('code')
    state = request.GET.get('state')
    realm_id = request.GET.get('realmId')

    saved_state = request.session.get('qb_oauth_state')
    if not state or state != saved_state:
        return HttpResponseBadRequest("Invalid state parameter")

    auth_client = AuthClient(
        client_id=settings.QBO_CLIENT_ID,
        client_secret=settings.QBO_CLIENT_SECRET,
        redirect_uri=settings.QBO_REDIRECT_URI,
        environment=settings.QBO_ENVIRONMENT,
    )

    try:
        auth_client.get_bearer_token(code, realm_id=realm_id)
    except Exception as e:
        return HttpResponse(f"Error obtaining token: {e}", status=500)

    realm_id = auth_client.realm_id

    data = get_company_info(access_token=auth_client.access_token, realm_id=realm_id)
    qb_company_name = data.get('CompanyInfo')['CompanyName']
    company, created = QuickBooksCompany.objects.update_or_create(
        realm_id=realm_id,
        defaults={
            # "user_account": request.user,
            "company_name": qb_company_name,
        }
    )

    QuickBooksOAuthToken.objects.update_or_create(
        company=company,
        defaults={
            "access_token": auth_client.access_token,
            "refresh_token": auth_client.refresh_token,
            "access_token_expires_at": timezone.now() + timedelta(seconds=auth_client.expires_in),
        }
    )

    return redirect('/')


def refresh_qb_token(request):
    """
    Refresh access token if expired, using session-stored refresh token.
    """
    access_token = request.session.get('qb_access_token')
    refresh_token = request.session.get('qb_refresh_token')
    token_expiry = request.session.get('qb_token_expiry')

    if not access_token or not refresh_token:
        return None

    # Convert token_expiry to timezone-aware datetime
    expiry_time = timezone.datetime.fromtimestamp(token_expiry, tz=timezone.get_current_timezone())

    # If token is still valid for 5+ minutes, return it
    if expiry_time > timezone.now() + timedelta(minutes=5):
        return access_token

    # Token expired → refresh
    try:
        auth_client = AuthClient(
            client_id=settings.QBO_CLIENT_ID,
            client_secret=settings.QBO_CLIENT_SECRET,
            redirect_uri=settings.QBO_REDIRECT_URI,
            environment=settings.QBO_ENVIRONMENT,
        )
        auth_client.refresh(refresh_token)

        # Update session
        request.session['qb_access_token'] = auth_client.access_token
        request.session['qb_refresh_token'] = auth_client.refresh_token
        request.session['qb_token_expiry'] = (timezone.now() + timedelta(seconds=auth_client.expires_in)).timestamp()

        return auth_client.access_token
    except Exception as e:
        print("QuickBooks token refresh failed:", str(e))
        return None


def get_company_info(access_token, realm_id):
    base_url = settings.QBO_BASE_URL
    url = f"{base_url}/v3/company/{realm_id}/companyinfo/{realm_id}"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        data = {"error": "QuickBooks API request failed", "details": str(e)}
