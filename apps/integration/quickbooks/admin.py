from django.contrib import admin
from .models import QuickBooksCompany, QuickBooksOAuthToken


@admin.register(QuickBooksCompany)
class QuickBooksCompanyAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "realm_id",
        "user_account",
        "created_at",
        "modified_at",
    )
    search_fields = ("company_name", "realm_id", "user_account__email")
    list_filter = ("created_at",)
    ordering = ("-created_at",)


@admin.register(QuickBooksOAuthToken)
class QuickBooksOAuthTokenAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "token_status",
        "access_token_expires_at",
        "created_at",
        "modified_at",
    )
    readonly_fields = (
        "created_at",
        "modified_at",
    )
    search_fields = ("company__company_name", "company__realm_id")
    ordering = ("-created_at",)

    def token_status(self, obj):
        return "VALID" if obj.is_access_token_valid() else "EXPIRED"

    token_status.short_description = "Access Token Status"
