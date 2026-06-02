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
    "password_recovery": EmailTemplate(
        subject="Recuperação de senha - Avaliza",
        template="password_recovery",
    ),
    "password_changed": EmailTemplate(
        subject="Senha alterada - Avaliza",
        template="password_changed",
    ),
    "new_login_alert": EmailTemplate(
        subject="Novo acesso detectado - Avaliza",
        template="new_login_alert",
    ),
}