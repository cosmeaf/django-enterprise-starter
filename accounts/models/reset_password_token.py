import uuid
from datetime import timedelta
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class ResetPasswordToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reset_tokens")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reset_password_token"

    def is_valid(self):
        return not self.is_used and timezone.now() - self.created_at <= timedelta(hours=1)