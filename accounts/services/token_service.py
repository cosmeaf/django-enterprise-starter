from rest_framework_simplejwt.tokens import RefreshToken


class TokenService:
    @staticmethod
    def create(user, session_id=None):
        refresh = RefreshToken.for_user(user)

        refresh["user_id"] = user.id
        refresh["email"] = user.email

        if session_id:
            refresh["session_id"] = str(session_id)

        access = refresh.access_token

        access["user_id"] = user.id
        access["email"] = user.email

        if session_id:
            access["session_id"] = str(session_id)

        return {
            "access": str(access),
            "refresh": str(refresh),
            "jti": str(refresh["jti"]),
        }