import socket
import smtplib
import ssl

class EmailErrorHandler:
    @staticmethod
    def classify(exc):
        name = exc.__class__.__name__
        message = str(exc)

        if isinstance(exc, smtplib.SMTPAuthenticationError):
            return "smtp_authentication_error", "Falha de autenticação SMTP", {"exception": name, "message": message}

        if isinstance(exc, smtplib.SMTPConnectError):
            return "smtp_connection_error", "Falha ao conectar no servidor SMTP", {"exception": name, "message": message}

        if isinstance(exc, smtplib.SMTPServerDisconnected):
            return "smtp_disconnected", "Servidor SMTP desconectou inesperadamente", {"exception": name, "message": message}

        if isinstance(exc, smtplib.SMTPRecipientsRefused):
            return "smtp_recipients_refused", "Destinatário recusado pelo servidor SMTP", {"exception": name, "message": message}

        if isinstance(exc, smtplib.SMTPSenderRefused):
            return "smtp_sender_refused", "Remetente recusado pelo servidor SMTP", {"exception": name, "message": message}

        if isinstance(exc, smtplib.SMTPDataError):
            return "smtp_data_error", "Servidor recusou o conteúdo do e-mail", {"exception": name, "message": message}

        if isinstance(exc, socket.gaierror):
            return "dns_error", "Falha de DNS ao resolver servidor SMTP", {"exception": name, "message": message}

        if isinstance(exc, socket.timeout) or isinstance(exc, TimeoutError):
            return "timeout_error", "Timeout ao comunicar com servidor SMTP", {"exception": name, "message": message}

        if isinstance(exc, ConnectionRefusedError):
            return "connection_refused", "Conexão recusada pelo servidor SMTP", {"exception": name, "message": message}

        if isinstance(exc, ssl.SSLError):
            return "tls_ssl_error", "Falha TLS/SSL na conexão SMTP", {"exception": name, "message": message}

        return "unknown_email_error", "Erro desconhecido ao enviar e-mail", {"exception": name, "message": message}