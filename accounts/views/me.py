from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.serializers.empty import EmptySerializer
from accounts.services.session_reader_service import SessionReaderService

class MeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EmptySerializer

    def list(self, request):
        return Response(SessionReaderService.build_me(request))