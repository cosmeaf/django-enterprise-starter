from dataclasses import dataclass


@dataclass(frozen=True)
class EmailTemplate:
    subject: str
    template: str


EMAIL_TEMPLATES = {
    "welcome": EmailTemplate(
        subject="Bem-vindo ao Avaliza",
        template="welcome",
    ),

    "email_verification": EmailTemplate(
        subject="Verifique seu e-mail - Avaliza",
        template="email_verification",
    ),

    "email_verified": EmailTemplate(
        subject="E-mail verificado com sucesso - Avaliza",
        template="email_verified",
    ),

    "password_recovery": EmailTemplate(
        subject="Recuperação de senha - Avaliza",
        template="password_recovery",
    ),

    "password_changed": EmailTemplate(
        subject="Senha alterada - Avaliza",
        template="password_changed",
    ),

    "password_reset_success": EmailTemplate(
        subject="Senha redefinida com sucesso - Avaliza",
        template="password_reset_success",
    ),

    "otp_code": EmailTemplate(
        subject="Seu código de verificação - Avaliza",
        template="otp_code",
    ),

    "new_login_alert": EmailTemplate(
        subject="Novo acesso detectado - Avaliza",
        template="new_login_alert",
    ),

    "new_device_login": EmailTemplate(
        subject="Novo dispositivo conectado - Avaliza",
        template="new_device_login",
    ),

    "failed_login_attempts": EmailTemplate(
        subject="Tentativas de acesso detectadas - Avaliza",
        template="failed_login_attempts",
    ),

    "suspicious_login": EmailTemplate(
        subject="Atividade suspeita detectada - Avaliza",
        template="suspicious_login",
    ),

    "security_alert": EmailTemplate(
        subject="Alerta de segurança - Avaliza",
        template="security_alert",
    ),

    "account_locked": EmailTemplate(
        subject="Conta bloqueada - Avaliza",
        template="account_locked",
    ),

    "account_unlocked": EmailTemplate(
        subject="Conta desbloqueada - Avaliza",
        template="account_unlocked",
    ),

    "email_changed": EmailTemplate(
        subject="Alteração de e-mail - Avaliza",
        template="email_changed",
    ),

    "invite_user": EmailTemplate(
        subject="Convite para acessar o Avaliza",
        template="invite_user",
    ),

    "user_invited": EmailTemplate(
        subject="Convite enviado - Avaliza",
        template="user_invited",
    ),

    "user_activated": EmailTemplate(
        subject="Usuário ativado - Avaliza",
        template="user_activated",
    ),

    "user_deactivated": EmailTemplate(
        subject="Usuário desativado - Avaliza",
        template="user_deactivated",
    ),

    "role_changed": EmailTemplate(
        subject="Permissões atualizadas - Avaliza",
        template="role_changed",
    ),

    "ticket_created": EmailTemplate(
        subject="Chamado criado - Avaliza",
        template="ticket_created",
    ),

    "ticket_updated": EmailTemplate(
        subject="Chamado atualizado - Avaliza",
        template="ticket_updated",
    ),

    "ticket_closed": EmailTemplate(
        subject="Chamado encerrado - Avaliza",
        template="ticket_closed",
    ),

    "notification": EmailTemplate(
        subject="Notificação - Avaliza",
        template="notification",
    ),

    "announcement": EmailTemplate(
        subject="Comunicado - Avaliza",
        template="announcement",
    ),

    "maintenance_notice": EmailTemplate(
        subject="Manutenção programada - Avaliza",
        template="maintenance_notice",
    ),

    "maintenance_finished": EmailTemplate(
        subject="Manutenção concluída - Avaliza",
        template="maintenance_finished",
    ),
}