from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "customer_id",
        "dba",
        "company",
        "integration_provider",
        "created_at",
        "modified_at",
    )
    search_fields = ("company_name", "customer_id", "dba", "tax_id")
    list_filter = ("company", "integration_provider", "created_at")
    readonly_fields = ("created_at", "modified_at", "integration_raw_data")
    ordering = ("-created_at",)
