from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from accounts.models.login_attempt import LoginAttempt

class SecurityService:
    @staticmethod
    def register_attempt(email, ip, user_agent, success, reason=""):
        return LoginAttempt.objects.create(email=(email or "").lower().strip(), ip_address=ip, user_agent=user_agent or "", success=success, reason=reason)

    @staticmethod
    def check_login_allowed(email, ip):
        since = timezone.now() - timedelta(minutes=settings.LOGIN_LOCK_MINUTES)
        failures = LoginAttempt.objects.filter(email=(email or "").lower().strip(), ip_address=ip, success=False, created_at__gte=since).count()
        if failures >= settings.LOGIN_MAX_ATTEMPTS:
            raise ValidationError(f"Muitas tentativas de login. Tente novamente em {settings.LOGIN_LOCK_MINUTES} minutos.")