from django.contrib import admin
from .models import IntegrationProvider, CompanyIntegration


@admin.register(IntegrationProvider)
class IntegrationProviderAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "display_name",
        "auth_type",
        "is_active",
        "created_at",
        "modified_at",
    )
    list_filter = ("auth_type", "is_active", "created_at")
    search_fields = ("name", "display_name")
    readonly_fields = ("created_at", "modified_at")
    ordering = ("name",)


@admin.register(CompanyIntegration)
class CompanyIntegrationAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "provider",
        "is_active",
        "created_at",
        "modified_at",
    )
    list_filter = ("provider", "is_active", "created_at")
    search_fields = ("company__name", "provider__name")
    readonly_fields = ("created_at", "modified_at")
    ordering = ("company", "provider")
