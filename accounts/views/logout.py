from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import UserSession
from accounts.serializers.empty import EmptySerializer


class LogoutViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer

    def create(self, request):
        refresh_token = request.data.get("refresh")

        session_id = request.auth.get("session_id") if request.auth else None
        jti = request.auth.get("jti") if request.auth else None

        if session_id:
            UserSession.objects.filter(
                id=session_id,
                user=request.user,
                is_active=True,
            ).update(
                is_active=False,
                revoked_at=timezone.now(),
            )
        elif jti:
            UserSession.objects.filter(
                token_jti=jti,
                user=request.user,
                is_active=True,
            ).update(
                is_active=False,
                revoked_at=timezone.now(),
            )

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                return Response(
                    {"detail": "Refresh token inválido ou já revogado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"detail": "Logout realizado com sucesso."},
            status=status.HTTP_200_OK,
        )