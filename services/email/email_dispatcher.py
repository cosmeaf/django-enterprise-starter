import logging

from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

from services.email.error_handler import EmailErrorHandler
from services.models import EmailLog

logger = logging.getLogger("services.email")


class EmailDispatcher:
    @staticmethod
    def dispatch(payload, email_log_id=None):
        email_log = None

        if email_log_id:
            email_log = EmailLog.objects.filter(id=email_log_id).first()

        try:
            if email_log:
                email_log.attempts += 1
                email_log.status = "pending"
                email_log.save(update_fields=["attempts", "status", "updated_at"])

            message = EmailMultiAlternatives(
                subject=payload["subject"],
                body=payload["text"],
                from_email=payload["from_email"],
                to=payload["to"],
                cc=payload.get("cc", []),
                bcc=payload.get("bcc", []),
            )

            html = payload.get("html")
            if html:
                message.attach_alternative(html, "text/html")

            sent = message.send(fail_silently=False)

            if email_log:
                email_log.status = "sent"
                email_log.sent_at = timezone.now()
                email_log.error_type = ""
                email_log.error_message = ""
                email_log.error_details = {}
                email_log.save(
                    update_fields=[
                        "status",
                        "sent_at",
                        "error_type",
                        "error_message",
                        "error_details",
                        "updated_at",
                    ]
                )

            logger.info(
                "E-mail enviado com sucesso.",
                extra={"email_log_id": email_log_id},
            )

            return {
                "status": "sent",
                "sent": sent,
                "email_log_id": email_log_id,
            }

        except Exception as exc:
            error_type, error_message, error_details = EmailErrorHandler.classify(exc)

            if email_log:
                email_log.status = "failed"
                email_log.error_type = error_type
                email_log.error_message = error_message
                email_log.error_details = error_details
                email_log.save(
                    update_fields=[
                        "status",
                        "error_type",
                        "error_message",
                        "error_details",
                        "updated_at",
                    ]
                )

            logger.exception(
                "Falha ao enviar e-mail.",
                extra={
                    "email_log_id": email_log_id,
                    "error_type": error_type,
                },
            )

            raise