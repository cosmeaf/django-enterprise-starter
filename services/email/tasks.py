import logging

from celery import shared_task

from services.email.email_dispatcher import EmailDispatcher
from services.models import EmailLog

logger = logging.getLogger("services.email")


@shared_task(
    bind=True,
    name="services.email.tasks.send_email_task",
    max_retries=3,
    default_retry_delay=60,
)
def send_email_task(self, payload, email_log_id):
    try:
        EmailLog.objects.filter(id=email_log_id).update(
            status="retry" if self.request.retries else "pending",
            task_id=self.request.id,
        )

        return EmailDispatcher.dispatch(
            payload=payload,
            email_log_id=email_log_id,
        )

    except Exception as exc:
        logger.warning(
            "Retry de email",
            extra={
                "email_log_id": email_log_id,
                "retry": self.request.retries,
            },
        )

        raise self.retry(exc=exc)