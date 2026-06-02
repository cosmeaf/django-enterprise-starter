from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from accounts.serializers.register import RegisterSerializer
from accounts.services.register_service import RegisterService

class RegisterViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = RegisterSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = RegisterService.register(serializer.validated_data)
        return Response(result, status=status.HTTP_201_CREATED)