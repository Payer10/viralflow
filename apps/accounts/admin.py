from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Admin config for the custom email-based User model.
    Django's default UserAdmin assumes a `username` field, so the
    fieldsets/list views are rebuilt around `email` instead.
    """

    ordering = ["-created_at"]
    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "created_at",
    ]
    list_filter = ["is_active", "is_staff", "is_superuser", "created_at"]
    search_fields = ["email", "first_name", "last_name"]
    readonly_fields = ["id", "created_at", "updated_at", "last_login"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "avatar")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )