from accounts.models.login_event import LoginEvent
from accounts.services.context_service import ContextService


class LoginAuditService:
    @staticmethod
    def register(request, user, success, session=None, token_jti=None):
        ctx = ContextService.get_context(request)

        LoginEvent.objects.create(
            user=user,
            ip=ctx.get("ip"),
            browser=ctx.get("browser"),
            os=ctx.get("os"),
            device=ctx.get("device"),
            user_agent=ctx.get("user_agent"),
            session_id=str(session.id) if session else None,
            token_jti=token_jti,
            risk_score=ctx.get("risk_score", 0),
            success=success,
        )