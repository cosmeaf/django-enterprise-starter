from django.db import models

class LoginAttempt(models.Model):
    email = models.EmailField(db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=False)
    reason = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "login_attempt"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} - {self.ip_address} - {self.success}"