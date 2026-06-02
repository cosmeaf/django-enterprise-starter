from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from accounts.serializers.block_user import BlockUserSerializer

class BlockUserViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = BlockUserSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response({"detail": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        if user.is_superuser:
            return Response({"detail": "Não é permitido bloquear superusuário."}, status=status.HTTP_403_FORBIDDEN)
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response({"detail": "Usuário bloqueado com sucesso."}, status=status.HTTP_200_OK)