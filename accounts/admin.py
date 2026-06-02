from django.contrib import admin

from accounts.models import (
    LoginAttempt,
    LoginEvent,
    OtpCode,
    ResetPasswordToken,
    UserSession,
)


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "ip_address",
        "success",
        "reason",
        "created_at",
    )

    search_fields = (
        "email",
        "ip_address",
        "reason",
    )

    list_filter = (
        "success",
        "reason",
    )


@admin.register(LoginEvent)
class LoginEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "ip",
        "success",
        "risk_score",
        "created_at",
    )

    search_fields = (
        "user__email",
        "ip",
    )

    list_filter = (
        "success",
        "risk_score",
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "ip_address",
        "browser",
        "os",
        "device",
        "is_active",
        "created_at",
        "last_seen",
    )

    search_fields = (
        "user__email",
        "ip_address",
        "token_jti",
    )

    list_filter = (
        "is_active",
        "browser",
        "os",
        "device",
    )


@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "attempts",
        "is_used",
        "created_at",
        "expires_at",
    )

    search_fields = (
        "user__email",
    )

    list_filter = (
        "is_used",
    )


@admin.register(ResetPasswordToken)
class ResetPasswordTokenAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "token",
        "is_used",
        "created_at",
    )

    search_fields = (
        "user__email",
    )

    list_filter = (
        "is_used",
    )