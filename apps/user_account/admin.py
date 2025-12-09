# apps/user_account/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserAccount


@admin.register(UserAccount)
class UserAccountAdmin(UserAdmin):
    model = UserAccount

    # Fields to display in list view
    list_display = ("email", "username", "phone", "is_active", "is_staff", "is_superuser")

    # Fields searchable
    search_fields = ("email", "username", "phone")

    # Minimal fieldsets for edit form
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Additional Info", {"fields": ("phone",)}),
    )

    # Fields for the add user form
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "phone", "password1", "password2", "is_active", "is_staff", "is_superuser"),
        }),
    )

    ordering = ("email",)
