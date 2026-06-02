from django.contrib.auth.models import Group, User
from django.db import transaction

from accounts.dto.user_dto import UserDTO
from services.email.email_service import EmailService


class RegisterService:
    @staticmethod
    @transaction.atomic
    def register(data):
        email = data["email"].lower().strip()
        group_name = data.get("group", "user").lower().strip()

        user = User.objects.create_user(
            username=email,
            email=email,
            password=data["password"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            is_active=data.get("is_active", True),
            is_staff=data.get("is_staff", False),
        )

        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)

        if group_name == "admin":
            user.is_staff = True
            user.save(update_fields=["is_staff"])

        EmailService.send(
            template_key="welcome",
            to=[user.email],
            context={
                "user": user,
            },
        )

        return UserDTO.build(user)