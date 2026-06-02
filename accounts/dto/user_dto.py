class UserDTO:
    @staticmethod
    def build(user):
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": UserDTO.role(user),
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "is_active": user.is_active,
            "groups": list(user.groups.values_list("name", flat=True)),
        }

    @staticmethod
    def role(user):
        if user.is_superuser:
            return "admin"

        if user.is_staff:
            return "staff"

        groups = list(user.groups.values_list("name", flat=True))

        if "admin" in groups:
            return "admin"

        if "staff" in groups:
            return "staff"

        return "user"