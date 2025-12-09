# apps/company/admin.py
from django.contrib import admin
from .models import Company, CompanyMember


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(CompanyMember)
class CompanyMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "user_account", "company", "role")
    list_filter = ("role", "company")
    search_fields = ("user_account__email", "user_account__username", "company__name")
    autocomplete_fields = ("user_account", "company")  # for large datasets
