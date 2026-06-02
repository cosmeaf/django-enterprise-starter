from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from accounts.serializers.recovery import RecoverySerializer
from accounts.services.recovery_service import RecoveryService

class RecoveryViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    serializer_class = RecoverySerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        RecoveryService.send_otp(serializer.validated_data["email"])
        return Response({"detail": "Código enviado, se o e-mail existir."}, status=status.HTTP_200_OK)