from rest_framework import serializers

class BlockUserSerializer(serializers.Serializer):
    email = serializers.EmailField()