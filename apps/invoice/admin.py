from django.contrib import admin

from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_no",
        "customer_id",
        "invoice_date",
        "due_date",
        "amount",
        "invoice_balance",
        "company",
        "integration_provider",
    )

    list_filter = (
        "company",
        "integration_provider",
        "invoice_date",
        "due_date",
    )

    search_fields = (
        "invoice_no",
        "customer_id",
        "invoice_id",
        "reference",
    )
