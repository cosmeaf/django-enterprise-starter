from rest_framework import serializers

class OtpVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)

    def validate_email(self, value):
        return value.lower().strip()