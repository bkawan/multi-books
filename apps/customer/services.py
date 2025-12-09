from django.db import transaction
from apps.customer.models import Customer
from apps.integration.models import CompanyIntegration


def create_or_update_qbo_customers(company_integration: CompanyIntegration, customers: list):
    """
    Save or update customers from a provider (e.g., QuickBooks) for a specific company.

    Args:
        company_integration (CompanyIntegration): The company integration object.
        customers(list): List of customer dicts from the provider API.
    """
    company = company_integration.company
    provider = company_integration.provider

    with transaction.atomic():
        for data in customers:
            # Extract address info
            addresses = data.get("BillAddr", {})
            primary_email = data.get("PrimaryEmailAddr", {}).get("Address")
            secondary_email = data.get("OtherEmailAddr", {}).get("Address") if data.get("OtherEmailAddr") else None
            primary_phone = data.get("PrimaryPhone", {}).get("FreeFormNumber")
            secondary_phone = data.get("AlternatePhone", {}).get("FreeFormNumber") if data.get(
                "AlternatePhone") else None

            # Prepare defaults for update_or_create
            customer_defaults = {
                "company": company,
                "integration_provider": provider,
                "integration_raw_data": data,
                "company_name": data.get("CompanyName", ""),
                "sales_tax_id": data.get("SalesTaxCodeRef", {}).get("value", ""),
                "customer_id": data.get("Id", ""),
                "license_id": data.get("TaxExemptionRef", {}).get("value", ""),
                "dba": data.get("DisplayName", ""),
                "tax_id": data.get("TaxIdentifier", ""),
                "country": addresses.get("Country", ""),
                "city": addresses.get("City", ""),
                "state": addresses.get("CountrySubDivisionCode", ""),
                "street_address": addresses.get("Line1", ""),
                "zipcode": addresses.get("PostalCode", ""),
                "company_email1": primary_email or "",
                "company_email2": secondary_email or "",
                "company_contact1": primary_phone or "",
                "company_contact2": secondary_phone or "",
            }

            # Create or update
            customer, created = Customer.objects.update_or_create(
                company=company,
                customer_id=data.get("Id", ""),
                defaults=customer_defaults
            )
