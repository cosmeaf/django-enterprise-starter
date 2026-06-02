from django.db import models

class EmailLog(models.Model):
    subject = models.CharField(max_length=255)
    template_key = models.CharField(max_length=100)
    from_email = models.EmailField()
    to = models.JSONField(default=list)
    cc = models.JSONField(default=list, blank=True)
    bcc = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, default="pending")
    mode = models.CharField(max_length=20, default="auto")
    task_id = models.CharField(max_length=255, blank=True)
    error_type = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "email_log"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} - {self.status}"