from django.db import transaction

from apps.invoice.models import Invoice


def create_or_update_qbo_invoices(company_integration, invoices: list):
    company = company_integration.company
    provider = company_integration.provider

    with transaction.atomic():
        for data in invoices:
            invoice_id = data.get("Id")
            customer_id = data.get("CustomerRef", {}).get("value")
            invoice_no = data.get("DocNumber")
            defaults = {
                "integration_provider": provider,
                "invoice_no": invoice_no,
                "invoice_date": data.get("TxnDate"),
                "due_date": data.get("DueDate"),
                "customer_id": customer_id,
                "amount": data.get("TotalAmt", 0),
                "invoice_balance": data.get("Balance", 0),
                "integration_raw_data": data,
            }

            invoice, created = Invoice.objects.update_or_create(
                company=company,
                invoice_id=invoice_id,
                integration_provider=company_integration.provider,
                defaults=defaults
            )
