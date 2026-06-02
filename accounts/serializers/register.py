from django.contrib.auth.models import User
from rest_framework import serializers
import re


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        required=False, 
        allow_blank=True,
        max_length=150
    )
    last_name = serializers.CharField(
        required=False, 
        allow_blank=True,
        max_length=150
    )
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    group = serializers.CharField(required=False, default="user")
    is_staff = serializers.BooleanField(required=False, default=False)
    is_active = serializers.BooleanField(required=False, default=True)

    # ==================== VALIDAÇÕES AVANÇADAS ====================

    def validate_email(self, value):
        """Validação rigorosa de email"""
        email = value.lower().strip()
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise serializers.ValidationError("Formato de e-mail inválido.")
        
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Este e-mail já está cadastrado.")
        
        return email

    def validate_first_name(self, value):
        if value:
            value = value.strip()
            if len(value) < 2:
                raise serializers.ValidationError("O nome deve ter pelo menos 2 caracteres.")
            if not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]+$', value):
                raise serializers.ValidationError("Nome contém caracteres inválidos.")
        return value

    def validate_last_name(self, value):
        if value:
            value = value.strip()
            if len(value) < 2:
                raise serializers.ValidationError("O sobrenome deve ter pelo menos 2 caracteres.")
        return value

    def validate_group(self, value):
        value = value.lower().strip()
        allowed_groups = ["admin", "staff", "user"]
        
        if value not in allowed_groups:
            raise serializers.ValidationError(
                "Grupo inválido. Use: admin, staff ou user."
            )
        return value

    def validate_password(self, value):
        """Validação forte de senha (padrão enterprise)"""
        if len(value) < 8:
            raise serializers.ValidationError("A senha deve ter no mínimo 8 caracteres.")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra maiúscula.")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra minúscula.")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("A senha deve conter pelo menos um número.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError(
                "A senha deve conter pelo menos um caractere especial (!@#$%^&*...)"
            )
        
        # Check for common passwords (opcional - pode expandir)
        common_passwords = {'12345678', 'password123', 'qwerty123', 'admin123'}
        if value.lower() in common_passwords:
            raise serializers.ValidationError("Esta senha é muito comum. Escolha uma mais segura.")
        
        return value

    def validate(self, attrs):
        """Validação cruzada"""
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({
                "password": "As senhas não coincidem.",
                "password2": "As senhas não coincidem."
            })

        # Segurança: não permitir criar admin facilmente via API
        if attrs.get('is_staff') and attrs.get('group') != 'admin':
            raise serializers.ValidationError({
                "is_staff": "Apenas usuários do grupo 'admin' podem ter is_staff=True."
            })

        # Evitar criar superuser por esta rota (recomendado)
        if attrs.get('group') == 'admin' and not attrs.get('is_staff'):
            attrs['is_staff'] = True  # força consistência

        return attrs

    def to_representation(self, instance):
        """Resposta limpa após criação"""
        return {
            "message": "Usuário cadastrado com sucesso!",
            "email": instance.email,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "group": getattr(instance, 'group', 'user')
        }