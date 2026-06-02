from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.exceptions import ValidationError
from accounts.models.otp_code import OtpCode
from accounts.models.reset_password_token import ResetPasswordToken
from accounts.services.url_service import UrlService

class OTPService:
    @staticmethod
    def verify(email, code):
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            raise ValidationError("Código inválido ou e-mail não encontrado.")
        otp = OtpCode.objects.filter(user=user, is_used=False).order_by("-created_at").first()
        if not otp:
            raise ValidationError("Código não encontrado.")
        if not otp.verify(code):
            raise ValidationError("Código inválido ou expirado.")
        with transaction.atomic():
            reset_token = ResetPasswordToken.objects.create(user=user)
        reset_url = UrlService.reset_password_url(reset_token.token)
        return {"reset_token": str(reset_token.token), "reset_url": reset_url, "expires_in": 3600}