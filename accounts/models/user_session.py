import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    token_jti = models.CharField(max_length=255, unique=True)
    device_hash = models.CharField(max_length=64, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    browser = models.CharField(max_length=100, null=True, blank=True)
    os = models.CharField(max_length=100, null=True, blank=True)
    device = models.CharField(max_length=50, null=True, blank=True)
    risk_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(default=timezone.now)
    revoked_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "user_session"
        ordering = ["-created_at"]

    def revoke(self):
        if not self.is_active:
            return
        self.is_active = False
        self.revoked_at = timezone.now()
        self.save(update_fields=["is_active", "revoked_at"])