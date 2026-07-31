from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "id",
        "email",
        "username",
        "user_role",
        "is_verified",
        "is_staff",
    )

    list_filter = (
        "user_role",
        "is_verified",
        "is_staff",
    )

    ordering = ("id",)

    fieldsets = (
        (None, {
            "fields": (
                "email",
                "username",
                "password",
            )
        }),

        ("Personal Info", {
            "fields": (
                "first_name",
                "last_name",
                "phone_number",
                "profile_image",
            )
        }),

        ("Role", {
            "fields": (
                "user_role",
                "is_verified",
            )
        }),

        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),

        ("Important Dates", {
            "fields": (
                "last_login",
                "date_joined",
            )
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "username",
                "password1",
                "password2",
                "user_role",
            ),
        }),
    )

    search_fields = (
        "email",
        "username",
    )