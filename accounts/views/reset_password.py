from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from accounts.serializers.reset_password import ResetPasswordSerializer
from accounts.services.password_service import PasswordService

class ResetPasswordViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        PasswordService.reset(serializer.validated_data["token"], serializer.validated_data["password"])
        return Response({"detail": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)