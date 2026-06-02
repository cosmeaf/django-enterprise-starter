from django.contrib.auth.models import User
from django.db import models

class LoginEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    browser = models.CharField(max_length=100, null=True, blank=True)
    os = models.CharField(max_length=100, null=True, blank=True)
    device = models.CharField(max_length=50, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    token_jti = models.CharField(max_length=255, null=True, blank=True)
    risk_score = models.IntegerField(default=0)
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "login_event"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} | {self.ip} | {self.success}"