import requests
from django.conf import settings
from apps.integration.models import CompanyIntegration
from apps.integration.services import refresh_qbo_token_for_integration


def get_qbo_customers(company_integration: CompanyIntegration):
    """
    Fetch QuickBooks customers for a given company integration.
    Handles token refresh automatically.
    Returns a list of customers or raises an exception.
    """
    access_token = refresh_qbo_token_for_integration(company_integration)
    if not access_token:
        raise Exception("QuickBooks not connected or token expired")

    realm_id = company_integration.provider_data.get("realm_id")
    if not realm_id:
        raise Exception("Realm ID not found for company integration")

    base_url = company_integration.provider.config.get(
        "api_base_url",
        settings.QBO_BASE_URL
    )

    url = f"{base_url}/v3/company/{realm_id}/query"
    query = "SELECT * FROM Customer MAXRESULTS 1000"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, params={"query": query}, timeout=10)
    response.raise_for_status()

    data = response.json()
    customers = data.get("QueryResponse", {}).get("Customer", [])
    return customers


def get_qbo_invoices(company_integration: CompanyIntegration):
    """
    Fetch QuickBooks Invoices for a given company integration.
    Handles token refresh automatically.
    Returns a list of invoices an exception.
    """
    access_token = refresh_qbo_token_for_integration(company_integration)
    if not access_token:
        raise Exception("QuickBooks not connected or token expired")

    realm_id = company_integration.provider_data.get("realm_id")
    if not realm_id:
        raise Exception("Realm ID not found for company integration")

    base_url = company_integration.provider.config.get(
        "api_base_url",
        settings.QBO_BASE_URL
    )

    url = f"{base_url}/v3/company/{realm_id}/query"
    params = {
        "query": "SELECT * FROM Invoice  MAXRESULTS 1000",
        "minorversion": "75"  #
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    customers = data.get("QueryResponse", {}).get("Invoice", [])
    return customers
