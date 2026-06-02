import logging
import smtplib
from typing import Any, Dict, List, Optional

from celery.exceptions import CeleryError
from django.conf import settings
from django.db import transaction
from django.template.base import VariableDoesNotExist

from services.email.email_dispatcher import EmailDispatcher
from services.email.email_renderer import EmailRenderer
from services.email.registry import EMAIL_TEMPLATES
from services.models import EmailLog

logger = logging.getLogger("services.email")


class EmailServiceError(Exception):
    code = "EMAIL_SERVICE_ERROR"
    message = "Erro no serviço de e-mail."

    def __init__(self, message=None, code=None, details=None):
        self.message = message or self.message
        self.code = code or self.code
        self.details = details or {}
        super().__init__(self.message)


class EmailTemplateError(EmailServiceError):
    code = "EMAIL_TEMPLATE_RENDER_ERROR"
    message = "Erro ao renderizar template de e-mail."


class EmailSMTPError(EmailServiceError):
    code = "EMAIL_SMTP_ERROR"
    message = "Erro SMTP ao enviar e-mail."


class EmailCeleryError(EmailServiceError):
    code = "EMAIL_CELERY_ERROR"
    message = "Erro ao enfileirar e-mail no Celery."


class EmailService:

    @classmethod
    def send(
        cls,
        *,
        template_key: str,
        to: List[str] | str,
        context: Optional[Dict[str, Any]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        mode: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        email_log = None
        normalized_to = to

        try:
            cls._validate_inputs(template_key, to)

            normalized_to = [to] if isinstance(to, str) else to
            cc = cc or []
            bcc = bcc or []
            context = context or {}
            metadata = metadata or {}

            template = EMAIL_TEMPLATES[template_key]
            delivery_mode = cls._get_delivery_mode(mode)

            text, html = cls._render_template_safe(
                template_path=template.template,
                context=context,
            )

            with transaction.atomic():
                email_log = EmailLog.objects.create(
                    subject=template.subject,
                    template_key=template_key,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=normalized_to,
                    cc=cc,
                    bcc=bcc,
                    status=EmailLog.Status.PENDING,
                    mode=delivery_mode,
                    metadata=metadata,
                )

                payload = {
                    "subject": template.subject,
                    "text": text,
                    "html": html,
                    "from_email": settings.DEFAULT_FROM_EMAIL,
                    "to": normalized_to,
                    "cc": cc,
                    "bcc": bcc,
                    "template_key": template_key,
                    "email_log_id": email_log.id,
                }

                if delivery_mode == "sync":
                    return cls._send_sync(payload, email_log)

                if delivery_mode == "async":
                    return cls._send_async(payload, email_log)

                return cls._send_auto(payload, email_log)

        except EmailServiceError as e:
            cls._handle_expected_error(
                exception=e,
                email_log=email_log,
                template_key=template_key,
                to=normalized_to,
            )
            return cls._error_response(e, email_log)

        except Exception as e:
            wrapped = EmailServiceError(
                code="EMAIL_UNEXPECTED_ERROR",
                message="Erro inesperado no envio de e-mail.",
                details={
                    "exception_type": type(e).__name__,
                    "exception": str(e),
                },
            )

            cls._handle_unexpected_error(
                exception=e,
                email_log=email_log,
                template_key=template_key,
                to=normalized_to,
            )

            return cls._error_response(wrapped, email_log)

    @staticmethod
    def _validate_inputs(template_key: str, to: Any):
        if template_key not in EMAIL_TEMPLATES:
            raise EmailServiceError(
                code="EMAIL_TEMPLATE_NOT_FOUND",
                message=f"Template de e-mail inválido: {template_key}",
            )

        if not to:
            raise EmailServiceError(
                code="EMAIL_RECIPIENT_REQUIRED",
                message="Destinatário do e-mail é obrigatório.",
            )

    @staticmethod
    def _render_template_safe(template_path: str, context: Dict[str, Any]) -> tuple:
        try:
            return EmailRenderer.render(template_path, context)

        except VariableDoesNotExist as e:
            raise EmailTemplateError(
                message="Contexto insuficiente para renderizar o template de e-mail.",
                details={
                    "template": template_path,
                    "context_keys": list(context.keys()),
                    "missing_variable": str(e),
                },
            ) from e

        except Exception as e:
            raise EmailTemplateError(
                message="Falha ao renderizar template de e-mail.",
                details={
                    "template": template_path,
                    "context_keys": list(context.keys()),
                    "exception_type": type(e).__name__,
                    "exception": str(e),
                },
            ) from e

    @staticmethod
    def _get_delivery_mode(mode: Optional[str]) -> str:
        delivery_mode = (
            mode or getattr(settings, "EMAIL_DELIVERY_MODE", "auto")
        ).lower().strip()

        if delivery_mode not in {"sync", "async", "auto"}:
            logger.warning(
                "EMAIL_DELIVERY_MODE inválido. Usando auto.",
                extra={
                    "email_delivery_mode": delivery_mode,
                },
            )
            return "auto"

        return delivery_mode

    @classmethod
    def _send_sync(cls, payload: Dict[str, Any], email_log: EmailLog):
        try:
            email_log.mark_sending()

            result = EmailDispatcher.dispatch(
                payload=payload,
                email_log_id=email_log.id,
            )

            email_log.mark_sent()

            return {
                "success": True,
                "delivery_mode": "sync",
                "status": "sent",
                "email_log_id": email_log.id,
                "result": result,
            }

        except smtplib.SMTPAuthenticationError as e:
            smtp_response = str(e)

            error_code = "EMAIL_SMTP_AUTH_ERROR"
            error_message = "Falha de autenticação SMTP."

            if "Unauthorized IP address" in smtp_response:
                error_code = "EMAIL_SMTP_IP_NOT_AUTHORIZED"
                error_message = "IP não autorizado no provedor SMTP."

            raise EmailSMTPError(
                code=error_code,
                message=error_message,
                details={
                    "smtp_response": smtp_response,
                },
            ) from e

        except smtplib.SMTPServerDisconnected as e:
            raise EmailSMTPError(
                code="EMAIL_SMTP_DISCONNECTED",
                message="Servidor SMTP desconectou durante o envio.",
                details={
                    "exception": str(e),
                },
            ) from e

        except smtplib.SMTPConnectError as e:
            raise EmailSMTPError(
                code="EMAIL_SMTP_CONNECTION_ERROR",
                message="Falha ao conectar no servidor SMTP.",
                details={
                    "exception": str(e),
                },
            ) from e

        except smtplib.SMTPRecipientsRefused as e:
            raise EmailSMTPError(
                code="EMAIL_SMTP_RECIPIENTS_REFUSED",
                message="Destinatário recusado pelo servidor SMTP.",
                details={
                    "recipients": str(e.recipients),
                },
            ) from e

        except smtplib.SMTPSenderRefused as e:
            raise EmailSMTPError(
                code="EMAIL_SMTP_SENDER_REFUSED",
                message="Remetente recusado pelo servidor SMTP.",
                details={
                    "sender": str(e.sender),
                    "smtp_code": str(e.smtp_code),
                    "smtp_error": str(e.smtp_error),
                },
            ) from e

        except smtplib.SMTPException as e:
            raise EmailSMTPError(
                code="EMAIL_SMTP_ERROR",
                message="Erro SMTP ao enviar e-mail.",
                details={
                    "exception_type": type(e).__name__,
                    "exception": str(e),
                },
            ) from e

        except Exception as e:
            raise EmailSMTPError(
                code="EMAIL_SYNC_SEND_FAILED",
                message="Falha no envio síncrono de e-mail.",
                details={
                    "exception_type": type(e).__name__,
                    "exception": str(e),
                },
            ) from e

    @classmethod
    def _send_async(cls, payload: Dict[str, Any], email_log: EmailLog):
        try:
            from services.email.tasks import send_email_task

            task = send_email_task.delay(payload, email_log.id)
            email_log.mark_queued(task.id)

            return {
                "success": True,
                "delivery_mode": "async",
                "status": "queued",
                "task_id": task.id,
                "email_log_id": email_log.id,
            }

        except (ImportError, CeleryError) as e:
            raise EmailCeleryError(
                code="EMAIL_CELERY_UNAVAILABLE",
                message="Celery indisponível para envio assíncrono.",
                details={
                    "exception_type": type(e).__name__,
                    "exception": str(e),
                },
            ) from e

        except Exception as e:
            raise EmailCeleryError(
                code="EMAIL_ASYNC_QUEUE_FAILED",
                message="Falha ao enfileirar e-mail assíncrono.",
                details={
                    "exception_type": type(e).__name__,
                    "exception": str(e),
                },
            ) from e

    @classmethod
    def _send_auto(cls, payload: Dict[str, Any], email_log: EmailLog):
        try:
            return cls._send_async(payload, email_log)

        except EmailCeleryError:
            logger.warning(
                "Celery indisponível. Usando fallback síncrono.",
                extra={
                    "email_log_id": email_log.id,
                    "email_delivery_mode": "auto",
                },
            )

            return cls._send_sync(payload, email_log)

    @staticmethod
    def _handle_expected_error(
        *,
        exception: EmailServiceError,
        email_log: Optional[EmailLog],
        template_key: str,
        to: Any,
    ):
        if email_log:
            email_log.mark_failed(
                error_code=exception.code,
                error_type=type(exception).__name__,
                error_message=exception.message,
                error_details=exception.details,
            )

        logger.warning(
            f"[{exception.code}] {exception.message}",
            extra={
                "email_error_code": exception.code,
                "email_template_key": template_key,
                "email_to": to,
                "email_log_id": getattr(email_log, "id", None),
                "email_error_details": exception.details,
            },
        )

    @staticmethod
    def _handle_unexpected_error(
        *,
        exception: Exception,
        email_log: Optional[EmailLog],
        template_key: str,
        to: Any,
    ):
        if email_log:
            email_log.mark_failed(
                error_code="EMAIL_UNEXPECTED_ERROR",
                error_type=type(exception).__name__,
                error_message=str(exception),
                error_details={
                    "exception_type": type(exception).__name__,
                    "exception": str(exception),
                },
            )

        logger.exception(
            "Erro inesperado no envio de e-mail",
            extra={
                "email_template_key": template_key,
                "email_to": to,
                "email_log_id": getattr(email_log, "id", None),
                "email_error_type": type(exception).__name__,
            },
        )

    @staticmethod
    def _error_response(
        exception: EmailServiceError,
        email_log: Optional[EmailLog],
    ) -> Dict[str, Any]:
        return {
            "success": False,
            "code": exception.code,
            "message": exception.message,
            "details": exception.details,
            "email_log_id": getattr(email_log, "id", None),
        }