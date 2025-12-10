from celery import shared_task

from apps.integration.models import CompanyIntegration
from apps.integration.selectors import get_qbo_customers, get_qbo_invoices
from apps.integration.services import create_or_update_qbo_customers, create_or_update_qbo_invoices


@shared_task
def sync_qb_customers(company_integration_id):
    company_integration = CompanyIntegration.objects.get(id=company_integration_id)
    try:
        customers = get_qbo_customers(company_integration)
        create_or_update_qbo_customers(company_integration, customers)
        print(f"Fetched {len(customers)} customers for company {company_integration.company_id}")
    except Exception as e:
        print(f"Failed to fetch QuickBooks customers: {e}")


@shared_task
def sync_qbo_invoices(company_integration_id):
    company_integration = CompanyIntegration.objects.get(id=company_integration_id)
    try:
        invoices = get_qbo_invoices(company_integration)
        create_or_update_qbo_invoices(company_integration, invoices)
        print(f"Fetched {len(invoices)} Invoices for company {company_integration.company_id}")
    except Exception as e:
        print(f"Failed to fetch QuickBooks Invoices: {e}")
