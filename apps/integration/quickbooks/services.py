from django.conf import settings
import requests

from apps.integration.quickbooks.models import QuickBooksCompany, QuickBooksOAuthToken


def fetch_and_save_quickbooks_customer(company_id):
    qb_company = QuickBooksCompany.objects.get(id=company_id)
    qb_oauth_token = QuickBooksOAuthToken.objects.get(company=qb_company)

    base_url = settings.QBO_BASE_URL

    base_url = settings.QBO_BASE_URL
    url = f"{base_url}/v3/company/{qb_company.realm_id}/query"
    query = "SELECT * FROM Customer MAXRESULTS 31"

    headers = {
        "Authorization": f"Bearer {qb_oauth_token.access_token}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, params={"query": query}, timeout=10)
        response.raise_for_status()
        data = response.json()

    except Exception as e:
        print(e)
