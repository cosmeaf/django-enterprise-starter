from django.db import models
from django.utils import timezone


class EmailLog(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        QUEUED = "queued", "Queued"
        SENDING = "sending", "Sending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        RETRYING = "retrying", "Retrying"
        CANCELLED = "cancelled", "Cancelled"

    class Mode(models.TextChoices):
        SYNC = "sync", "Sync"
        ASYNC = "async", "Async"
        AUTO = "auto", "Auto"

    class Provider(models.TextChoices):
        SMTP = "smtp", "SMTP"
        BREVO = "brevo", "Brevo"
        UNKNOWN = "unknown", "Unknown"

    subject = models.CharField(max_length=255)
    template_key = models.CharField(max_length=100, db_index=True)

    from_email = models.EmailField()
    to = models.JSONField(default=list)
    cc = models.JSONField(default=list, blank=True)
    bcc = models.JSONField(default=list, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    mode = models.CharField(
        max_length=20,
        choices=Mode.choices,
        default=Mode.AUTO,
        db_index=True,
    )

    provider = models.CharField(
        max_length=30,
        choices=Provider.choices,
        default=Provider.SMTP,
        db_index=True,
    )

    task_id = models.CharField(max_length=255, blank=True, db_index=True)

    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)

    error_code = models.CharField(max_length=100, blank=True, db_index=True)
    error_type = models.CharField(max_length=150, blank=True)
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    queued_at = models.DateTimeField(null=True, blank=True)
    sending_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    last_attempt_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "email_log"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["template_key", "created_at"]),
            models.Index(fields=["mode", "status"]),
            models.Index(fields=["provider", "status"]),
        ]

    def __str__(self):
        return f"{self.subject} | {self.status} | {self.mode}"

    def mark_queued(self, task_id=None):
        self.status = self.Status.QUEUED
        self.queued_at = timezone.now()
        if task_id:
            self.task_id = task_id
        self.save(update_fields=["status", "queued_at", "task_id", "updated_at"])

    def mark_sending(self):
        now = timezone.now()
        self.status = self.Status.SENDING
        self.sending_at = now
        self.last_attempt_at = now
        self.attempts += 1
        self.save(update_fields=[
            "status",
            "sending_at",
            "last_attempt_at",
            "attempts",
            "updated_at",
        ])

    def mark_sent(self):
        self.status = self.Status.SENT
        self.sent_at = timezone.now()
        self.error_code = ""
        self.error_type = ""
        self.error_message = ""
        self.error_details = {}
        self.save(update_fields=[
            "status",
            "sent_at",
            "error_code",
            "error_type",
            "error_message",
            "error_details",
            "updated_at",
        ])

    def mark_failed(
        self,
        *,
        error_code="EMAIL_SEND_FAILED",
        error_type="",
        error_message="",
        error_details=None,
    ):
        self.status = self.Status.FAILED
        self.failed_at = timezone.now()
        self.error_code = error_code
        self.error_type = error_type
        self.error_message = str(error_message)[:2000]
        self.error_details = error_details or {}
        self.save(update_fields=[
            "status",
            "failed_at",
            "error_code",
            "error_type",
            "error_message",
            "error_details",
            "updated_at",
        ])