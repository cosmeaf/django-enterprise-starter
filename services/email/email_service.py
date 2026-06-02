import logging
from typing import Any, Dict, List, Optional
from django.conf import settings
from django.db import transaction
from rest_framework.exceptions import ValidationError
from services.email.email_dispatcher import EmailDispatcher
from services.email.email_renderer import EmailRenderer
from services.email.registry import EMAIL_TEMPLATES
from services.models import EmailLog
from celery.exceptions import CeleryError  # se estiver usando Celery

logger = logging.getLogger("services.email")


class EmailServiceError(Exception):
    """Exceção base customizada para o serviço de email."""


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
        metadata: Optional[Dict[str, Any]] = None,  # para rastreabilidade
    ) -> Dict[str, Any]:
        
        email_log = None
        try:
            # === 1. Validação inicial ===
            cls._validate_inputs(template_key, to, mode)

            to = [to] if isinstance(to, str) else to
            cc = cc or []
            bcc = bcc or []
            context = context or {}
            metadata = metadata or {}

            template = EMAIL_TEMPLATES[template_key]

            # === 2. Renderização com tratamento ===
            text, html = cls._render_template_safe(template.template, context)

            delivery_mode = cls._get_delivery_mode(mode)

            # === 3. Criação do log em transação ===
            with transaction.atomic():
                email_log = EmailLog.objects.create(
                    subject=template.subject,
                    template_key=template_key,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=to,
                    cc=cc,
                    bcc=bcc,
                    status="pending",
                    mode=delivery_mode,
                    metadata=metadata,  # campo JSONField recomendado
                )

                payload = {
                    "subject": template.subject,
                    "text": text,
                    "html": html,
                    "from_email": settings.DEFAULT_FROM_EMAIL,
                    "to": to,
                    "cc": cc,
                    "bcc": bcc,
                    "template_key": template_key,
                    "email_log_id": email_log.id,
                }

                # === 4. Decisão de envio ===
                if delivery_mode == "sync":
                    return cls._send_sync(payload, email_log.id)
                elif delivery_mode == "async":
                    return cls._send_async(payload, email_log.id)
                elif delivery_mode == "auto":
                    return cls._send_auto(payload, email_log.id)
                else:
                    raise ValidationError(f"EMAIL_DELIVERY_MODE inválido: {delivery_mode}")

        except Exception as e:
            cls._handle_critical_error(e, email_log, template_key, to)
            raise

    # ======================= MÉTODOS PRIVADOS =======================

    @staticmethod
    def _validate_inputs(template_key: str, to: Any, mode: Optional[str]):
        if template_key not in EMAIL_TEMPLATES:
            raise ValidationError(f"Template de e-mail inválido: {template_key}")

        if not to:
            raise ValidationError("Destinatário (to) é obrigatório.")

    @staticmethod
    def _render_template_safe(template: str, context: Dict) -> tuple:
        try:
            return EmailRenderer.render(template, context)
        except Exception as e:
            logger.error("Falha ao renderizar template", 
                        extra={"template": template, "error": str(e)},
                        exc_info=True)
            raise EmailServiceError(f"Erro na renderização do template: {e}") from e

    @staticmethod
    def _get_delivery_mode(mode: Optional[str]) -> str:
        mode = (mode or getattr(settings, "EMAIL_DELIVERY_MODE", "auto")).lower().strip()
        if mode not in {"sync", "async", "auto"}:
            logger.warning(f"Modo inválido '{mode}', usando 'auto'")
            return "auto"
        return mode

    @classmethod
    def _send_sync(cls, payload: Dict, email_log_id: int):
        try:
            return EmailDispatcher.dispatch(payload=payload, email_log_id=email_log_id)
        except Exception as e:
            logger.error("Falha no envio síncrono", 
                        extra={"email_log_id": email_log_id}, exc_info=True)
            raise EmailServiceError("Falha no envio síncrono de email") from e

    @classmethod
    def _send_async(cls, payload: Dict, email_log_id: int):
        try:
            from services.email.tasks import send_email_task
            task = send_email_task.delay(payload, email_log_id)
            
            EmailLog.objects.filter(id=email_log_id).update(
                task_id=task.id,
                status="queued",
            )
            return {
                "queued": True,
                "task_id": task.id,
                "email_log_id": email_log_id,
            }
        except (ImportError, CeleryError, Exception) as e:
            logger.exception("Celery indisponível ou erro ao enfileirar tarefa",
                           extra={"email_log_id": email_log_id})
            raise EmailServiceError("Falha ao enfileirar email assíncrono") from e

    @classmethod
    def _send_auto(cls, payload: Dict, email_log_id: int):
        """Tenta async, fallback para sync se falhar."""
        try:
            return cls._send_async(payload, email_log_id)
        except Exception as e:
            logger.warning("Fallback para envio síncrono devido a falha no Celery",
                         extra={"email_log_id": email_log_id}, exc_info=False)
            return cls._send_sync(payload, email_log_id)

    @staticmethod
    def _handle_critical_error(
        exception: Exception,
        email_log: Optional[EmailLog],
        template_key: str,
        to: List[str]
    ):
        """Tratamento final de erro crítico - nível produção."""
        error_msg = str(exception)
        
        if email_log:
            email_log.status = "failed"
            email_log.error_message = error_msg[:500]
            email_log.save(update_fields=["status", "error_message"])

        logger.critical(
            "ERRO CRÍTICO NO ENVIO DE EMAIL",
            extra={
                "template_key": template_key,
                "to": to,
                "email_log_id": getattr(email_log, 'id', None),
                "error_type": type(exception).__name__,
            },
            exc_info=True
        )