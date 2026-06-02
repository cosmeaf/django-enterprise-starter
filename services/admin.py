from django.contrib import admin
from services.models import EmailLog

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "template_key", "status", "mode", "attempts", "error_type", "sent_at", "created_at")
    search_fields = ("subject", "template_key", "from_email", "error_type", "error_message")
    list_filter = ("status", "mode", "template_key", "error_type")
    readonly_fields = ("created_at", "updated_at", "sent_at", "error_details")