import logging

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

from accounts.dto.user_dto import UserDTO
from accounts.services.context_service import ContextService
from accounts.services.login_audit_service import LoginAuditService
from accounts.services.notification_service import NotificationService
from accounts.services.security_service import SecurityService
from accounts.services.session_service import SessionService
from accounts.services.token_service import TokenService

logger = logging.getLogger(__name__)


class AuthService:
    FAILURE_USER_NOT_FOUND = "user_not_found"
    FAILURE_INVALID_PASSWORD = "invalid_password"
    FAILURE_INACTIVE_USER = "inactive_user"

    @staticmethod
    def login(email: str, password: str, request):
        email = (email or "").lower().strip()

        if not email or not password:
            raise ValidationError("E-mail e senha são obrigatórios.")

        ctx = ContextService.get_context(request)
        ip = ctx.get("ip")
        user_agent = ctx.get("user_agent")

        SecurityService.check_login_allowed(email, ip)

        user_obj = User.objects.filter(email__iexact=email).first()

        if not user_obj:
            AuthService._handle_login_failure(
                email=email,
                ip=ip,
                user_agent=user_agent,
                user=None,
                reason=AuthService.FAILURE_USER_NOT_FOUND,
                request=request,
            )
            raise ValidationError("Credenciais inválidas.")

        user = authenticate(
            request=request,
            username=user_obj.username,
            password=password,
        )

        if not user:
            AuthService._handle_login_failure(
                email=email,
                ip=ip,
                user_agent=user_agent,
                user=user_obj,
                reason=AuthService.FAILURE_INVALID_PASSWORD,
                request=request,
            )
            raise ValidationError("Credenciais inválidas.")

        if not user.is_active:
            AuthService._handle_login_failure(
                email=email,
                ip=ip,
                user_agent=user_agent,
                user=user,
                reason=AuthService.FAILURE_INACTIVE_USER,
                request=request,
            )
            raise ValidationError("Conta desativada.")

        tmp_tokens = TokenService.create(
            user=user,
            session_id=None,
        )

        session = SessionService.create(
            user=user,
            jti=tmp_tokens["jti"],
            ctx=ctx,
            request=request,
        )

        tokens = TokenService.create(
            user=user,
            session_id=session.id,
        )

        session.token_jti = tokens["jti"]
        session.save(update_fields=["token_jti"])

        SecurityService.register_attempt(
            email=email,
            ip=ip,
            user_agent=user_agent,
            success=True,
            reason="success",
        )

        LoginAuditService.register(
            request=request,
            user=user,
            success=True,
            session=session,
            token_jti=tokens["jti"],
        )

        if getattr(settings, "LOGIN_ALERT_ENABLED", True):
            try:
                NotificationService.new_login_alert(
                    user=user,
                    session=session,
                    ctx=ctx,
                )
            except Exception:
                logger.exception("Falha ao enviar alerta de novo login.")

        return {
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "session": {
                "id": str(session.id),
            },
            "user": UserDTO.build(user),
        }

    @staticmethod
    def _handle_login_failure(email, ip, user_agent, user, reason, request):
        SecurityService.register_attempt(
            email=email,
            ip=ip,
            user_agent=user_agent,
            success=False,
            reason=reason,
        )

        LoginAuditService.register(
            request=request,
            user=user,
            success=False,
        )

        logger.warning(
            "Tentativa de login falhou",
            extra={
                "email": email,
                "ip": ip,
                "reason": reason,
                "user_id": getattr(user, "id", None),
            },
        )