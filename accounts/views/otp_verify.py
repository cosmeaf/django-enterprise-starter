from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from accounts.serializers.otp_verify import OtpVerifySerializer
from accounts.services.otp_service import OTPService

class OtpVerifyViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    serializer_class = OtpVerifySerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = OTPService.verify(serializer.validated_data["email"], serializer.validated_data["code"])
        return Response(result, status=status.HTTP_200_OK)