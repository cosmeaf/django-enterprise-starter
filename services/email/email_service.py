import logging

from django.conf import settings
from rest_framework.exceptions import ValidationError

from services.email.email_dispatcher import EmailDispatcher
from services.email.email_renderer import EmailRenderer
from services.email.registry import EMAIL_TEMPLATES
from services.models import EmailLog

logger = logging.getLogger("services.email")


class EmailService:
    @classmethod
    def send(cls, *, template_key, to, context=None, cc=None, bcc=None, mode=None):
        if template_key not in EMAIL_TEMPLATES:
            raise ValidationError(f"Template de e-mail inválido: {template_key}")

        if isinstance(to, str):
            to = [to]

        cc = cc or []
        bcc = bcc or []
        context = context or {}

        template = EMAIL_TEMPLATES[template_key]
        text, html = EmailRenderer.render(template.template, context)

        delivery_mode = mode or getattr(settings, "EMAIL_DELIVERY_MODE", "sync")
        delivery_mode = delivery_mode.lower().strip()

        payload = {
            "subject": template.subject,
            "text": text,
            "html": html,
            "from_email": settings.DEFAULT_FROM_EMAIL,
            "to": to,
            "cc": cc,
            "bcc": bcc,
            "template_key": template_key,
        }

        email_log = EmailLog.objects.create(
            subject=template.subject,
            template_key=template_key,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to,
            cc=cc,
            bcc=bcc,
            status="pending",
            mode=delivery_mode,
        )

        if delivery_mode == "sync":
            return EmailDispatcher.dispatch(
                payload=payload,
                email_log_id=email_log.id,
            )

        if delivery_mode == "async":
            return cls.send_async(
                payload=payload,
                email_log_id=email_log.id,
            )

        if delivery_mode == "auto":
            return cls.send_auto(
                payload=payload,
                email_log_id=email_log.id,
            )

        raise ValidationError("EMAIL_DELIVERY_MODE inválido. Use: sync, async ou auto.")

    @staticmethod
    def send_async(payload, email_log_id):
        from services.email.tasks import send_email_task

        task = send_email_task.delay(payload, email_log_id)

        EmailLog.objects.filter(id=email_log_id).update(
            task_id=task.id,
            status="pending",
        )

        return {
            "queued": True,
            "task_id": task.id,
            "email_log_id": email_log_id,
        }

    @staticmethod
    def send_auto(payload, email_log_id):
        try:
            return EmailService.send_async(
                payload=payload,
                email_log_id=email_log_id,
            )

        except Exception:
            logger.exception(
                "Celery indisponível. Enviando e-mail em modo sync.",
                extra={"email_log_id": email_log_id},
            )

            return EmailDispatcher.dispatch(
                payload=payload,
                email_log_id=email_log_id,
            )