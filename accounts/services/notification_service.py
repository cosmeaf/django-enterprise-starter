from services.email.email_service import EmailService


class NotificationService:
    @staticmethod
    def new_login_alert(user, session, ctx):
        EmailService.send(
            template_key="new_login_alert",
            to=[user.email],
            context={
                "user": user,
                "session": session,
                "ctx": ctx,
            },
        )