from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models.otp_code import OtpCode
from services.email.email_service import EmailService

class RecoveryService:
    @staticmethod
    def send_otp(email):
        email = email.lower().strip()
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return
        recent = OtpCode.objects.filter(user=user, created_at__gte=timezone.now() - timedelta(seconds=60)).exists()
        if recent:
            return
        otp_obj, otp_code = OtpCode.create_code(user)
        EmailService.send(template_key="password_recovery", to=[user.email], context={"user": user, "otp_code": otp_code})