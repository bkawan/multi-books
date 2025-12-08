from celery import shared_task
from apps.customer.models import Customer
from apps.integration.quickbooks.selectors import get_quickbooks_customers


@shared_task
def sync_quickbooks_customers(company_id):
    customers = get_quickbooks_customers(company_id)

    for qb_customer in customers:
        external_id = qb_customer.get("Id")
        bill_addr = qb_customer.get("BillAddr", {}) or {}
        email_addr = qb_customer.get("PrimaryEmailAddr", {}) or {}
        phone = qb_customer.get("PrimaryPhone", {}) or {}

        customer, created = Customer.objects.update_or_create(
            customer_id=external_id,  # Unique internal mapping
            defaults={
                "company_name": qb_customer.get("DisplayName", "") or "",
                "sales_tax_id": qb_customer.get("PrimaryTaxIdentifier", "") or "",
                "license_id": "",
                "dba": qb_customer.get("CompanyName", "") or "",
                "tax_id": "",

                "company_registration_no": None,
                "duns": None,
                "fincen": None,

                "country": bill_addr.get("Country", "") or "",
                "city": bill_addr.get("City", "") or "",
                "state": bill_addr.get("CountrySubDivisionCode", "") or "",
                "street_address": bill_addr.get("Line1", "") or "",
                "zipcode": bill_addr.get("PostalCode"),

                "company_email1": email_addr.get("Address", "") or "noemail@example.com",
                "company_contact1": phone.get("FreeFormNumber", "") or "0000000000",

                "company_email2": None,
                "company_contact2": None,
                "customer_email1": None,
                "customer_email2": None,
                "customer_contact1": None,
                "customer_contact2": None,
            }
        )

    return f"Synced {len(customers)} QuickBooks Customers"
