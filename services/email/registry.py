from dataclasses import dataclass


@dataclass(frozen=True)
class EmailTemplate:
    subject: str
    template: str


EMAIL_TEMPLATES = {

    # ==========================
    # AUTH
    # ==========================

    "welcome": EmailTemplate(
        subject="Bem-vindo ao Avaliza",
        template="auth/welcome",
    ),

    "email_verification": EmailTemplate(
        subject="Verifique seu e-mail - Avaliza",
        template="auth/email_verification",
    ),

    "email_verified": EmailTemplate(
        subject="E-mail confirmado - Avaliza",
        template="auth/email_verified",
    ),

    "password_recovery": EmailTemplate(
        subject="Recuperação de senha - Avaliza",
        template="auth/password_recovery",
    ),

    "password_changed": EmailTemplate(
        subject="Senha alterada - Avaliza",
        template="auth/password_changed",
    ),

    "password_reset_success": EmailTemplate(
        subject="Senha redefinida com sucesso - Avaliza",
        template="auth/password_reset_success",
    ),

    "otp_code": EmailTemplate(
        subject="Seu código de verificação - Avaliza",
        template="auth/otp_code",
    ),

    # ==========================
    # LOGIN / SEGURANÇA
    # ==========================

    "new_login_alert": EmailTemplate(
        subject="Novo acesso detectado - Avaliza",
        template="security/new_login_alert",
    ),

    "new_device_login": EmailTemplate(
        subject="Novo dispositivo conectado - Avaliza",
        template="security/new_device_login",
    ),

    "failed_login_attempts": EmailTemplate(
        subject="Tentativas de acesso detectadas - Avaliza",
        template="security/failed_login_attempts",
    ),

    "suspicious_login": EmailTemplate(
        subject="Atividade suspeita detectada - Avaliza",
        template="security/suspicious_login",
    ),

    "security_alert": EmailTemplate(
        subject="Alerta de segurança - Avaliza",
        template="security/security_alert",
    ),

    "account_locked": EmailTemplate(
        subject="Conta bloqueada - Avaliza",
        template="security/account_locked",
    ),

    "account_unlocked": EmailTemplate(
        subject="Conta desbloqueada - Avaliza",
        template="security/account_unlocked",
    ),

    "email_changed": EmailTemplate(
        subject="Alteração de e-mail - Avaliza",
        template="security/email_changed",
    ),

    # ==========================
    # USUÁRIOS
    # ==========================

    "invite_user": EmailTemplate(
        subject="Você foi convidado para o Avaliza",
        template="users/invite_user",
    ),

    "user_invited": EmailTemplate(
        subject="Convite enviado - Avaliza",
        template="users/user_invited",
    ),

    "user_activated": EmailTemplate(
        subject="Usuário ativado - Avaliza",
        template="users/user_activated",
    ),

    "user_deactivated": EmailTemplate(
        subject="Usuário desativado - Avaliza",
        template="users/user_deactivated",
    ),

    "role_changed": EmailTemplate(
        subject="Permissão atualizada - Avaliza",
        template="users/role_changed",
    ),

    # ==========================
    # SUPORTE
    # ==========================

    "ticket_created": EmailTemplate(
        subject="Chamado aberto - Avaliza",
        template="support/ticket_created",
    ),

    "ticket_updated": EmailTemplate(
        subject="Chamado atualizado - Avaliza",
        template="support/ticket_updated",
    ),

    "ticket_closed": EmailTemplate(
        subject="Chamado encerrado - Avaliza",
        template="support/ticket_closed",
    ),

    # ==========================
    # SISTEMA
    # ==========================

    "notification": EmailTemplate(
        subject="Notificação - Avaliza",
        template="system/notification",
    ),

    "announcement": EmailTemplate(
        subject="Comunicado - Avaliza",
        template="system/announcement",
    ),

    "maintenance_notice": EmailTemplate(
        subject="Manutenção programada - Avaliza",
        template="system/maintenance_notice",
    ),

    "maintenance_finished": EmailTemplate(
        subject="Manutenção concluída - Avaliza",
        template="system/maintenance_finished",
    ),
}