from rest_framework.exceptions import ValidationError
from accounts.models.reset_password_token import ResetPasswordToken
from services.email.email_service import EmailService

class PasswordService:
    @staticmethod
    def reset(token, password):
        token_obj = ResetPasswordToken.objects.filter(token=token).first()
        if not token_obj:
            raise ValidationError("Token inválido.")
        if not token_obj.is_valid():
            raise ValidationError("Token expirado ou já utilizado.")
        user = token_obj.user
        user.set_password(password)
        user.save(update_fields=["password"])
        token_obj.is_used = True
        token_obj.save(update_fields=["is_used"])
        EmailService.send(template_key="password_changed", to=[user.email], context={"user": user})