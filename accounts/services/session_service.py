import hashlib

from accounts.models.user_session import UserSession


class SessionService:

    @staticmethod
    def build_device_hash(ctx):
        raw = "|".join([
            str(ctx.get("ip", "")),
            str(ctx.get("browser", "")),
            str(ctx.get("os", "")),
            str(ctx.get("device", "")),
        ])
        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def create(user, jti, ctx, request):
        device_hash = SessionService.build_device_hash(ctx)

        return UserSession.objects.create(
            user=user,
            token_jti=jti,
            device_hash=device_hash,
            ip_address=ctx.get("ip"),
            browser=ctx.get("browser"),
            os=ctx.get("os"),
            device=ctx.get("device"),
            risk_score=ctx.get("risk_score", 0),
        )