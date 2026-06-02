from accounts.dto.user_dto import UserDTO
from accounts.models.user_session import UserSession


class SessionReaderService:
    @staticmethod
    def get_current_session(request):
        session_id = request.auth.get("session_id") if request.auth else None

        if not session_id:
            return None

        return UserSession.objects.filter(
            id=session_id,
            user=request.user,
            is_active=True,
        ).first()

    @staticmethod
    def build_me(request):
        session = SessionReaderService.get_current_session(request)

        return {
            "user": UserDTO.build(request.user),
            "session": SessionReaderService.session_payload(session),
        }

    @staticmethod
    def session_payload(session):
        if not session:
            return None

        return {
            "id": str(session.id),
            "ip_address": session.ip_address,
            "browser": session.browser,
            "os": session.os,
            "device": session.device,
            "risk_score": session.risk_score,
            "created_at": session.created_at,
            "last_seen": session.last_seen,
            "is_active": session.is_active,
        }